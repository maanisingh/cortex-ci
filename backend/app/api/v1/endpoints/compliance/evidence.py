"""Evidence Management API Endpoints"""

from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.evidence import Evidence, EvidenceLink, EvidenceReview, EvidenceStatus

router = APIRouter()


class EvidenceCreate(BaseModel):
    title: str
    description: str | None = None
    evidence_type: str
    control_id: UUID | None = None
    external_url: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    is_perpetual: bool = False


class EvidenceUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    category: str | None = None
    tags: list[str] | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    is_perpetual: bool | None = None


class EvidenceResponse(BaseModel):
    id: UUID
    evidence_ref: str
    title: str
    description: str | None = None
    evidence_type: str
    category: str | None = None
    status: str
    collected_at: datetime
    file_name: str | None = None
    file_size: int | None = None
    external_url: str | None = None
    valid_from: date | None = None
    valid_to: date | None = None
    is_perpetual: bool
    tags: list[str] | None = None
    created_at: datetime | None = None

    class Config:
        from_attributes = True


class EvidenceListResponse(BaseModel):
    items: list[EvidenceResponse]
    total: int
    page: int
    page_size: int


class EvidenceSummary(BaseModel):
    total: int
    by_type: dict[str, int]
    by_status: dict[str, int]
    expiring_soon: int
    pending_review: int


class EvidenceReviewRequest(BaseModel):
    decision: str  # APPROVE, REJECT, REQUEST_CHANGES
    comments: str | None = None
    completeness_score: int | None = Field(None, ge=1, le=5)
    relevance_score: int | None = Field(None, ge=1, le=5)
    quality_score: int | None = Field(None, ge=1, le=5)


