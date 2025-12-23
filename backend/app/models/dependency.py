from datetime import datetime, timezone
from uuid import UUID, uuid4
from typing import Optional
from enum import Enum
from sqlalchemy import String, Text, ForeignKey, Integer, Enum as SQLEnum, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class DependencyLayer(str, Enum):
    """Layer classification for multi-layer dependency modeling (Phase 2 ready)."""
    LEGAL = "legal"  # Contracts, grants, obligations
    FINANCIAL = "financial"  # Banks, currencies, payment corridors
    OPERATIONAL = "operational"  # Suppliers, logistics, IT
    ACADEMIC = "academic"  # Research partners, funding sources
    HUMAN = "human"  # Key personnel, irreplaceable staff


class RelationshipType(str, Enum):
    """Type of relationship between entities."""
    # Operational
    SUPPLIES = "supplies"
    PROCURES_FROM = "procures_from"
    PROVIDES_SERVICE = "provides_service"
    RECEIVES_SERVICE = "receives_service"
    HOSTS_INFRASTRUCTURE = "hosts_infrastructure"
    USES_INFRASTRUCTURE = "uses_infrastructure"

    # Financial
    BANKS_WITH = "banks_with"
    RECEIVES_PAYMENT = "receives_payment"
    MAKES_PAYMENT = "makes_payment"
    INVESTS_IN = "invests_in"
    RECEIVES_INVESTMENT = "receives_investment"

    # Legal
    CONTRACTS_WITH = "contracts_with"
    LICENSED_BY = "licensed_by"
    REGULATED_BY = "regulated_by"

    # Organizational
    OWNS = "owns"
    OWNED_BY = "owned_by"
    SUBSIDIARY_OF = "subsidiary_of"
    PARTNER_WITH = "partner_with"
    EMPLOYS = "employs"
    EMPLOYED_BY = "employed_by"

    # Academic/Research
    COLLABORATES_WITH = "collaborates_with"
    FUNDED_BY = "funded_by"
    FUNDS = "funds"

    # Generic
    DEPENDS_ON = "depends_on"
    CONNECTED_TO = "connected_to"


class Dependency(Base, TimestampMixin, TenantMixin):
    """Dependency relationship between two entities."""

    __tablename__ = "dependencies"

    id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), primary_key=True, default=uuid4
    )

    # Related entities
    source_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    target_entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # Classification (Phase 2 multi-layer support)
    layer: Mapped[DependencyLayer] = mapped_column(
        SQLEnum(DependencyLayer),
        default=DependencyLayer.OPERATIONAL,
        nullable=False,
        index=True,
    )
    relationship_type: Mapped[RelationshipType] = mapped_column(
        SQLEnum(RelationshipType), nullable=False
    )

    # Criticality (1-5, where 5 is most critical)
    criticality: Mapped[int] = mapped_column(Integer, default=3, nullable=False)

    # Description
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # For reversible relationships
    is_bidirectional: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    # Flexible metadata (contract numbers, amounts, dates, etc.)
    metadata: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    source_entity = relationship(
        "Entity",
        foreign_keys=[source_entity_id],
        back_populates="outgoing_dependencies",
    )
    target_entity = relationship(
        "Entity",
        foreign_keys=[target_entity_id],
        back_populates="incoming_dependencies",
    )

    def __repr__(self) -> str:
        return f"<Dependency {self.source_entity_id} --[{self.relationship_type.value}]--> {self.target_entity_id}>"
