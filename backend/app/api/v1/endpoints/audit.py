from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.v1.deps import DB, CurrentTenant, CurrentUser, RequireAdmin
from app.models import AuditAction, AuditLog
from app.schemas.audit import (
    AuditExportRequest,
    AuditExportResponse,
    AuditLogListResponse,
    AuditLogResponse,
    AuditLogSearchRequest,
)

router = APIRouter()


@router.get("", response_model=AuditLogListResponse)
async def list_audit_logs(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    user_id: UUID | None = None,
    action: AuditAction | None = None,
    resource_type: str | None = None,
    start_date: datetime | None = None,
    end_date: datetime | None = None,
):
    """List audit logs with pagination and filtering."""
    query = select(AuditLog).where(AuditLog.tenant_id == tenant.id)

    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    if action:
        query = query.where(AuditLog.action == action)

    if resource_type:
        query = query.where(AuditLog.resource_type == resource_type)

    if start_date:
        query = query.where(AuditLog.created_at >= start_date)

    if end_date:
        query = query.where(AuditLog.created_at <= end_date)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(AuditLog.created_at.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{audit_id}", response_model=AuditLogResponse)
async def get_audit_log(
    audit_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific audit log entry."""
    result = await db.execute(
        select(AuditLog).where(
            AuditLog.id == audit_id,
            AuditLog.tenant_id == tenant.id,
        )
    )
    log = result.scalar_one_or_none()

    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Audit log not found",
        )

    return log


@router.post("/search", response_model=AuditLogListResponse)
async def search_audit_logs(
    search_data: AuditLogSearchRequest,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
):
    """Search audit logs with advanced filters."""
    query = select(AuditLog).where(AuditLog.tenant_id == tenant.id)

    if search_data.user_id:
        query = query.where(AuditLog.user_id == search_data.user_id)

    if search_data.actions:
        query = query.where(AuditLog.action.in_(search_data.actions))

    if search_data.resource_type:
        query = query.where(AuditLog.resource_type == search_data.resource_type)

    if search_data.resource_id:
        query = query.where(AuditLog.resource_id == search_data.resource_id)

    if search_data.start_date:
        query = query.where(AuditLog.created_at >= search_data.start_date)

    if search_data.end_date:
        query = query.where(AuditLog.created_at <= search_data.end_date)

    if search_data.success_only:
        query = query.where(AuditLog.success)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(AuditLog.created_at.desc())

    result = await db.execute(query)
    logs = result.scalars().all()

    return AuditLogListResponse(
        items=logs,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/resource/{resource_type}/{resource_id}", response_model=list[AuditLogResponse])
async def get_resource_history(
    resource_type: str,
    resource_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    limit: int = Query(50, ge=1, le=200),
):
    """Get audit history for a specific resource."""
    result = await db.execute(
        select(AuditLog)
        .where(
            AuditLog.tenant_id == tenant.id,
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id,
        )
        .order_by(AuditLog.created_at.desc())
        .limit(limit)
    )
    logs = result.scalars().all()

    return logs


@router.post("/export", response_model=AuditExportResponse)
async def export_audit_logs(
    export_data: AuditExportRequest,
    db: DB,
    current_user: RequireAdmin,
    tenant: CurrentTenant,
):
    """Export audit logs for compliance reporting."""
    # Count records in range
    query = select(func.count(AuditLog.id)).where(
        AuditLog.tenant_id == tenant.id,
        AuditLog.created_at >= export_data.start_date,
        AuditLog.created_at <= export_data.end_date,
    )

    if export_data.actions:
        query = query.where(AuditLog.action.in_(export_data.actions))

    result = await db.execute(query)
    count = result.scalar()

    # Log the export request
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.EXPORT_AUDIT,
        description=f"Audit log export requested for {export_data.start_date} to {export_data.end_date}",
        metadata={
            "start_date": export_data.start_date.isoformat(),
            "end_date": export_data.end_date.isoformat(),
            "format": export_data.format,
            "record_count": count,
        },
        success=True,
    )
    db.add(audit)
    await db.commit()

    # In a real implementation, this would generate a file and return a download URL
    return AuditExportResponse(
        export_id=str(audit.id),
        status="pending",
        download_url=None,  # Would be populated asynchronously
        record_count=count,
    )
