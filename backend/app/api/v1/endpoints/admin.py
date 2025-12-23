from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func

from app.models import Tenant, User, AuditLog, AuditAction
from app.schemas.tenant import TenantCreate, TenantUpdate, TenantResponse
from app.schemas.user import UserCreate, UserUpdate, UserResponse, UserListResponse
from app.core.security import hash_password, Role
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireAdmin


router = APIRouter()


# Tenant Management

@router.get("/tenants", response_model=List[TenantResponse])
async def list_tenants(
    db: DB,
    current_user: RequireAdmin,
    include_inactive: bool = False,
):
    """List all tenants (super admin only)."""
    query = select(Tenant)
    if not include_inactive:
        query = query.where(Tenant.is_active == True)

    result = await db.execute(query.order_by(Tenant.created_at.desc()))
    tenants = result.scalars().all()

    return tenants


@router.post("/tenants", response_model=TenantResponse, status_code=status.HTTP_201_CREATED)
async def create_tenant(
    tenant_data: TenantCreate,
    db: DB,
    current_user: RequireAdmin,
):
    """Create a new tenant."""
    # Check if slug already exists
    result = await db.execute(
        select(Tenant).where(Tenant.slug == tenant_data.slug)
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant slug already exists",
        )

    tenant = Tenant(**tenant_data.model_dump())
    db.add(tenant)

    # Audit log (using current user's tenant)
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.TENANT_CREATE,
        resource_type="tenant",
        resource_id=tenant.id,
        resource_name=tenant.name,
        after_state=tenant_data.model_dump(mode="json"),
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(tenant)

    return tenant


@router.get("/tenants/{tenant_id}", response_model=TenantResponse)
async def get_tenant(
    tenant_id: UUID,
    db: DB,
    current_user: RequireAdmin,
):
    """Get a specific tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    return tenant


@router.put("/tenants/{tenant_id}", response_model=TenantResponse)
async def update_tenant(
    tenant_id: UUID,
    tenant_data: TenantUpdate,
    db: DB,
    current_user: RequireAdmin,
):
    """Update a tenant."""
    result = await db.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found",
        )

    before_state = {"name": tenant.name, "is_active": tenant.is_active}

    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)

    # Audit log
    audit = AuditLog(
        tenant_id=current_user.tenant_id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.TENANT_UPDATE,
        resource_type="tenant",
        resource_id=tenant.id,
        resource_name=tenant.name,
        before_state=before_state,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(tenant)

    return tenant


# User Management

@router.get("/users", response_model=UserListResponse)
async def list_users(
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    role: Optional[str] = None,
    is_active: bool = True,
):
    """List users in the current tenant."""
    query = select(User).where(
        User.tenant_id == tenant.id,
        User.is_active == is_active,
    )

    if role:
        query = query.where(User.role == role)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(User.created_at.desc())

    result = await db.execute(query)
    users = result.scalars().all()

    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.post("/users", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Create a new user in the current tenant."""
    # Check if email already exists in tenant
    result = await db.execute(
        select(User).where(
            User.email == user_data.email,
            User.tenant_id == tenant.id,
        )
    )
    if result.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists in this organization",
        )

    # Validate role
    if user_data.role not in Role.all():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(Role.all())}",
        )

    user = User(
        tenant_id=tenant.id,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        full_name=user_data.full_name,
        job_title=user_data.job_title,
        department=user_data.department,
        role=user_data.role,
        is_active=True,
        is_verified=False,
    )
    db.add(user)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.USER_CREATE,
        resource_type="user",
        resource_id=user.id,
        resource_name=user.email,
        after_state={"email": user.email, "role": user.role},
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    return user


@router.get("/users/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Get a specific user."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant.id,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user


@router.put("/users/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: UUID,
    user_data: UserUpdate,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Update a user."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant.id,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    before_state = {"role": user.role, "is_active": user.is_active}

    # Validate role if being changed
    if user_data.role and user_data.role not in Role.all():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role. Must be one of: {', '.join(Role.all())}",
        )

    update_data = user_data.model_dump(exclude_unset=True)

    # Track if role changed
    role_changed = "role" in update_data and update_data["role"] != user.role

    for field, value in update_data.items():
        setattr(user, field, value)

    # Audit log
    action = AuditAction.ROLE_CHANGE if role_changed else AuditAction.USER_UPDATE
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=action,
        resource_type="user",
        resource_id=user.id,
        resource_name=user.email,
        before_state=before_state,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(user)

    return user


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Deactivate a user (soft delete)."""
    result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant.id,
        )
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Prevent self-deactivation
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot deactivate your own account",
        )

    user.is_active = False

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.USER_DEACTIVATE,
        resource_type="user",
        resource_id=user.id,
        resource_name=user.email,
        success=True,
    )
    db.add(audit)
    await db.commit()


# System Settings

@router.get("/settings")
async def get_tenant_settings(
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Get current tenant settings."""
    return {
        "tenant_id": str(tenant.id),
        "tenant_name": tenant.name,
        "settings": tenant.settings,
        "risk_weights": tenant.risk_weights,
    }


@router.put("/settings")
async def update_tenant_settings(
    settings: dict,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Update tenant settings."""
    before_state = {"settings": tenant.settings}

    tenant.settings = {**tenant.settings, **settings}

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.SETTINGS_UPDATE,
        resource_type="tenant",
        resource_id=tenant.id,
        before_state=before_state,
        after_state={"settings": settings},
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(tenant)

    return {"settings": tenant.settings}


@router.put("/settings/risk-weights")
async def update_risk_weights(
    weights: dict,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Update risk calculation weights."""
    # Validate weights sum to 1.0 (or close to it)
    total = sum(weights.values())
    if not (0.99 <= total <= 1.01):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Risk weights must sum to 1.0, got {total}",
        )

    before_state = {"risk_weights": tenant.risk_weights}

    tenant.risk_weights = weights

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.SETTINGS_UPDATE,
        resource_type="tenant",
        resource_id=tenant.id,
        before_state=before_state,
        after_state={"risk_weights": weights},
        description="Risk weights updated",
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(tenant)

    return {"risk_weights": tenant.risk_weights}
