from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from sqlalchemy import String, Text, ForeignKey, DateTime, Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, INET

from app.core.database import Base
from app.models.base import TenantMixin


class AuditAction(str, Enum):
    """Types of auditable actions."""
    # Auth
    LOGIN = "login"
    LOGOUT = "logout"
    LOGIN_FAILED = "login_failed"
    PASSWORD_CHANGE = "password_change"
    TOKEN_REFRESH = "token_refresh"

    # CRUD
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    BULK_CREATE = "bulk_create"
    BULK_UPDATE = "bulk_update"
    BULK_DELETE = "bulk_delete"

    # Entity operations
    ENTITY_SCREEN = "entity_screen"
    ENTITY_IMPORT = "entity_import"
    ENTITY_EXPORT = "entity_export"

    # Match operations
    MATCH_CONFIRM = "match_confirm"
    MATCH_DISMISS = "match_dismiss"
    MATCH_ESCALATE = "match_escalate"

    # Risk operations
    RISK_CALCULATE = "risk_calculate"
    RISK_OVERRIDE = "risk_override"

    # Scenario operations
    SCENARIO_RUN = "scenario_run"
    SCENARIO_ARCHIVE = "scenario_archive"

    # Admin operations
    TENANT_CREATE = "tenant_create"
    TENANT_UPDATE = "tenant_update"
    USER_CREATE = "user_create"
    USER_UPDATE = "user_update"
    USER_DEACTIVATE = "user_deactivate"
    ROLE_CHANGE = "role_change"

    # System operations
    SANCTIONS_SYNC = "sanctions_sync"
    SETTINGS_UPDATE = "settings_update"
    EXPORT_AUDIT = "export_audit"


class AuditLog(Base, TenantMixin):
    """Immutable audit log for all actions in the system."""

    __tablename__ = "audit_log"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # When
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # Who
    user_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    user_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    user_role: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # What
    action: Mapped[AuditAction] = mapped_column(
        SQLEnum(AuditAction), nullable=False, index=True
    )
    resource_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True, index=True)
    resource_id: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True), nullable=True
    )
    resource_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # State changes
    before_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    after_state: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    changes: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Context
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    context_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Request info
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    request_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Result
    success: Mapped[bool] = mapped_column(default=True, nullable=False)
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    user = relationship("User", foreign_keys=[user_id])

    def __repr__(self) -> str:
        return f"<AuditLog {self.action.value} by {self.user_email} at {self.created_at}>"

    # Note: This table is append-only. No updates or deletes should ever be performed.
