from datetime import datetime, timezone
from uuid import UUID
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.core.security import (
    verify_password,
    hash_password,
    create_token_pair,
    decode_token,
    validate_token_type,
)
from app.models import User, Tenant, AuditLog, AuditAction
from app.schemas.auth import (
    Token,
    LoginRequest,
    RegisterRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
)
from app.schemas.user import UserResponse
from app.api.v1.deps import CurrentUser, DB, get_current_tenant


router = APIRouter()


@router.post("/login", response_model=Token)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: DB,
):
    """Authenticate user and return tokens."""
    # Find tenant
    tenant_query = select(Tenant).where(Tenant.is_active == True)
    if login_data.tenant_slug:
        tenant_query = tenant_query.where(Tenant.slug == login_data.tenant_slug)
    else:
        # Default tenant
        tenant_query = tenant_query.where(Tenant.slug == "default")

    result = await db.execute(tenant_query)
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant not found",
        )

    # Find user
    result = await db.execute(
        select(User).where(
            User.email == login_data.email,
            User.tenant_id == tenant.id,
            User.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(login_data.password, user.hashed_password):
        # Log failed attempt
        audit = AuditLog(
            tenant_id=tenant.id,
            action=AuditAction.LOGIN_FAILED,
            description=f"Failed login attempt for {login_data.email}",
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            success=False,
            error_message="Invalid credentials",
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
        )

    # Update last login (naive datetime for DB compatibility)
    user.last_login = datetime.utcnow()

    # Create tokens
    tokens = create_token_pair(user.id, user.tenant_id, user.role)

    # Log successful login
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=user.id,
        user_email=user.email,
        user_role=user.role,
        action=AuditAction.LOGIN,
        description=f"User logged in",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    db.add(audit)
    await db.commit()

    return tokens


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    request: Request,
    register_data: RegisterRequest,
    db: DB,
    tenant: Tenant = Depends(get_current_tenant),
):
    """Register a new user (requires tenant context)."""
    # Check if email already exists in tenant
    result = await db.execute(
        select(User).where(
            User.email == register_data.email,
            User.tenant_id == tenant.id,
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered in this organization",
        )

    # Create user
    user = User(
        tenant_id=tenant.id,
        email=register_data.email,
        hashed_password=hash_password(register_data.password),
        full_name=register_data.full_name,
        job_title=register_data.job_title,
        department=register_data.department,
        role="viewer",  # Default role
        is_active=True,
        is_verified=False,
    )
    db.add(user)

    # Log registration
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=user.id,
        user_email=user.email,
        action=AuditAction.USER_CREATE,
        resource_type="user",
        resource_id=user.id,
        description=f"New user registered: {user.email}",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    return user


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_data: RefreshTokenRequest,
    db: DB,
):
    """Refresh access token using refresh token."""
    payload = decode_token(refresh_data.refresh_token)

    if not payload or not validate_token_type(payload, "refresh"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )

    # Verify user still exists and is active
    result = await db.execute(
        select(User).where(
            User.id == UUID(payload.sub),
            User.is_active == True,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    # Create new tokens
    tokens = create_token_pair(user.id, user.tenant_id, user.role)

    # Log token refresh
    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        action=AuditAction.TOKEN_REFRESH,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return tokens


@router.post("/logout")
async def logout(
    request: Request,
    current_user: CurrentUser,
    db: DB,
):
    """Logout user (logs the event, token invalidation handled client-side)."""
    # Log logout
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.LOGOUT,
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return {"message": "Logged out successfully"}


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: CurrentUser,
):
    """Get current user information."""
    return current_user


@router.post("/change-password")
async def change_password(
    request: Request,
    password_data: PasswordChangeRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Change current user's password."""
    if not verify_password(password_data.current_password, current_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect",
        )

    current_user.hashed_password = hash_password(password_data.new_password)

    # Log password change
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action=AuditAction.PASSWORD_CHANGE,
        resource_type="user",
        resource_id=current_user.id,
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return {"message": "Password changed successfully"}
