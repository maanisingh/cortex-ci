"""
Role-Based Access Control (RBAC) Service
Fine-grained permissions for GRC platform.

Features:
- Predefined roles (Admin, DPO, Auditor, etc.)
- Custom roles
- Permission inheritance
- Resource-level access control
- Audit logging of access decisions
"""

from typing import Optional, List, Dict, Set, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class Permission(str, Enum):
    # System
    ADMIN_FULL = "admin:*"
    SYSTEM_SETTINGS = "system:settings"

    # Users
    USERS_VIEW = "users:view"
    USERS_CREATE = "users:create"
    USERS_UPDATE = "users:update"
    USERS_DELETE = "users:delete"
    USERS_MANAGE_ROLES = "users:manage_roles"

    # Companies
    COMPANIES_VIEW = "companies:view"
    COMPANIES_CREATE = "companies:create"
    COMPANIES_UPDATE = "companies:update"
    COMPANIES_DELETE = "companies:delete"

    # Documents
    DOCUMENTS_VIEW = "documents:view"
    DOCUMENTS_CREATE = "documents:create"
    DOCUMENTS_UPDATE = "documents:update"
    DOCUMENTS_DELETE = "documents:delete"
    DOCUMENTS_APPROVE = "documents:approve"
    DOCUMENTS_EXPORT = "documents:export"

    # Tasks
    TASKS_VIEW = "tasks:view"
    TASKS_CREATE = "tasks:create"
    TASKS_UPDATE = "tasks:update"
    TASKS_DELETE = "tasks:delete"
    TASKS_ASSIGN = "tasks:assign"
    TASKS_COMPLETE = "tasks:complete"

    # Compliance
    COMPLIANCE_VIEW = "compliance:view"
    COMPLIANCE_GAP_ANALYSIS = "compliance:gap_analysis"
    COMPLIANCE_CONTROL_MAPPING = "compliance:control_mapping"
    COMPLIANCE_EVIDENCE = "compliance:evidence"

    # Audit
    AUDIT_VIEW = "audit:view"
    AUDIT_CREATE = "audit:create"
    AUDIT_CONDUCT = "audit:conduct"
    AUDIT_REPORT = "audit:report"

    # Reports
    REPORTS_VIEW = "reports:view"
    REPORTS_CREATE = "reports:create"
    REPORTS_EXPORT = "reports:export"

    # Incidents
    INCIDENTS_VIEW = "incidents:view"
    INCIDENTS_CREATE = "incidents:create"
    INCIDENTS_MANAGE = "incidents:manage"

    # Training
    TRAINING_VIEW = "training:view"
    TRAINING_MANAGE = "training:manage"

    # Logs
    LOGS_VIEW = "logs:view"
    LOGS_EXPORT = "logs:export"


