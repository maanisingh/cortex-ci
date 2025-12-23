from datetime import datetime, date, timezone
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from sqlalchemy import String, Text, Date, DateTime, Enum as SQLEnum, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class ConstraintType(str, Enum):
    """Types of internal constraints."""
    POLICY = "policy"
    REGULATION = "regulation"
    COMPLIANCE = "compliance"
    CONTRACTUAL = "contractual"
    OPERATIONAL = "operational"
    FINANCIAL = "financial"
    SECURITY = "security"
    CUSTOM = "custom"


class ConstraintSeverity(str, Enum):
    """Severity levels for constraints."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class Constraint(Base, TimestampMixin, TenantMixin):
    """Internal constraint model - policies, regulations, rules that affect entities."""

    __tablename__ = "constraints"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Constraint details
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    type: Mapped[ConstraintType] = mapped_column(
        SQLEnum(ConstraintType), nullable=False, index=True
    )
    severity: Mapped[ConstraintSeverity] = mapped_column(
        SQLEnum(ConstraintSeverity), default=ConstraintSeverity.MEDIUM, nullable=False
    )

    # Reference information
    reference_code: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    source_document: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    external_url: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Applicability
    applies_to_entity_types: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    applies_to_countries: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )
    applies_to_categories: Mapped[List[str]] = mapped_column(
        ARRAY(String), default=list, nullable=False
    )

    # Dates
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Risk impact
    risk_weight: Mapped[float] = mapped_column(default=1.0, nullable=False)

    # Requirements/conditions
    requirements: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)
    """
    Example:
    {
        "conditions": ["Must have valid license", "Annual audit required"],
        "exceptions": ["Entities under $1M revenue"],
        "documentation": ["License copy", "Audit report"]
    }
    """

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Custom data
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list, nullable=False)
    custom_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Created by
    created_by: Mapped[Optional[UUID]] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Relationships
    creator = relationship("User", foreign_keys=[created_by])

    def __repr__(self) -> str:
        return f"<Constraint {self.name} ({self.type.value})>"

    @property
    def is_currently_active(self) -> bool:
        """Check if the constraint is currently in effect."""
        today = date.today()
        if self.effective_date and self.effective_date > today:
            return False
        if self.expiry_date and self.expiry_date < today:
            return False
        return self.is_active
