"""Evidence Management API Endpoints"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.evidence import Evidence, EvidenceType, EvidenceStatus, EvidenceLink

router = APIRouter()

class EvidenceCreate(BaseModel):
    title: str
    description: Optional[str] = None
    evidence_type: str
    control_id: Optional[UUID] = None
    external_url: Optional[str] = None

class EvidenceResponse(BaseModel):
    id: UUID
    evidence_ref: str
    title: str
    evidence_type: str
    status: str
    collected_at: datetime
    file_name: Optional[str]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[EvidenceResponse])
async def list_evidence(
    evidence_type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    control_id: Optional[UUID] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Evidence).where(Evidence.tenant_id == tenant_id)
    if evidence_type:
        query = query.where(Evidence.evidence_type == evidence_type)
    if status:
        query = query.where(Evidence.status == status)
    result = await db.execute(query.order_by(Evidence.collected_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()

@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    evidence: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    evidence_id = uuid4()
    db_evidence = Evidence(
        id=evidence_id,
        tenant_id=tenant_id,
        evidence_ref=f"EVD-{str(evidence_id)[:8].upper()}",
        title=evidence.title,
        description=evidence.description,
        evidence_type=evidence.evidence_type,
        status=EvidenceStatus.DRAFT,
        external_url=evidence.external_url,
        collected_at=datetime.now(timezone.utc),
    )
    db.add(db_evidence)

    if evidence.control_id:
        link = EvidenceLink(
            id=uuid4(),
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            control_id=evidence.control_id,
            link_type="PRIMARY",
            linked_at=datetime.now(timezone.utc),
        )
        db.add(link)

    await db.commit()
    await db.refresh(db_evidence)
    return db_evidence

@router.get("/{evidence_id}", response_model=EvidenceResponse)
async def get_evidence(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")
    return evidence

@router.post("/{evidence_id}/link-control")
async def link_evidence_to_control(
    evidence_id: UUID,
    control_id: UUID = Query(...),
    link_type: str = Query("PRIMARY"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    link = EvidenceLink(
        id=uuid4(),
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        control_id=control_id,
        link_type=link_type,
        linked_at=datetime.now(timezone.utc),
    )
    db.add(link)
    await db.commit()
    return {"message": "Evidence linked to control"}
