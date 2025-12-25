from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy import select

from app.core.security import (
    verify_password,
    hash_password,
    create_token_pair,
    decode_token,
    validate_token_type,
)
from app.core.mfa import (
    MFAManager,
    generate_mfa_token,
    verify_mfa_token,
    verify_totp,
)
from app.core.config import settings
from app.models import User, Tenant, AuditLog, AuditAction
from app.schemas.auth import (
    Token,
    LoginRequest,
    LoginResponse,
    RegisterRequest,
    PasswordChangeRequest,
    RefreshTokenRequest,
    MFASetupResponse,
    MFAVerifyRequest,
    MFAVerifyResponse,
    MFALoginVerifyRequest,
    MFABackupCodeRequest,
    MFADisableRequest,
    MFAStatusResponse,
)
from app.schemas.user import UserResponse
from app.api.v1.deps import CurrentUser, DB, get_current_tenant


router = APIRouter()

# Store pending MFA setups (in production, use Redis)
_pending_mfa_setups: dict = {}


@router.post("/login", response_model=LoginResponse)
async def login(
    request: Request,
    login_data: LoginRequest,
    db: DB,
):
    """Authenticate user and return tokens (may require MFA)."""
    # Find tenant
    tenant_query = select(Tenant).where(Tenant.is_active)
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
            User.is_active,
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

    # Check if MFA is enabled for this user
    if user.mfa_enabled and settings.MFA_ENABLED:
        # If MFA code provided, verify it
        if login_data.mfa_code:
            if not await MFAManager.verify_mfa(user, login_data.mfa_code):
                audit = AuditLog(
                    tenant_id=tenant.id,
                    user_id=user.id,
                    action=AuditAction.LOGIN_FAILED,
                    description="Invalid MFA code",
                    ip_address=request.client.host if request.client else None,
                    success=False,
                    error_message="Invalid MFA code",
                )
                db.add(audit)
                await db.commit()

                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid MFA code",
                )
        else:
            # MFA required but no code provided - return MFA token
            mfa_token = generate_mfa_token(str(user.id))

            audit = AuditLog(
                tenant_id=tenant.id,
                user_id=user.id,
                action=AuditAction.MFA_REQUIRED,
                description="MFA verification required",
                ip_address=request.client.host if request.client else None,
                success=True,
            )
            db.add(audit)
            await db.commit()

            return LoginResponse(
                mfa_required=True,
                mfa_token=mfa_token,
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
        description="User logged in",
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
        success=True,
    )
    db.add(audit)
    await db.commit()

    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
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
            User.is_active,
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
    if not verify_password(
        password_data.current_password, current_user.hashed_password
    ):
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


# ============================================
# MFA/TOTP Endpoints (Phase 3 Security)
# ============================================


@router.post("/mfa/verify-login", response_model=LoginResponse)
async def verify_mfa_login(
    request: Request,
    mfa_data: MFALoginVerifyRequest,
    db: DB,
):
    """Complete MFA verification during login."""
    # Verify MFA token
    user_id = verify_mfa_token(mfa_data.mfa_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA session",
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == UUID(user_id), User.is_active)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Verify TOTP code
    if not await MFAManager.verify_mfa(user, mfa_data.code):
        audit = AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action=AuditAction.MFA_FAILED,
            description="Invalid MFA code during login",
            ip_address=request.client.host if request.client else None,
            success=False,
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid MFA code",
        )

    # MFA verified - create tokens
    user.last_login = datetime.utcnow()
    tokens = create_token_pair(user.id, user.tenant_id, user.role)

    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        action=AuditAction.MFA_VERIFIED,
        description="MFA verification successful",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.post("/mfa/backup-code", response_model=LoginResponse)