@router.get("/summary", response_model=EvidenceSummary)
async def get_evidence_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get summary statistics for evidence."""
    result = await db.execute(
        select(Evidence).where(Evidence.tenant_id == tenant_id)
    )
    all_evidence = result.scalars().all()

    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    expiring_soon = 0
    pending_review = 0
    today = date.today()
    soon = today + timedelta(days=30)

    for e in all_evidence:
        # Type counts
        type_val = e.evidence_type if isinstance(e.evidence_type, str) else e.evidence_type.value
        by_type[type_val] = by_type.get(type_val, 0) + 1

        # Status counts
        status_val = e.status if isinstance(e.status, str) else e.status.value
        by_status[status_val] = by_status.get(status_val, 0) + 1

        # Expiring soon
        if e.valid_to and not e.is_perpetual and e.valid_to <= soon:
            expiring_soon += 1

        # Pending review
        if status_val == "PENDING_REVIEW":
            pending_review += 1

    return EvidenceSummary(
        total=len(all_evidence),
        by_type=by_type,
        by_status=by_status,
        expiring_soon=expiring_soon,
        pending_review=pending_review,
    )


@router.get("/", response_model=EvidenceListResponse)
async def list_evidence(
    evidence_type: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    control_id: UUID | None = Query(None),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List evidence with filtering and pagination."""
    query = select(Evidence).where(Evidence.tenant_id == tenant_id)

    if evidence_type:
        query = query.where(Evidence.evidence_type == evidence_type)
    if status_filter:
        query = query.where(Evidence.status == status_filter)
    if search:
        query = query.where(
            Evidence.title.ilike(f"%{search}%") | Evidence.evidence_ref.ilike(f"%{search}%")
        )

    # Count total
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    query = query.order_by(Evidence.collected_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    evidence_list = result.scalars().all()

    return EvidenceListResponse(
        items=evidence_list,
        total=total,
        page=page,
        page_size=page_size,
    )


@router.post("/", response_model=EvidenceResponse, status_code=status.HTTP_201_CREATED)
async def create_evidence(
    evidence: EvidenceCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
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
        collected_at=datetime.now(UTC),
    )
    db.add(db_evidence)

    if evidence.control_id:
        link = EvidenceLink(
            id=uuid4(),
            tenant_id=tenant_id,
            evidence_id=evidence_id,
            control_id=evidence.control_id,
            link_type="PRIMARY",
            linked_at=datetime.now(UTC),
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


@router.put("/{evidence_id}", response_model=EvidenceResponse)
async def update_evidence(
    evidence_id: UUID,
    data: EvidenceUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update evidence metadata."""
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(evidence, field, value)

    await db.commit()
    await db.refresh(evidence)
    return evidence


@router.delete("/{evidence_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_evidence(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Delete evidence."""
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    await db.delete(evidence)
    await db.commit()


@router.post("/{evidence_id}/review")
async def review_evidence(
    evidence_id: UUID,
    review_data: EvidenceReviewRequest,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Review evidence (approve/reject/request changes)."""
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    now = datetime.now(UTC)

    # Create review record
    review = EvidenceReview(
        id=uuid4(),
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        review_type="MANUAL",
        reviewer_id=current_user.id,
        reviewed_at=now,
        decision=review_data.decision,
        comments=review_data.comments,
        completeness_score=review_data.completeness_score,
        relevance_score=review_data.relevance_score,
        quality_score=review_data.quality_score,
    )
    db.add(review)

    # Update evidence status
    if review_data.decision == "APPROVE":
        evidence.status = EvidenceStatus.APPROVED
    elif review_data.decision == "REJECT":
        evidence.status = EvidenceStatus.REJECTED

    evidence.reviewed_at = now
    evidence.reviewed_by = current_user.id
    evidence.review_notes = review_data.comments

    await db.commit()
    return {
        "message": f"Evidence {review_data.decision.lower()}d",
        "evidence_id": str(evidence_id),
        "status": evidence.status.value if hasattr(evidence.status, 'value') else evidence.status,
    }


@router.post("/{evidence_id}/submit-for-review")
async def submit_for_review(
    evidence_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Submit evidence for review."""
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    evidence = result.scalar_one_or_none()
    if not evidence:
        raise HTTPException(status_code=404, detail="Evidence not found")

    evidence.status = EvidenceStatus.PENDING_REVIEW
    await db.commit()
    return {"message": "Evidence submitted for review", "evidence_id": str(evidence_id)}


@router.get("/expiring", response_model=list[EvidenceResponse])
async def get_expiring_evidence(
    days: int = Query(30, ge=1, le=365),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get evidence expiring within specified days."""
    today = date.today()
    expiry_threshold = today + timedelta(days=days)

    result = await db.execute(
        select(Evidence)
        .where(
            and_(
                Evidence.tenant_id == tenant_id,
                Evidence.valid_to <= expiry_threshold,
                Evidence.valid_to >= today,
                Evidence.is_perpetual == False,
            )
        )
        .order_by(Evidence.valid_to)
    )
    return result.scalars().all()


@router.get("/by-control/{control_id}", response_model=list[EvidenceResponse])
async def get_evidence_by_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get all evidence linked to a control."""
    result = await db.execute(
        select(Evidence)
        .join(EvidenceLink, Evidence.id == EvidenceLink.evidence_id)
        .where(
            and_(
                EvidenceLink.control_id == control_id,
                Evidence.tenant_id == tenant_id,
            )
        )
        .order_by(Evidence.collected_at.desc())
    )
    return result.scalars().all()


@router.post("/{evidence_id}/link-control")
async def link_evidence_to_control(
    evidence_id: UUID,
    control_id: UUID = Query(...),
    link_type: str = Query("PRIMARY"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Link evidence to a control."""
    # Verify evidence exists
    result = await db.execute(
        select(Evidence).where(and_(Evidence.id == evidence_id, Evidence.tenant_id == tenant_id))
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Evidence not found")

    link = EvidenceLink(
        id=uuid4(),
        tenant_id=tenant_id,
        evidence_id=evidence_id,
        control_id=control_id,
        link_type=link_type,
        linked_at=datetime.now(UTC),
        linked_by=current_user.id,
    )
    db.add(link)
    await db.commit()
    return {"message": "Evidence linked to control", "evidence_id": str(evidence_id), "control_id": str(control_id)}
