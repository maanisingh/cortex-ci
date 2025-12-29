from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Enum as SQLEnum
from sqlalchemy import String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class EntityType(str, Enum):
    """Types of entities that can be monitored."""

    ORGANIZATION = "ORGANIZATION"
    INDIVIDUAL = "INDIVIDUAL"
    LOCATION = "LOCATION"
    FINANCIAL = "FINANCIAL"
    VESSEL = "VESSEL"
    AIRCRAFT = "AIRCRAFT"
    AI_MODEL = "AI_MODEL"
    DATA_SYSTEM = "DATA_SYSTEM"
    PROCESS = "PROCESS"
    TEAM = "TEAM"
    INFRASTRUCTURE = "INFRASTRUCTURE"
    VENDOR = "VENDOR"
    APPLICATION = "APPLICATION"
    DATASET = "DATASET"
    ASSET = "ASSET"


class Entity(Base, TimestampMixin, TenantMixin):
    """Entity model - organizations, individuals, locations being monitored."""

    __tablename__ = "entities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Core identity
    type: Mapped[EntityType] = mapped_column(SQLEnum(EntityType), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    # Additional identifiers
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    registration_number: Mapped[str | None] = mapped_column(String(255), nullable=True)
    tax_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Location
    country_code: Mapped[str | None] = mapped_column(String(3), nullable=True, index=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, nullable=False)

    # Criticality (1-5, where 5 is most critical)
    criticality: Mapped[int] = mapped_column(default=3, nullable=False)

    # Flexible custom data
    custom_data: Mapped[dict] = mapped_column(JSONB, default=dict, nullable=False)

    # Status
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    tenant = relationship("Tenant", back_populates="entities")
    risk_scores = relationship("RiskScore", back_populates="entity", cascade="all, delete-orphan")

    # Dependencies (as source)
    outgoing_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.source_entity_id",
        back_populates="source_entity",
        cascade="all, delete-orphan",
    )
    # Dependencies (as target)
    incoming_dependencies = relationship(
        "Dependency",
        foreign_keys="Dependency.target_entity_id",
        back_populates="target_entity",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:
        return f"<Entity {self.type.value}:{self.name}>"

    @property
    def all_names(self) -> list[str]:
        """Return all names including aliases."""
        return [self.name] + (self.aliases or [])
