from typing import Annotated
from uuid import UUID

from fastapi import Depends, Header, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import Role, TokenPayload, decode_token, validate_token_type
from app.models import Tenant, User

security = HTTPBearer()


async def get_current_tenant(
    request: Request,
    db: AsyncSession = Depends(get_db),
    x_tenant_id: str | None = Header(None),
    credentials: HTTPAuthorizationCredentials | None = Depends(HTTPBearer(auto_error=False)),
) -> Tenant:
    """Get current tenant from header, token, or subdomain."""
    tenant_id = x_tenant_id

    # Try to get from JWT token if no header provided
    if not tenant_id and credentials:
        token = credentials.credentials
        payload = decode_token(token)
        if payload and payload.tenant_id:
            tenant_id = payload.tenant_id

    if not tenant_id:
        # Try to get from subdomain
        host = request.headers.get("host", "")
        if "." in host:
            tenant_slug = host.split(".")[0]
            result = await db.execute(
                select(Tenant).where(Tenant.slug == tenant_slug, Tenant.is_active)
            )
            tenant = result.scalar_one_or_none()
            if tenant:
                return tenant

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Tenant ID required. Provide X-Tenant-ID header.",
        )

    try:
        tenant_uuid = UUID(tenant_id)
    except ValueError:
        # Maybe it's a slug
        result = await db.execute(select(Tenant).where(Tenant.slug == tenant_id, Tenant.is_active))
        tenant = result.scalar_one_or_none()
        if tenant:
            return tenant
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid tenant ID format",
        )

    result = await db.execute(select(Tenant).where(Tenant.id == tenant_uuid, Tenant.is_active))
    tenant = result.scalar_one_or_none()

    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found or inactive",
        )

    return tenant


async def get_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(security),
) -> TokenPayload:
    """Extract and validate token payload."""
    token = credentials.credentials
    payload = decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not validate_token_type(payload, "access"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return payload


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: TokenPayload = Depends(get_token_payload),
) -> User:
    """Get current authenticated user."""
    result = await db.execute(select(User).where(User.id == UUID(token.sub), User.is_active))
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive",
        )

    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Ensure user is active."""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated",
        )
    return current_user


def require_roles(*roles: str):
    """Dependency factory for role-based access control."""

    async def role_checker(
        current_user: User = Depends(get_current_active_user),
    ) -> User:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Insufficient permissions. Required roles: {', '.join(roles)}",
            )
        return current_user

    return role_checker


async def get_current_tenant_id(
    tenant: Tenant = Depends(get_current_tenant),
) -> UUID:
    """Get current tenant ID."""
    return tenant.id


# Convenience dependencies
RequireAdmin = Annotated[User, Depends(require_roles(Role.ADMIN))]
RequireWriter = Annotated[User, Depends(require_roles(Role.ADMIN, Role.ANALYST))]
RequireApprover = Annotated[User, Depends(require_roles(Role.ADMIN, Role.APPROVER))]
RequireViewer = Annotated[
    User, Depends(require_roles(Role.ADMIN, Role.ANALYST, Role.APPROVER, Role.VIEWER))
]

CurrentUser = Annotated[User, Depends(get_current_active_user)]
CurrentTenant = Annotated[Tenant, Depends(get_current_tenant)]
DB = Annotated[AsyncSession, Depends(get_db)]
