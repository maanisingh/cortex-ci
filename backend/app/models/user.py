from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import String, Boolean, ForeignKey, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin
from app.core.security import Role


class User(Base, TimestampMixin, TenantMixin):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    email: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)

    # Profile
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    job_title: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Role-based access control
    role: Mapped[str] = mapped_column(
        String(50), nullable=False, default=Role.VIEWER
    )

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Metadata
    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Relationships
    tenant = relationship("Tenant", back_populates="users")

    # Unique constraint: email unique per tenant
    __table_args__ = (
        {"schema": None},
    )

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
