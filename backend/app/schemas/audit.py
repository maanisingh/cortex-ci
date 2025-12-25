from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel, field_serializer

from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""

    id: UUID
    tenant_id: UUID
    created_at: datetime
    user_id: Optional[UUID] = None
    user_email: Optional[str] = None
    user_role: Optional[str] = None
    action: AuditAction
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    resource_name: Optional[str] = None
    before_state: Optional[Dict[str, Any]] = None
    after_state: Optional[Dict[str, Any]] = None
    changes: Optional[Dict[str, Any]] = None
    description: Optional[str] = None
    context_data: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    success: bool
    error_message: Optional[str] = None

    @field_serializer("ip_address")
    def serialize_ip(self, v):
        return str(v) if v else None

    class Config:
        from_attributes = True


class AuditLogListResponse(BaseModel):
    """Paginated audit log list response."""

    items: List[AuditLogResponse]
    total: int
    page: int
    page_size: int
    pages: int


class AuditLogSearchRequest(BaseModel):
    """Search audit logs."""

    user_id: Optional[UUID] = None
    actions: Optional[List[AuditAction]] = None
    resource_type: Optional[str] = None
    resource_id: Optional[UUID] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    success_only: bool = False


class AuditExportRequest(BaseModel):
    """Request to export audit logs."""

    start_date: datetime
    end_date: datetime
    actions: Optional[List[AuditAction]] = None
    format: str = "json"  # json, csv


class AuditExportResponse(BaseModel):
    """Audit export response."""

    export_id: str
    status: str
    download_url: Optional[str] = None
    record_count: int
    file_size: Optional[int] = None
