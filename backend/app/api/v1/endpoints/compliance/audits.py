"""Audit Management API Endpoints"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.audit import Audit, AuditType, AuditStatus, AuditFinding, FindingSeverity

router = APIRouter()

class AuditCreate(BaseModel):
    title: str
    audit_type: str
    description: Optional[str] = None
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None

class AuditResponse(BaseModel):
    id: UUID
    audit_ref: str
    title: str
    audit_type: str
    status: str
    total_findings: int
    critical_findings: int

    class Config:
        from_attributes = True

class FindingCreate(BaseModel):
    title: str
    severity: str
    description: str
    recommendation: Optional[str] = None

class FindingResponse(BaseModel):
    id: UUID
    finding_ref: str
    title: str
    severity: str
    status: str

    class Config:
        from_attributes = True

@router.get("/", response_model=List[AuditResponse])
async def list_audits(
    audit_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Audit).where(Audit.tenant_id == tenant_id)
    if audit_type:
        query = query.where(Audit.audit_type == audit_type)
    if status:
        query = query.where(Audit.status == status)
    result = await db.execute(query.order_by(Audit.created_at.desc()))
    return result.scalars().all()

@router.post("/", response_model=AuditResponse, status_code=status.HTTP_201_CREATED)
async def create_audit(
    audit: AuditCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    audit_id = uuid4()
    db_audit = Audit(
        id=audit_id,
        tenant_id=tenant_id,
        audit_ref=f"AUD-{str(audit_id)[:8].upper()}",
        title=audit.title,
        audit_type=audit.audit_type,
        description=audit.description,
        status=AuditStatus.PLANNED,
        planned_start=audit.planned_start,
        planned_end=audit.planned_end,
    )
    db.add(db_audit)
    await db.commit()
    await db.refresh(db_audit)
    return db_audit

@router.get("/{audit_id}/findings", response_model=List[FindingResponse])
async def list_audit_findings(
    audit_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(AuditFinding).where(
            and_(AuditFinding.audit_id == audit_id, AuditFinding.tenant_id == tenant_id)
        )
    )
    return result.scalars().all()

@router.post("/{audit_id}/findings", response_model=FindingResponse)
async def create_finding(
    audit_id: UUID,
    finding: FindingCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
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
        status="OPEN",
    )
    db.add(db_finding)

    # Update audit counts
    result = await db.execute(select(Audit).where(Audit.id == audit_id))
    audit = result.scalar_one_or_none()
    if audit:
        audit.total_findings += 1
        if finding.severity == "CRITICAL":
            audit.critical_findings += 1
        elif finding.severity == "HIGH":
            audit.high_findings += 1

    await db.commit()
    await db.refresh(db_finding)
    return db_finding