async def use_backup_code(
    request: Request,
    backup_data: MFABackupCodeRequest,
    db: DB,
):
    """Use a backup code for MFA verification during login."""
    # Verify MFA token
    user_id = verify_mfa_token(backup_data.mfa_token)
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired MFA session",
        )

    # Get user
    result = await db.execute(
        select(User).where(User.id == UUID(user_id), User.is_active)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    # Verify backup code
    if not await MFAManager.use_backup_code(user, backup_data.backup_code):
        audit = AuditLog(
            tenant_id=user.tenant_id,
            user_id=user.id,
            action=AuditAction.MFA_FAILED,
            description="Invalid backup code",
            ip_address=request.client.host if request.client else None,
            success=False,
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid backup code",
        )

    # Backup code verified - create tokens
    user.last_login = datetime.utcnow()
    tokens = create_token_pair(user.id, user.tenant_id, user.role)

    audit = AuditLog(
        tenant_id=user.tenant_id,
        user_id=user.id,
        user_email=user.email,
        action=AuditAction.MFA_BACKUP_USED,
        description="Backup code used for login",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return LoginResponse(
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )


@router.get("/mfa/status", response_model=MFAStatusResponse)
async def get_mfa_status(
    current_user: CurrentUser,
):
    """Get current user's MFA status."""
    backup_count = 0
    if current_user.mfa_backup_codes:
        backup_count = len([c for c in current_user.mfa_backup_codes if c])

    return MFAStatusResponse(
        mfa_enabled=current_user.mfa_enabled,
        mfa_verified_at=current_user.mfa_verified_at,
        backup_codes_remaining=backup_count,
    )


@router.post("/mfa/setup", response_model=MFASetupResponse)
async def setup_mfa(
    request: Request,
    current_user: CurrentUser,
    db: DB,
):
    """Initialize MFA setup for current user."""
    if current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is already enabled. Disable it first to set up again.",
        )

    # Generate MFA setup data
    setup_data = await MFAManager.setup_mfa(current_user)

    # Store pending setup (in production, use Redis with expiration)
    _pending_mfa_setups[str(current_user.id)] = {
        "secret": setup_data["secret"],
        "hashed_backup_codes": setup_data["hashed_backup_codes"],
    }

    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action=AuditAction.MFA_SETUP_STARTED,
        description="MFA setup initiated",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return MFASetupResponse(
        secret=setup_data["secret"],
        provisioning_uri=setup_data["provisioning_uri"],
        backup_codes=setup_data["backup_codes"],
    )


@router.post("/mfa/enable", response_model=MFAVerifyResponse)
async def enable_mfa(
    request: Request,
    verify_data: MFAVerifyRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Enable MFA after verifying the TOTP code."""
    user_id = str(current_user.id)

    if user_id not in _pending_mfa_setups:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No pending MFA setup. Please call /mfa/setup first.",
        )

    pending = _pending_mfa_setups[user_id]

    # Verify the code
    if not verify_totp(pending["secret"], verify_data.code):
        audit = AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=AuditAction.MFA_SETUP_FAILED,
            description="Invalid verification code during MFA setup",
            ip_address=request.client.host if request.client else None,
            success=False,
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid verification code. Please try again.",
        )

    # Enable MFA
    current_user.mfa_enabled = True
    current_user.mfa_secret = pending["secret"]
    current_user.mfa_backup_codes = pending["hashed_backup_codes"]
    current_user.mfa_verified_at = datetime.utcnow()

    # Clean up pending setup
    del _pending_mfa_setups[user_id]

    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action=AuditAction.MFA_ENABLED,
        description="MFA enabled successfully",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return MFAVerifyResponse(
        verified=True,
        message="MFA has been enabled successfully.",
    )


@router.post("/mfa/disable", response_model=MFAVerifyResponse)
async def disable_mfa(
    request: Request,
    disable_data: MFADisableRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Disable MFA for current user."""
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled.",
        )

    # Verify password and MFA code
    if not await MFAManager.disable_mfa(
        current_user, disable_data.password, disable_data.code
    ):
        audit = AuditLog(
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            action=AuditAction.MFA_DISABLE_FAILED,
            description="Failed to disable MFA - invalid credentials",
            ip_address=request.client.host if request.client else None,
            success=False,
        )
        db.add(audit)
        await db.commit()

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid password or MFA code.",
        )

    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action=AuditAction.MFA_DISABLED,
        description="MFA disabled",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return MFAVerifyResponse(
        verified=True,
        message="MFA has been disabled.",
    )


@router.post("/mfa/regenerate-backup-codes")
async def regenerate_backup_codes(
    request: Request,
    verify_data: MFAVerifyRequest,
    current_user: CurrentUser,
    db: DB,
):
    """Regenerate backup codes (requires current MFA code)."""
    if not current_user.mfa_enabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="MFA is not enabled.",
        )

    # Verify current MFA code
    if not await MFAManager.verify_mfa(current_user, verify_data.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid MFA code.",
        )

    # Regenerate codes
    new_codes = MFAManager.regenerate_backup_codes(current_user)

    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        action=AuditAction.MFA_BACKUP_REGENERATED,
        description="Backup codes regenerated",
        ip_address=request.client.host if request.client else None,
        success=True,
    )
    db.add(audit)
    await db.commit()

    return {"backup_codes": new_codes}
