from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.dependency import DependencyLayer, RelationshipType


class DependencyBase(BaseModel):
    """Base dependency schema."""

    source_entity_id: UUID
    target_entity_id: UUID
    layer: DependencyLayer = DependencyLayer.OPERATIONAL
    relationship_type: RelationshipType
    criticality: int = Field(3, ge=1, le=5)
    description: str | None = None
    is_bidirectional: bool = False
    custom_data: dict[str, Any] = {}


class DependencyCreate(DependencyBase):
    """Dependency creation schema."""

    pass


class DependencyUpdate(BaseModel):
    """Dependency update schema."""

    layer: DependencyLayer | None = None
    relationship_type: RelationshipType | None = None
    criticality: int | None = Field(None, ge=1, le=5)
    description: str | None = None
    is_bidirectional: bool | None = None
    custom_data: dict[str, Any] | None = None
    is_active: bool | None = None


class DependencyResponse(DependencyBase):
    """Dependency response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Optionally include related entity info
    source_entity_name: str | None = None
    target_entity_name: str | None = None

    class Config:
        from_attributes = True


class DependencyListResponse(BaseModel):
    """Paginated dependency list response."""

    items: list[DependencyResponse]
    total: int
    page: int
    page_size: int
    pages: int


class DependencyGraphNode(BaseModel):
    """Node in the dependency graph."""

    id: str
    label: str
    type: str
    criticality: int
    risk_level: str | None = None
    metadata: dict[str, Any] = {}


class DependencyGraphEdge(BaseModel):
    """Edge in the dependency graph."""

    id: str
    source: str
    target: str
    layer: str
    relationship: str
    criticality: int
    is_bidirectional: bool


class DependencyGraphResponse(BaseModel):
    """Full dependency graph for visualization."""

    nodes: list[DependencyGraphNode]
    edges: list[DependencyGraphEdge]
    stats: dict[str, Any] = {}
