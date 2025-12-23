from datetime import datetime
from typing import Optional, List, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.models.audit import AuditAction


class AuditLogResponse(BaseModel):
    """Audit log entry response schema."""
    id: UUID
    tenant_id: UUID
    created_at: datetime
    user_id: Optional[UUID]
    user_email: Optional[str]
    user_role: Optional[str]
    action: AuditAction
    resource_type: Optional[str]
    resource_id: Optional[UUID]
    resource_name: Optional[str]
    before_state: Optional[Dict[str, Any]]
    after_state: Optional[Dict[str, Any]]
    changes: Optional[Dict[str, Any]]
    description: Optional[str]
    metadata: Dict[str, Any]
    ip_address: Optional[str]
    success: bool
    error_message: Optional[str]

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
