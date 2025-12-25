from datetime import datetime
from typing import Optional, List
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field


class UserBase(BaseModel):
    """Base user schema."""

    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    job_title: Optional[str] = None
    department: Optional[str] = None


class UserCreate(UserBase):
    """User creation schema."""

    password: str = Field(..., min_length=8)
    role: str = "viewer"


class UserUpdate(BaseModel):
    """User update schema."""

    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    job_title: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """User response schema."""

    id: UUID
    tenant_id: UUID
    role: str
    is_active: bool
    is_verified: bool
    last_login: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class UserListResponse(BaseModel):
    """Paginated user list response."""

    items: List[UserResponse]
    total: int
    page: int
    page_size: int
    pages: int
