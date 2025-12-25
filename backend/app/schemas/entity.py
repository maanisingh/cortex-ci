from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, Field

from app.models.entity import EntityType


class EntityBase(BaseModel):
    """Base entity schema."""

    type: EntityType
    name: str = Field(..., min_length=1, max_length=500)
    aliases: List[str] = []
    external_id: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    country_code: Optional[str] = Field(None, max_length=3)
    address: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: List[str] = []
    criticality: int = Field(3, ge=1, le=5)
    custom_data: Dict[str, Any] = {}


class EntityCreate(EntityBase):
    """Entity creation schema."""

    pass


class EntityUpdate(BaseModel):
    """Entity update schema."""

    name: Optional[str] = Field(None, min_length=1, max_length=500)
    aliases: Optional[List[str]] = None
    external_id: Optional[str] = None
    registration_number: Optional[str] = None
    tax_id: Optional[str] = None
    country_code: Optional[str] = Field(None, max_length=3)
    address: Optional[str] = None
    category: Optional[str] = None
    subcategory: Optional[str] = None
    tags: Optional[List[str]] = None
    criticality: Optional[int] = Field(None, ge=1, le=5)
    custom_data: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None


class EntityResponse(EntityBase):
    """Entity response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EntityListResponse(BaseModel):
    """Paginated entity list response."""

    items: List[EntityResponse]
    total: int
    page: int
    page_size: int
    pages: int


class EntityScreenRequest(BaseModel):
    """Request to screen an entity or list of entities."""

    entity_ids: Optional[List[UUID]] = None  # Screen specific entities
    name: Optional[str] = None  # Screen a name (without creating entity)
    aliases: List[str] = []


class EntityBulkImportRequest(BaseModel):
    """Bulk import request."""

    entities: List[EntityCreate]
    skip_duplicates: bool = True


class EntityBulkImportResponse(BaseModel):
    """Bulk import response."""

    imported: int
    skipped: int
    errors: List[Dict[str, Any]]
