from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    job_title: str | None = None
    department: str | None = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)
    role: str = "viewer"


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: str | None = Field(None, min_length=2, max_length=255)
    job_title: str | None = None
    department: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    tenant_id: UUID
    role: str
    is_active: bool
    is_verified: bool
    last_login: datetime | None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
