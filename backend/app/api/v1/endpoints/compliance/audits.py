"""Audit Management API Endpoints"""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.audit import (
    Audit,
    AuditFinding,
    AuditStatus,
    FindingStatus,
    FindingSeverity,
    RemediationPlan,
)

router = APIRouter()


class AuditCreate(BaseModel):
    title: str
    audit_type: str
    description: str | None = None
    scope_description: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    in_scope_systems: list[str] | None = None
    in_scope_frameworks: list[str] | None = None


class AuditUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    scope_description: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    overall_rating: str | None = None
    opinion: str | None = None


class AuditResponse(BaseModel):
    id: UUID
    audit_ref: str
    title: str
    description: str | None = None
    audit_type: str
    status: str
    scope_description: str | None = None
    planned_start: date | None = None
    planned_end: date | None = None
    actual_start: date | None = None
    actual_end: date | None = None
    total_findings: int
    critical_findings: int
    high_findings: int
    medium_findings: int
    low_findings: int
    overall_rating: str | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class AuditListResponse(BaseModel):
    items: list[AuditResponse]
    total: int
    page: int
    page_size: int


class AuditSummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_type: dict[str, int]
    in_progress: int
    completed_this_year: int
    total_open_findings: int


class FindingCreate(BaseModel):
    title: str
    severity: str
    description: str
    recommendation: str | None = None
    root_cause: str | None = None
    impact: str | None = None
    target_remediation_date: date | None = None
    owner_department: str | None = None


class FindingUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    recommendation: str | None = None
    root_cause: str | None = None
    impact: str | None = None
    target_remediation_date: date | None = None
    owner_department: str | None = None


class FindingResponse(BaseModel):
    id: UUID
    audit_id: UUID
    finding_ref: str
    title: str
    description: str
    severity: str
    status: str
    recommendation: str | None = None
    root_cause: str | None = None
    impact: str | None = None
    management_response: str | None = None
    target_remediation_date: date | None = None
    actual_remediation_date: date | None = None
    owner_department: str | None = None
    is_repeat: bool
    created_at: datetime | None = None
    audit_title: str | None = None

    class Config:
        from_attributes = True


class FindingListResponse(BaseModel):
    items: list[FindingResponse]
    total: int
    page: int
    page_size: int


class FindingSummary(BaseModel):
    total_open: int
    critical_open: int
    high_open: int
    medium_open: int
    low_open: int
    overdue: int
    pending_validation: int
    closed_this_month: int
    by_status: dict[str, int]
    by_severity: dict[str, int]
    avg_days_to_close: float | None


class ManagementResponseRequest(BaseModel):
    response: str
    target_date: date | None = None


