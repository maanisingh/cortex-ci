from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.entity import EntityType


class EntityBase(BaseModel):
    """Base entity schema."""

    type: EntityType
    name: str = Field(..., min_length=1, max_length=500)
    aliases: list[str] = []
    external_id: str | None = None
    registration_number: str | None = None
    tax_id: str | None = None
    country_code: str | None = Field(None, max_length=3)
    address: str | None = None
    category: str | None = None
    subcategory: str | None = None
    tags: list[str] = []
    criticality: int = Field(3, ge=1, le=5)
    custom_data: dict[str, Any] = {}


class EntityCreate(EntityBase):
    """Entity creation schema."""

    pass


class EntityUpdate(BaseModel):
    """Entity update schema."""

    name: str | None = Field(None, min_length=1, max_length=500)
    aliases: list[str] | None = None
    external_id: str | None = None
    registration_number: str | None = None
    tax_id: str | None = None
    country_code: str | None = Field(None, max_length=3)
    address: str | None = None
    category: str | None = None
    subcategory: str | None = None
    tags: list[str] | None = None
    criticality: int | None = Field(None, ge=1, le=5)
    custom_data: dict[str, Any] | None = None
    is_active: bool | None = None
    notes: str | None = None


class EntityResponse(EntityBase):
    """Entity response schema."""

    id: UUID
    tenant_id: UUID
    is_active: bool
    notes: str | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EntityListResponse(BaseModel):
    """Paginated entity list response."""

    items: list[EntityResponse]
    total: int
    page: int
    page_size: int
    pages: int


class EntityScreenRequest(BaseModel):
    """Request to screen an entity or list of entities."""

    entity_ids: list[UUID] | None = None  # Screen specific entities
    name: str | None = None  # Screen a name (without creating entity)
    aliases: list[str] = []


class EntityBulkImportRequest(BaseModel):
    """Bulk import request."""

    entities: list[EntityCreate]
    skip_duplicates: bool = True


class EntityBulkImportResponse(BaseModel):
    """Bulk import response."""

    imported: int
    skipped: int
    errors: list[dict[str, Any]]
