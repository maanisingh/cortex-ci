from datetime import datetime
from ipaddress import IPv4Address, IPv6Address
from typing import Any
from uuid import UUID

from pydantic import BaseModel, field_validator

from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    user_id: UUID | None = None
    user_email: str | None = None
    user_role: str | None = None
    action: AuditAction
    resource_type: str | None = None
    resource_id: UUID | None = None
    resource_name: str | None = None
    before_state: dict[str, Any] | None = None
    after_state: dict[str, Any] | None = None
    changes: dict[str, Any] | None = None
    description: str | None = None
    context_data: dict[str, Any] | None = None
    ip_address: str | None = None
    success: bool
    error_message: str | None = None

    @field_validator("ip_address", mode="before")
    @classmethod
    def convert_ip_to_string(cls, v):
        if v is None:
            return None
        if isinstance(v, (IPv4Address, IPv6Address)):
            return str(v)
        return v

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""

    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AuditLogSearchRequest(BaseModel):
    """Search audit logs."""

    user_id: UUID | None = None
    actions: list[AuditAction] | None = None
    resource_type: str | None = None
    resource_id: UUID | None = None
    start_date: datetime | None = None
    end_date: datetime | None = None
    success_only: bool = False


class AuditExportRequest(BaseModel):
    """Request to export audit logs."""

    start_date: datetime
    end_date: datetime
    actions: list[AuditAction] | None = None
    format: str = "json"  # json, csv


class AuditExportResponse(BaseModel):
    """Audit export response."""

    export_id: str
    status: str
    download_url: str | None = None
    record_count: int
    file_size: int | None = None