@router.get("/summary", response_model=AuditSummary)
async def get_audit_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get audit summary statistics."""
    result = await db.execute(select(Audit).where(Audit.tenant_id == tenant_id))
    audits = result.scalars().all()

    by_status: dict[str, int] = {}
    by_type: dict[str, int] = {}
    in_progress = 0
    completed_this_year = 0
    current_year = date.today().year

    for a in audits:
        status_val = a.status if isinstance(a.status, str) else a.status.value
        by_status[status_val] = by_status.get(status_val, 0) + 1

        type_val = a.audit_type if isinstance(a.audit_type, str) else a.audit_type.value
        by_type[type_val] = by_type.get(type_val, 0) + 1

        if status_val == "IN_PROGRESS":
            in_progress += 1
        if status_val == "CLOSED" and a.actual_end and a.actual_end.year == current_year:
            completed_this_year += 1

    # Count open findings
    findings_result = await db.execute(
        select(func.count(AuditFinding.id)).where(
            and_(
                AuditFinding.tenant_id == tenant_id,
                AuditFinding.status.in_(["OPEN", "IN_PROGRESS"]),
            )
        )
    )
    total_open_findings = findings_result.scalar() or 0

    return AuditSummary(
        total=len(audits),
        by_status=by_status,
        by_type=by_type,
        in_progress=in_progress,
        completed_this_year=completed_this_year,
        total_open_findings=total_open_findings,
    )


@router.get("/", response_model=AuditListResponse)
async def list_audits(
    audit_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List audits with filtering and pagination."""
    query = select(Audit).where(Audit.tenant_id == tenant_id)

    if audit_type:
        query = query.where(Audit.audit_type == audit_type)
    if status_filter:
        query = query.where(Audit.status == status_filter)
    if search:
        query = query.where(
            Audit.title.ilike(f"%{search}%") | Audit.audit_ref.ilike(f"%{search}%")
        )

    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    query = query.order_by(Audit.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    return AuditListResponse(
        items=result.scalars().all(),
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit: AuditCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Create a new audit."""
    audit_id = uuid4()
    db_audit = Audit(
        id=audit_id,
        tenant_id=tenant_id,
        audit_ref=f"AUD-{str(audit_id)[:8].upper()}",
        title=audit.title,
        audit_type=audit.audit_type,
        description=audit.description,
        scope_description=audit.scope_description,
        status=AuditStatus.PLANNED,
        planned_start=audit.planned_start,
        planned_end=audit.planned_end,
        in_scope_systems=audit.in_scope_systems or [],
        in_scope_frameworks=audit.in_scope_frameworks or [],
    )
    db.add(db_audit)
    await db.commit()
    await db.refresh(db_audit)
    return db_audit


@router.get("/{audit_id}", response_model=AuditResponse)
async def get_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get audit details."""
    result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")
    return audit


@router.put("/{audit_id}", response_model=AuditResponse)
async def update_audit(
    audit_id: UUID,
    data: AuditUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update audit."""
    result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(audit, field, value)

    await db.commit()
    await db.refresh(audit)
    return audit


@router.delete("/{audit_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Delete audit."""
    result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    await db.delete(audit)
    await db.commit()


@router.post("/{audit_id}/start")
async def start_audit(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Start an audit (move to IN_PROGRESS)."""
    result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    audit.status = AuditStatus.IN_PROGRESS
    audit.actual_start = date.today()
    await db.commit()
    return {"message": "Audit started", "audit_id": str(audit_id)}


@router.post("/{audit_id}/complete")
async def complete_audit(
    audit_id: UUID,
    overall_rating: str = Query(None),
    opinion: str = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Complete an audit."""
    result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    audit.status = AuditStatus.CLOSED
    audit.actual_end = date.today()
    if overall_rating:
        audit.overall_rating = overall_rating
    if opinion:
        audit.opinion = opinion

    await db.commit()
    return {"message": "Audit completed", "audit_id": str(audit_id)}


# ==================== FINDINGS ENDPOINTS ====================

@router.get("/findings/summary", response_model=FindingSummary)
async def get_findings_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get findings summary statistics."""
    today = date.today()
    month_start = today.replace(day=1)

    result = await db.execute(
        select(AuditFinding).where(AuditFinding.tenant_id == tenant_id)
    )
    findings = result.scalars().all()

    by_status: dict[str, int] = {}
    by_severity: dict[str, int] = {}
    total_open = 0
    critical_open = 0
    high_open = 0
    medium_open = 0
    low_open = 0
    overdue = 0
    pending_validation = 0
    closed_this_month = 0
    total_days_to_close = 0
    closed_count = 0

    for f in findings:
        status_val = f.status if isinstance(f.status, str) else f.status.value
        severity_val = f.severity if isinstance(f.severity, str) else f.severity.value

        by_status[status_val] = by_status.get(status_val, 0) + 1
        by_severity[severity_val] = by_severity.get(severity_val, 0) + 1

        if status_val in ["OPEN", "IN_PROGRESS"]:
            total_open += 1
            if severity_val == "CRITICAL":
                critical_open += 1
            elif severity_val == "HIGH":
                high_open += 1
            elif severity_val == "MEDIUM":
                medium_open += 1
            elif severity_val == "LOW":
                low_open += 1

            if f.target_remediation_date and f.target_remediation_date < today:
                overdue += 1

        if status_val == "PENDING_VALIDATION":
            pending_validation += 1

        if status_val == "CLOSED":
            if f.actual_remediation_date and f.actual_remediation_date >= month_start:
                closed_this_month += 1
            if f.actual_remediation_date and f.created_at:
                days = (f.actual_remediation_date - f.created_at.date()).days
                total_days_to_close += days
                closed_count += 1

    avg_days = (total_days_to_close / closed_count) if closed_count > 0 else None

    return FindingSummary(
        total_open=total_open,
        critical_open=critical_open,
        high_open=high_open,
        medium_open=medium_open,
        low_open=low_open,
        overdue=overdue,
        pending_validation=pending_validation,
        closed_this_month=closed_this_month,
        by_status=by_status,
        by_severity=by_severity,
        avg_days_to_close=avg_days,
    )


@router.get("/findings/all", response_model=FindingListResponse)
async def list_all_findings(
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List all findings across all audits with filtering and pagination."""
    query = select(AuditFinding, Audit.title.label("audit_title")).join(
        Audit, Audit.id == AuditFinding.audit_id
    ).where(AuditFinding.tenant_id == tenant_id)

    if severity:
        query = query.where(AuditFinding.severity == severity)
    if status_filter:
        query = query.where(AuditFinding.status == status_filter)
    if search:
        query = query.where(
            AuditFinding.title.ilike(f"%{search}%")
            | AuditFinding.description.ilike(f"%{search}%")
            | AuditFinding.finding_ref.ilike(f"%{search}%")
        )

    # Count total
    count_query = select(func.count(AuditFinding.id)).where(
        AuditFinding.tenant_id == tenant_id
    )
    if severity:
        count_query = count_query.where(AuditFinding.severity == severity)
    if status_filter:
        count_query = count_query.where(AuditFinding.status == status_filter)
    if search:
        count_query = count_query.where(
            AuditFinding.title.ilike(f"%{search}%")
            | AuditFinding.description.ilike(f"%{search}%")
            | AuditFinding.finding_ref.ilike(f"%{search}%")
        )

    count_result = await db.execute(count_query)
    total = count_result.scalar() or 0

    query = query.order_by(AuditFinding.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    rows = result.all()

    items = []
    for finding, audit_title in rows:
        finding_dict = {
            "id": finding.id,
            "audit_id": finding.audit_id,
            "finding_ref": finding.finding_ref,
            "title": finding.title,
            "description": finding.description,
            "severity": finding.severity if isinstance(finding.severity, str) else finding.severity.value,
            "status": finding.status if isinstance(finding.status, str) else finding.status.value,
            "recommendation": finding.recommendation,
            "root_cause": finding.root_cause,
            "impact": finding.impact,
            "management_response": finding.management_response,
            "target_remediation_date": finding.target_remediation_date,
            "actual_remediation_date": finding.actual_remediation_date,
            "owner_department": finding.owner_department,
            "is_repeat": finding.is_repeat,
            "created_at": finding.created_at,
            "audit_title": audit_title,
        }
        items.append(FindingResponse(**finding_dict))

    return FindingListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{audit_id}/findings", response_model=list[FindingResponse])
async def list_audit_findings(
    audit_id: UUID,
    severity: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List findings for an audit."""
    query = select(AuditFinding).where(
        and_(AuditFinding.audit_id == audit_id, AuditFinding.tenant_id == tenant_id)
    )
    if severity:
        query = query.where(AuditFinding.severity == severity)
    if status_filter:
        query = query.where(AuditFinding.status == status_filter)

    result = await db.execute(query.order_by(AuditFinding.created_at.desc()))
    return result.scalars().all()


@router.post("/{audit_id}/findings", response_model=FindingResponse, status_code=status.HTTP_201_CREATED)
async def create_finding(
    audit_id: UUID,
    finding: FindingCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Create a new finding."""
    # Verify audit exists
    audit_result = await db.execute(
        select(Audit).where(and_(Audit.id == audit_id, Audit.tenant_id == tenant_id))
    )
    audit = audit_result.scalar_one_or_none()
    if not audit:
        raise HTTPException(status_code=404, detail="Audit not found")

    finding_id = uuid4()
    db_finding = AuditFinding(
        id=finding_id,
        tenant_id=tenant_id,
        audit_id=audit_id,
        finding_ref=f"FND-{str(finding_id)[:8].upper()}",
        title=finding.title,
        severity=finding.severity,
        description=finding.description,
        recommendation=finding.recommendation,
        root_cause=finding.root_cause,
        impact=finding.impact,
        target_remediation_date=finding.target_remediation_date,
        owner_department=finding.owner_department,
        status=FindingStatus.OPEN,
    )
    db.add(db_finding)

    # Update audit counts
    audit.total_findings += 1
    if finding.severity == "CRITICAL":
        audit.critical_findings += 1
    elif finding.severity == "HIGH":
        audit.high_findings += 1
    elif finding.severity == "MEDIUM":
        audit.medium_findings += 1
    elif finding.severity == "LOW":
        audit.low_findings += 1

    await db.commit()
    await db.refresh(db_finding)
    return db_finding


@router.get("/findings/open", response_model=list[FindingResponse])
async def get_open_findings(
    severity: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get all open findings across all audits."""
    query = select(AuditFinding).where(
        and_(
            AuditFinding.tenant_id == tenant_id,
            AuditFinding.status.in_(["OPEN", "IN_PROGRESS"]),
        )
    )
    if severity:
        query = query.where(AuditFinding.severity == severity)

    result = await db.execute(query.order_by(AuditFinding.created_at.desc()))
    return result.scalars().all()


@router.get("/findings/overdue", response_model=list[FindingResponse])
async def get_overdue_findings(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get overdue findings."""
    today = date.today()
    result = await db.execute(
        select(AuditFinding)
        .where(
            and_(
                AuditFinding.tenant_id == tenant_id,
                AuditFinding.status.in_(["OPEN", "IN_PROGRESS"]),
                AuditFinding.target_remediation_date < today,
            )
        )
        .order_by(AuditFinding.target_remediation_date)
    )
    return result.scalars().all()


@router.get("/findings/{finding_id}", response_model=FindingResponse)
async def get_finding(
    finding_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get finding details."""
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")
    return finding


@router.put("/findings/{finding_id}", response_model=FindingResponse)
async def update_finding(
    finding_id: UUID,
    data: FindingUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update a finding."""
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(finding, field, value)

    await db.commit()
    await db.refresh(finding)
    return finding


@router.post("/findings/{finding_id}/respond")
async def management_response(
    finding_id: UUID,
    response_data: ManagementResponseRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Add management response to finding."""
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.management_response = response_data.response
    finding.response_date = date.today()
    finding.response_by = current_user.id
    if response_data.target_date:
        finding.target_remediation_date = response_data.target_date
    finding.status = FindingStatus.IN_PROGRESS

    await db.commit()
    return {"message": "Management response recorded", "finding_id": str(finding_id)}


@router.post("/findings/{finding_id}/close")
async def close_finding(
    finding_id: UUID,
    verification_notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Close a finding after verification."""
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    finding.status = FindingStatus.CLOSED
    finding.actual_remediation_date = date.today()
    finding.verified_by = current_user.id
    finding.verified_at = datetime.now(UTC)
    if verification_notes:
        finding.verification_notes = verification_notes

    await db.commit()
    return {"message": "Finding closed", "finding_id": str(finding_id)}


@router.patch("/findings/{finding_id}/status")
async def update_finding_status(
    finding_id: UUID,
    new_status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update finding status."""
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.id == finding_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    finding = result.scalar_one_or_none()
    if not finding:
        raise HTTPException(status_code=404, detail="Finding not found")

    try:
        finding.status = FindingStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    await db.commit()
    return {"message": f"Finding status updated to {new_status}", "finding_id": str(finding_id)}
