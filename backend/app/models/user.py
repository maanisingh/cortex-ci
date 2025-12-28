from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import Boolean, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.core.security import Role
from app.models.base import TenantMixin, TimestampMixin


class User(Base, TimestampMixin, TenantMixin):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[str | None] = mapped_column(String(255), nullable=True)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Role-based access control
    role: Mapped[str] = mapped_column(String(50), nullable=False, default=Role.VIEWER)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # MFA/TOTP (Phase 3 Security)
    mfa_enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    mfa_secret: Mapped[str | None] = mapped_column(String(255), nullable=True)
    mfa_backup_codes: Mapped[list[str] | None] = mapped_column(ARRAY(String(20)), nullable=True)
    mfa_verified_at: Mapped[datetime | None] = mapped_column(nullable=True)

    # Metadata
    last_login: Mapped[datetime | None] = mapped_column(nullable=True)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    # Unique constraint: email unique per tenant
    __table_args__ = ({"schema": None},)

    def __repr__(self) -> str:
        return f"<User {self.email}>"

    @property
    def is_admin(self) -> bool:
        return self.role == Role.ADMIN

    @property
    def can_write(self) -> bool:
        return self.role in Role.can_write()

    @property
    def can_approve(self) -> bool:
        return self.role in Role.can_approve()
