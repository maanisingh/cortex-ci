from datetime import datetime
from typing import Optional, List, Dict, Any
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
    description: Optional[str] = None
    is_bidirectional: bool = False
    custom_data: Dict[str, Any] = {}


class DependencyCreate(DependencyBase):
    """Dependency creation schema."""
    pass


class DependencyUpdate(BaseModel):
    """Dependency update schema."""
    layer: Optional[DependencyLayer] = None
    relationship_type: Optional[RelationshipType] = None
    criticality: Optional[int] = Field(None, ge=1, le=5)
    description: Optional[str] = None
    is_bidirectional: Optional[bool] = None
    custom_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class DependencyResponse(DependencyBase):
    """Dependency response schema."""
    id: UUID
    tenant_id: UUID
    is_active: bool
    created_at: datetime
    updated_at: datetime

    # Optionally include related entity info
    source_entity_name: Optional[str] = None
    target_entity_name: Optional[str] = None

    class Config:
        from_attributes = True


class DependencyListResponse(BaseModel):
    """Paginated dependency list response."""
    items: List[DependencyResponse]
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
    risk_level: Optional[str] = None
    metadata: Dict[str, Any] = {}


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
    nodes: List[DependencyGraphNode]
    edges: List[DependencyGraphEdge]
    stats: Dict[str, Any] = {}