class Role(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    name: str
    name_ru: str
    description: str
    description_ru: str
    permissions: Set[Permission]
    is_system: bool = False  # System roles can't be deleted
    parent_role_id: Optional[UUID] = None  # For permission inheritance
    created_at: datetime = Field(default_factory=datetime.utcnow)


class UserRole(BaseModel):
    user_id: str
    role_id: UUID
    company_id: Optional[UUID] = None  # None means all companies
    granted_at: datetime = Field(default_factory=datetime.utcnow)
    granted_by: Optional[str] = None
    expires_at: Optional[datetime] = None


# Predefined System Roles
SYSTEM_ROLES: Dict[str, Role] = {
    "admin": Role(
        id=UUID("00000000-0000-0000-0000-000000000001"),
        name="Administrator",
        name_ru="Администратор",
        description="Full system access",
        description_ru="Полный доступ к системе",
        permissions={Permission.ADMIN_FULL},
        is_system=True
    ),
    "dpo": Role(
        id=UUID("00000000-0000-0000-0000-000000000002"),
        name="Data Protection Officer",
        name_ru="Ответственный за обработку ПДн",
        description="Manages personal data protection compliance",
        description_ru="Управляет соответствием требованиям защиты ПДн",
        permissions={
            Permission.DOCUMENTS_VIEW, Permission.DOCUMENTS_CREATE,
            Permission.DOCUMENTS_UPDATE, Permission.DOCUMENTS_APPROVE,
            Permission.COMPLIANCE_VIEW, Permission.COMPLIANCE_GAP_ANALYSIS,
            Permission.COMPLIANCE_CONTROL_MAPPING, Permission.COMPLIANCE_EVIDENCE,
            Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_ASSIGN,
            Permission.REPORTS_VIEW, Permission.REPORTS_CREATE, Permission.REPORTS_EXPORT,
            Permission.TRAINING_VIEW, Permission.TRAINING_MANAGE,
            Permission.LOGS_VIEW
        },
        is_system=True
    ),
    "security_admin": Role(
        id=UUID("00000000-0000-0000-0000-000000000003"),
        name="Security Administrator",
        name_ru="Администратор ИБ",
        description="Manages information security",
        description_ru="Управляет информационной безопасностью",
        permissions={
            Permission.DOCUMENTS_VIEW, Permission.DOCUMENTS_CREATE,
            Permission.COMPLIANCE_VIEW, Permission.COMPLIANCE_GAP_ANALYSIS,
            Permission.INCIDENTS_VIEW, Permission.INCIDENTS_CREATE, Permission.INCIDENTS_MANAGE,
            Permission.AUDIT_VIEW, Permission.AUDIT_CREATE, Permission.AUDIT_CONDUCT,
            Permission.LOGS_VIEW, Permission.LOGS_EXPORT,
            Permission.REPORTS_VIEW, Permission.REPORTS_CREATE
        },
        is_system=True
    ),
    "auditor": Role(
        id=UUID("00000000-0000-0000-0000-000000000004"),
        name="Auditor",
        name_ru="Аудитор",
        description="Conducts internal and external audits",
        description_ru="Проводит внутренние и внешние аудиты",
        permissions={
            Permission.DOCUMENTS_VIEW, Permission.DOCUMENTS_EXPORT,
            Permission.COMPLIANCE_VIEW,
            Permission.AUDIT_VIEW, Permission.AUDIT_CONDUCT, Permission.AUDIT_REPORT,
            Permission.REPORTS_VIEW, Permission.REPORTS_EXPORT,
            Permission.LOGS_VIEW
        },
        is_system=True
    ),
    "manager": Role(
        id=UUID("00000000-0000-0000-0000-000000000005"),
        name="Department Manager",
        name_ru="Руководитель подразделения",
        description="Manages department compliance tasks",
        description_ru="Управляет задачами по соответствию подразделения",
        permissions={
            Permission.DOCUMENTS_VIEW, Permission.DOCUMENTS_CREATE,
            Permission.TASKS_VIEW, Permission.TASKS_CREATE, Permission.TASKS_UPDATE,
            Permission.TASKS_ASSIGN, Permission.TASKS_COMPLETE,
            Permission.COMPLIANCE_VIEW, Permission.COMPLIANCE_EVIDENCE,
            Permission.REPORTS_VIEW
        },
        is_system=True
    ),
    "employee": Role(
        id=UUID("00000000-0000-0000-0000-000000000006"),
        name="Employee",
        name_ru="Сотрудник",
        description="Basic access to assigned tasks",
        description_ru="Базовый доступ к назначенным задачам",
        permissions={
            Permission.DOCUMENTS_VIEW,
            Permission.TASKS_VIEW, Permission.TASKS_COMPLETE,
            Permission.TRAINING_VIEW
        },
        is_system=True
    ),
    "viewer": Role(
        id=UUID("00000000-0000-0000-0000-000000000007"),
        name="Read-Only Viewer",
        name_ru="Только просмотр",
        description="Read-only access",
        description_ru="Доступ только для чтения",
        permissions={
            Permission.DOCUMENTS_VIEW,
            Permission.TASKS_VIEW,
            Permission.COMPLIANCE_VIEW,
            Permission.REPORTS_VIEW
        },
        is_system=True
    )
}


class RBACService:
    """
    Role-Based Access Control service.
    """

    def __init__(self):
        self.roles: Dict[UUID, Role] = {r.id: r for r in SYSTEM_ROLES.values()}
        self.user_roles: Dict[str, List[UserRole]] = {}

    # ==========================================================================
    # Role Management
    # ==========================================================================

    async def create_role(
        self,
        name: str,
        name_ru: str,
        description: str,
        description_ru: str,
        permissions: List[str],
        parent_role_id: Optional[UUID] = None
    ) -> Role:
        """Create a custom role."""
        role = Role(
            name=name,
            name_ru=name_ru,
            description=description,
            description_ru=description_ru,
            permissions={Permission(p) for p in permissions},
            parent_role_id=parent_role_id,
            is_system=False
        )
        self.roles[role.id] = role
        return role

    async def get_role(self, role_id: UUID) -> Optional[Role]:
        """Get role by ID."""
        return self.roles.get(role_id)

    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        for role in self.roles.values():
            if role.name.lower() == name.lower():
                return role
        return None

    async def list_roles(self, include_system: bool = True) -> List[Role]:
        """List all roles."""
        roles = list(self.roles.values())
        if not include_system:
            roles = [r for r in roles if not r.is_system]
        return roles

    async def update_role(
        self,
        role_id: UUID,
        data: Dict[str, Any]
    ) -> Optional[Role]:
        """Update a custom role (system roles cannot be updated)."""
        role = self.roles.get(role_id)
        if role and not role.is_system:
            if "permissions" in data:
                data["permissions"] = {Permission(p) for p in data["permissions"]}
            for key, value in data.items():
                if hasattr(role, key):
                    setattr(role, key, value)
            self.roles[role_id] = role
            return role
        return None

    async def delete_role(self, role_id: UUID) -> bool:
        """Delete a custom role (system roles cannot be deleted)."""
        role = self.roles.get(role_id)
        if role and not role.is_system:
            del self.roles[role_id]
            return True
        return False

    # ==========================================================================
    # User Role Assignment
    # ==========================================================================

    async def assign_role(
        self,
        user_id: str,
        role_id: UUID,
        company_id: Optional[UUID] = None,
        granted_by: Optional[str] = None,
        expires_at: Optional[datetime] = None
    ) -> UserRole:
        """Assign a role to a user."""
        user_role = UserRole(
            user_id=user_id,
            role_id=role_id,
            company_id=company_id,
            granted_by=granted_by,
            expires_at=expires_at
        )

        if user_id not in self.user_roles:
            self.user_roles[user_id] = []

        # Remove duplicate assignment
        self.user_roles[user_id] = [
            ur for ur in self.user_roles[user_id]
            if not (ur.role_id == role_id and ur.company_id == company_id)
        ]
        self.user_roles[user_id].append(user_role)

        return user_role

    async def revoke_role(
        self,
        user_id: str,
        role_id: UUID,
        company_id: Optional[UUID] = None
    ) -> bool:
        """Revoke a role from a user."""
        if user_id in self.user_roles:
            original_len = len(self.user_roles[user_id])
            self.user_roles[user_id] = [
                ur for ur in self.user_roles[user_id]
                if not (ur.role_id == role_id and ur.company_id == company_id)
            ]
            return len(self.user_roles[user_id]) < original_len
        return False

    async def get_user_roles(
        self,
        user_id: str,
        company_id: Optional[UUID] = None
    ) -> List[UserRole]:
        """Get all roles for a user."""
        roles = self.user_roles.get(user_id, [])

        # Filter by company if specified
        if company_id:
            roles = [
                r for r in roles
                if r.company_id is None or r.company_id == company_id
            ]

        # Filter expired roles
        now = datetime.utcnow()
        roles = [r for r in roles if r.expires_at is None or r.expires_at > now]

        return roles

    # ==========================================================================
    # Permission Checking
    # ==========================================================================

    async def get_user_permissions(
        self,
        user_id: str,
        company_id: Optional[UUID] = None
    ) -> Set[Permission]:
        """Get all permissions for a user."""
        permissions: Set[Permission] = set()

        user_roles = await self.get_user_roles(user_id, company_id)

        for user_role in user_roles:
            role = self.roles.get(user_role.role_id)
            if role:
                permissions.update(role.permissions)

                # Add inherited permissions from parent role
                if role.parent_role_id:
                    parent = self.roles.get(role.parent_role_id)
                    if parent:
                        permissions.update(parent.permissions)

        return permissions

    async def check_permission(
        self,
        user_id: str,
        permission: Permission,
        company_id: Optional[UUID] = None
    ) -> bool:
        """Check if user has a specific permission."""
        permissions = await self.get_user_permissions(user_id, company_id)

        # Admin has all permissions
        if Permission.ADMIN_FULL in permissions:
            return True

        # Check for wildcard permission (e.g., documents:* matches documents:view)
        perm_parts = permission.value.split(":")
        if len(perm_parts) == 2:
            wildcard = f"{perm_parts[0]}:*"
            if Permission(wildcard) in permissions:
                return True

        return permission in permissions

    async def check_permissions(
        self,
        user_id: str,
        permissions: List[Permission],
        company_id: Optional[UUID] = None,
        require_all: bool = True
    ) -> bool:
        """Check if user has multiple permissions."""
        results = [
            await self.check_permission(user_id, p, company_id)
            for p in permissions
        ]

        if require_all:
            return all(results)
        return any(results)

    # ==========================================================================
    # Access Control Matrix
    # ==========================================================================

    async def get_access_matrix(
        self,
        user_id: str,
        company_id: Optional[UUID] = None
    ) -> Dict[str, Dict[str, bool]]:
        """Get access control matrix for a user."""
        permissions = await self.get_user_permissions(user_id, company_id)

        # Group by resource
        resources = {}
        for perm in Permission:
            parts = perm.value.split(":")
            if len(parts) == 2:
                resource, action = parts
                if resource not in resources:
                    resources[resource] = {}
                resources[resource][action] = perm in permissions or Permission.ADMIN_FULL in permissions

        return resources


# Singleton instance
rbac_service = RBACService()


# FastAPI Router with Permission Decorator
from fastapi import APIRouter, HTTPException, Depends, Request
from functools import wraps

router = APIRouter()


def require_permission(permission: Permission):
    """Decorator to require a specific permission."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Get user from request (in production, from JWT/session)
            request = kwargs.get("request") or args[0]
            user_id = getattr(request.state, "user_id", "demo-user")
            company_id = getattr(request.state, "company_id", None)

            has_perm = await rbac_service.check_permission(
                user_id, permission, company_id
            )

            if not has_perm:
                raise HTTPException(
                    status_code=403,
                    detail=f"Permission denied: {permission.value}"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator


@router.get("/roles")
async def list_roles(include_system: bool = True):
    """List all roles."""
    roles = await rbac_service.list_roles(include_system)
    return {"roles": [r.model_dump() for r in roles]}


@router.get("/roles/{role_id}")
async def get_role(role_id: str):
    """Get role by ID."""
    role = await rbac_service.get_role(UUID(role_id))
    if role:
        return role.model_dump()
    raise HTTPException(status_code=404, detail="Role not found")


@router.post("/roles")
async def create_role(data: Dict[str, Any]):
    """Create a custom role."""
    role = await rbac_service.create_role(**data)
    return role.model_dump()


@router.post("/users/{user_id}/roles")
async def assign_role(
    user_id: str,
    role_id: str,
    company_id: Optional[str] = None
):
    """Assign role to user."""
    company_uuid = UUID(company_id) if company_id else None
    user_role = await rbac_service.assign_role(
        user_id, UUID(role_id), company_uuid
    )
    return user_role.model_dump()


@router.delete("/users/{user_id}/roles/{role_id}")
async def revoke_role(
    user_id: str,
    role_id: str,
    company_id: Optional[str] = None
):
    """Revoke role from user."""
    company_uuid = UUID(company_id) if company_id else None
    success = await rbac_service.revoke_role(user_id, UUID(role_id), company_uuid)
    if success:
        return {"status": "revoked"}
    raise HTTPException(status_code=404, detail="Role assignment not found")


@router.get("/users/{user_id}/roles")
async def get_user_roles(user_id: str, company_id: Optional[str] = None):
    """Get user's roles."""
    company_uuid = UUID(company_id) if company_id else None
    roles = await rbac_service.get_user_roles(user_id, company_uuid)
    return {"roles": [r.model_dump() for r in roles]}


@router.get("/users/{user_id}/permissions")
async def get_user_permissions(user_id: str, company_id: Optional[str] = None):
    """Get user's permissions."""
    company_uuid = UUID(company_id) if company_id else None
    permissions = await rbac_service.get_user_permissions(user_id, company_uuid)
    return {"permissions": [p.value for p in permissions]}


@router.get("/users/{user_id}/access-matrix")
async def get_access_matrix(user_id: str, company_id: Optional[str] = None):
    """Get user's access control matrix."""
    company_uuid = UUID(company_id) if company_id else None
    matrix = await rbac_service.get_access_matrix(user_id, company_uuid)
    return matrix


@router.post("/check-permission")
async def check_permission(
    user_id: str,
    permission: str,
    company_id: Optional[str] = None
):
    """Check if user has permission."""
    company_uuid = UUID(company_id) if company_id else None
    has_perm = await rbac_service.check_permission(
        user_id, Permission(permission), company_uuid
    )
    return {"has_permission": has_perm}
