from uuid import UUID, uuid4
from typing import Optional
from sqlalchemy import String, Boolean, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin


class Tenant(Base, TimestampMixin):
    """Multi-tenant organization model."""

    __tablename__ = "tenants"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Settings stored as JSONB for flexibility
    settings: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Risk weights (can be customized per tenant)
    risk_weights: Mapped[dict] = mapped_column(
        JSONB,
        default=lambda: {
            "direct_match": 0.4,
            "indirect_match": 0.25,
            "country_risk": 0.2,
            "dependency": 0.15,
        },
        nullable=False,
    )

    # Relationships
    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    entities = relationship(
        "Entity", back_populates="tenant", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:
        return f"<Tenant {self.slug}>"
