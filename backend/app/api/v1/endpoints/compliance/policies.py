"""Policy Management API Endpoints"""

from datetime import UTC, date, datetime
from typing import Any
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, Field
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.policy import (
    Policy,
    PolicyAcknowledgement,
    PolicyVersion,
    PolicyException,
    PolicyStatus,
    PolicyCategory,
    ExceptionStatus,
)

router = APIRouter()


class PolicyCreate(BaseModel):
    policy_number: str
    title: str
    category: str
    content: str
    summary: str | None = None
    purpose: str | None = None
    scope: str | None = None
    owner_department: str | None = None
    requires_acknowledgement: bool = True
    review_frequency_months: int = 12
    tags: list[str] | None = None


class PolicyUpdate(BaseModel):
    title: str | None = None
    category: str | None = None
    content: str | None = None
    summary: str | None = None
    purpose: str | None = None
    scope: str | None = None
    owner_department: str | None = None
    requires_acknowledgement: bool | None = None
    review_frequency_months: int | None = None
    review_date: date | None = None
    tags: list[str] | None = None


class PolicyResponse(BaseModel):
    id: UUID
    policy_number: str
    title: str
    category: str
    status: str
    current_version: str
    summary: str | None = None
    purpose: str | None = None
    scope: str | None = None
    content: str | None = None
    owner_department: str | None = None
    requires_acknowledgement: bool
    review_frequency_months: int
    effective_date: date | None = None
    review_date: date | None = None
    tags: list[str] | None = None
    created_at: datetime | None = None
    updated_at: datetime | None = None

    class Config:
        from_attributes = True


class PolicyListResponse(BaseModel):
    items: list[PolicyResponse]
    total: int
    page: int
    page_size: int
    pages: int


class PolicySummary(BaseModel):
    total: int
    by_status: dict[str, int]
    by_category: dict[str, int]
    pending_review: int
    requires_acknowledgement: int


# Version schemas
class PolicyVersionCreate(BaseModel):
    change_summary: str
    version_type: str = "MINOR"  # MAJOR, MINOR, PATCH
    content: str | None = None


class PolicyVersionResponse(BaseModel):
    id: UUID
    policy_id: UUID
    version_number: str
    version_type: str
    content: str
    change_summary: str | None = None
    created_by: UUID | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    is_current: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


# Acknowledgement schemas
class AcknowledgementResponse(BaseModel):
    id: UUID
    policy_id: UUID
    user_id: UUID
    policy_version: str
    acknowledged_at: datetime
    is_verified: bool
    is_expired: bool
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


class AcknowledgementStats(BaseModel):
    total_required: int
    total_acknowledged: int
    pending: int
    expired: int
    compliance_rate: float


# Exception schemas
class ExceptionCreate(BaseModel):
    title: str
    justification: str
    scope: str
    risk_description: str | None = None
    compensating_controls: str | None = None
    department: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    is_permanent: bool = False


class ExceptionUpdate(BaseModel):
    title: str | None = None
    justification: str | None = None
    scope: str | None = None
    risk_description: str | None = None
    compensating_controls: str | None = None
    residual_risk: str | None = None


class ExceptionResponse(BaseModel):
    id: UUID
    policy_id: UUID
    title: str
    justification: str
    scope: str
    risk_description: str | None = None
    compensating_controls: str | None = None
    residual_risk: str | None = None
    requested_by: UUID
    requested_at: datetime
    department: str | None = None
    status: str
    reviewed_by: UUID | None = None
    reviewed_at: datetime | None = None
    review_notes: str | None = None
    approved_by: UUID | None = None
    approved_at: datetime | None = None
    approval_notes: str | None = None
    effective_from: date | None = None
    effective_to: date | None = None
    is_permanent: bool
    created_at: datetime | None = None

    class Config:
        from_attributes = True


@router.get("/summary", response_model=PolicySummary)
async def get_policy_summary(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get summary statistics for policies."""
    result = await db.execute(
        select(Policy).where(Policy.tenant_id == tenant_id)
    )
    policies = result.scalars().all()

    by_status: dict[str, int] = {}
    by_category: dict[str, int] = {}
    pending_review = 0
    requires_ack = 0
    today = date.today()

    for p in policies:
        # Status counts
        status_val = p.status if isinstance(p.status, str) else p.status.value
        by_status[status_val] = by_status.get(status_val, 0) + 1

        # Category counts
        cat_val = p.category if isinstance(p.category, str) else p.category
        by_category[cat_val] = by_category.get(cat_val, 0) + 1

        # Pending review
        if p.review_date and p.review_date <= today:
            pending_review += 1

        # Requires acknowledgement
        if p.requires_acknowledgement:
            requires_ack += 1

    return PolicySummary(
        total=len(policies),
        by_status=by_status,
        by_category=by_category,
        pending_review=pending_review,
        requires_acknowledgement=requires_ack,
    )


@router.get("/", response_model=PolicyListResponse)
async def list_policies(
    category: str | None = Query(None),
    status_filter: str | None = Query(None, alias="status"),
    search: str | None = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List policies with filtering and pagination."""
    query = select(Policy).where(Policy.tenant_id == tenant_id)

    if category:
        query = query.where(Policy.category == category)
    if status_filter:
        query = query.where(Policy.status == status_filter)
    if search:
        query = query.where(
            Policy.title.ilike(f"%{search}%") | Policy.policy_number.ilike(f"%{search}%")
        )

    # Count total
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    query = query.order_by(Policy.policy_number)
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    policies = result.scalars().all()

    return PolicyListResponse(
        items=policies,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size if total > 0 else 0,
    )


@router.post("/", response_model=PolicyResponse, status_code=status.HTTP_201_CREATED)
async def create_policy(
    policy: PolicyCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    db_policy = Policy(
        id=uuid4(),
        tenant_id=tenant_id,
        policy_number=policy.policy_number,
        title=policy.title,
        category=policy.category,
        content=policy.content,
        summary=policy.summary,
        status=PolicyStatus.DRAFT,
        current_version="1.0",
        requires_acknowledgement=policy.requires_acknowledgement,
    )
    db.add(db_policy)
    await db.commit()
    await db.refresh(db_policy)
    return db_policy


@router.get("/{policy_id}", response_model=PolicyResponse)
async def get_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")
    return policy


@router.post("/{policy_id}/acknowledge")
async def acknowledge_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    ack = PolicyAcknowledgement(
        id=uuid4(),
        tenant_id=tenant_id,
        policy_id=policy_id,
        user_id=current_user.id,
        policy_version=policy.current_version,
        acknowledged_at=datetime.now(UTC),
    )
    db.add(ack)
    await db.commit()
    return {"message": "Policy acknowledged", "policy_id": str(policy_id)}


@router.put("/{policy_id}", response_model=PolicyResponse)
async def update_policy(
    policy_id: UUID,
    data: PolicyUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update a policy."""
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(policy, field, value)

    await db.commit()
    await db.refresh(policy)
    return policy


@router.delete("/{policy_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Delete a policy."""
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    await db.delete(policy)
    await db.commit()


@router.patch("/{policy_id}/publish")
async def publish_policy(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Publish a policy."""
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    policy.status = PolicyStatus.PUBLISHED
    policy.effective_date = date.today()
    await db.commit()
    return {"message": "Policy published", "policy_id": str(policy_id)}


@router.patch("/{policy_id}/status")
async def update_policy_status(
    policy_id: UUID,
    new_status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update policy status."""
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    try:
        policy.status = PolicyStatus(new_status)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid status: {new_status}")

    if new_status == PolicyStatus.PUBLISHED.value:
        policy.effective_date = date.today()

    await db.commit()
    return {"message": f"Policy status updated to {new_status}", "policy_id": str(policy_id)}


# ==================== VERSION CONTROL ENDPOINTS ====================

@router.get("/{policy_id}/versions", response_model=list[PolicyVersionResponse])
async def list_policy_versions(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List all versions of a policy."""
    # Verify policy exists
    policy_result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    if not policy_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Policy not found")

    result = await db.execute(
        select(PolicyVersion)
        .where(and_(PolicyVersion.policy_id == policy_id, PolicyVersion.tenant_id == tenant_id))
        .order_by(PolicyVersion.created_at.desc())
    )
    return result.scalars().all()


@router.post("/{policy_id}/versions", response_model=PolicyVersionResponse, status_code=status.HTTP_201_CREATED)
async def create_policy_version(
    policy_id: UUID,
    version_data: PolicyVersionCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create a new version of a policy."""
    result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Calculate new version number
    current_version = policy.current_version
    parts = current_version.split(".")
    major, minor = int(parts[0]), int(parts[1]) if len(parts) > 1 else 0

    if version_data.version_type == "MAJOR":
        new_version = f"{major + 1}.0"
    elif version_data.version_type == "MINOR":
        new_version = f"{major}.{minor + 1}"
    else:  # PATCH
        patch = int(parts[2]) if len(parts) > 2 else 0
        new_version = f"{major}.{minor}.{patch + 1}"

    # Mark old versions as not current
    await db.execute(
        select(PolicyVersion)
        .where(and_(PolicyVersion.policy_id == policy_id, PolicyVersion.is_current == True))
    )
    old_versions = (await db.execute(
        select(PolicyVersion).where(and_(PolicyVersion.policy_id == policy_id, PolicyVersion.is_current == True))
    )).scalars().all()
    for old_v in old_versions:
        old_v.is_current = False
        old_v.effective_to = date.today()

    # Create new version
    new_policy_version = PolicyVersion(
        id=uuid4(),
        tenant_id=tenant_id,
        policy_id=policy_id,
        version_number=new_version,
        version_type=version_data.version_type,
        content=version_data.content or policy.content,
        change_summary=version_data.change_summary,
        created_by=current_user.id,
        effective_from=date.today(),
        is_current=True,
    )
    db.add(new_policy_version)

    # Update policy's current version and content
    policy.current_version = new_version
    if version_data.content:
        policy.content = version_data.content

    await db.commit()
    await db.refresh(new_policy_version)
    return new_policy_version


@router.get("/{policy_id}/versions/{version_id}", response_model=PolicyVersionResponse)
async def get_policy_version(
    policy_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get a specific version of a policy."""
    result = await db.execute(
        select(PolicyVersion).where(
            and_(
                PolicyVersion.id == version_id,
                PolicyVersion.policy_id == policy_id,
                PolicyVersion.tenant_id == tenant_id
            )
        )
    )
    version = result.scalar_one_or_none()
    if not version:
        raise HTTPException(status_code=404, detail="Policy version not found")
    return version


# ==================== ACKNOWLEDGEMENT ENDPOINTS ====================

@router.get("/{policy_id}/acknowledgements", response_model=list[AcknowledgementResponse])
async def list_policy_acknowledgements(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List all acknowledgements for a policy."""
    result = await db.execute(
        select(PolicyAcknowledgement)
        .where(and_(PolicyAcknowledgement.policy_id == policy_id, PolicyAcknowledgement.tenant_id == tenant_id))
        .order_by(PolicyAcknowledgement.acknowledged_at.desc())
    )
    return result.scalars().all()


@router.get("/{policy_id}/acknowledgements/stats", response_model=AcknowledgementStats)
async def get_acknowledgement_stats(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get acknowledgement statistics for a policy."""
    # Get policy
    policy_result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    policy = policy_result.scalar_one_or_none()
    if not policy:
        raise HTTPException(status_code=404, detail="Policy not found")

    # Get acknowledgements
    ack_result = await db.execute(
        select(PolicyAcknowledgement).where(
            and_(PolicyAcknowledgement.policy_id == policy_id, PolicyAcknowledgement.tenant_id == tenant_id)
        )
    )
    acknowledgements = ack_result.scalars().all()

    # Calculate stats (simplified - in real app, would check against user count)
    total_acked = len(acknowledgements)
    expired = sum(1 for a in acknowledgements if a.is_expired)

    # For now, use acknowledged count as total required (would come from user count in real app)
    total_required = max(total_acked, 1)

    return AcknowledgementStats(
        total_required=total_required,
        total_acknowledged=total_acked,
        pending=total_required - total_acked,
        expired=expired,
        compliance_rate=round((total_acked / total_required) * 100, 1) if total_required > 0 else 0,
    )


@router.get("/{policy_id}/acknowledgements/my-status")
async def get_my_acknowledgement_status(
    policy_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Check if the current user has acknowledged the policy."""
    result = await db.execute(
        select(PolicyAcknowledgement).where(
            and_(
                PolicyAcknowledgement.policy_id == policy_id,
                PolicyAcknowledgement.user_id == current_user.id,
                PolicyAcknowledgement.tenant_id == tenant_id
            )
        ).order_by(PolicyAcknowledgement.acknowledged_at.desc())
    )
    ack = result.scalar_one_or_none()

    if not ack:
        return {"acknowledged": False, "acknowledgement": None}

    return {
        "acknowledged": True,
        "is_current": not ack.is_expired,
        "acknowledgement": AcknowledgementResponse.model_validate(ack),
    }


# ==================== EXCEPTION ENDPOINTS ====================

@router.get("/{policy_id}/exceptions", response_model=list[ExceptionResponse])
async def list_policy_exceptions(
    policy_id: UUID,
    status_filter: str | None = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List all exceptions for a policy."""
    query = select(PolicyException).where(
        and_(PolicyException.policy_id == policy_id, PolicyException.tenant_id == tenant_id)
    )
    if status_filter:
        query = query.where(PolicyException.status == status_filter)

    query = query.order_by(PolicyException.requested_at.desc())
    result = await db.execute(query)
    return result.scalars().all()


@router.post("/{policy_id}/exceptions", response_model=ExceptionResponse, status_code=status.HTTP_201_CREATED)
async def create_policy_exception(
    policy_id: UUID,
    exception_data: ExceptionCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Request a policy exception."""
    # Verify policy exists
    policy_result = await db.execute(
        select(Policy).where(and_(Policy.id == policy_id, Policy.tenant_id == tenant_id))
    )
    if not policy_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Policy not found")

    exception = PolicyException(
        id=uuid4(),
        tenant_id=tenant_id,
        policy_id=policy_id,
        title=exception_data.title,
        justification=exception_data.justification,
        scope=exception_data.scope,
        risk_description=exception_data.risk_description,
        compensating_controls=exception_data.compensating_controls,
        department=exception_data.department,
        requested_by=current_user.id,
        requested_at=datetime.now(UTC),
        status=ExceptionStatus.PENDING,
        effective_from=exception_data.effective_from,
        effective_to=exception_data.effective_to,
        is_permanent=exception_data.is_permanent,
    )
    db.add(exception)
    await db.commit()
    await db.refresh(exception)
    return exception


@router.get("/{policy_id}/exceptions/{exception_id}", response_model=ExceptionResponse)
async def get_policy_exception(
    policy_id: UUID,
    exception_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get a specific policy exception."""
    result = await db.execute(
        select(PolicyException).where(
            and_(
                PolicyException.id == exception_id,
                PolicyException.policy_id == policy_id,
                PolicyException.tenant_id == tenant_id
            )
        )
    )
    exception = result.scalar_one_or_none()
    if not exception:
        raise HTTPException(status_code=404, detail="Policy exception not found")
    return exception


@router.put("/{policy_id}/exceptions/{exception_id}", response_model=ExceptionResponse)
async def update_policy_exception(
    policy_id: UUID,
    exception_id: UUID,
    data: ExceptionUpdate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Update a policy exception."""
    result = await db.execute(
        select(PolicyException).where(
            and_(
                PolicyException.id == exception_id,
                PolicyException.policy_id == policy_id,
                PolicyException.tenant_id == tenant_id
            )
        )
    )
    exception = result.scalar_one_or_none()
    if not exception:
        raise HTTPException(status_code=404, detail="Policy exception not found")

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(exception, field, value)

    await db.commit()
    await db.refresh(exception)
    return exception


@router.patch("/{policy_id}/exceptions/{exception_id}/review")
async def review_policy_exception(
    policy_id: UUID,
    exception_id: UUID,
    action: str = Query(..., regex="^(approve|deny)$"),
    notes: str = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Review (approve/deny) a policy exception."""
    result = await db.execute(
        select(PolicyException).where(
            and_(
                PolicyException.id == exception_id,
                PolicyException.policy_id == policy_id,
                PolicyException.tenant_id == tenant_id
            )
        )
    )
    exception = result.scalar_one_or_none()
    if not exception:
        raise HTTPException(status_code=404, detail="Policy exception not found")

    if exception.status != ExceptionStatus.PENDING:
        raise HTTPException(status_code=400, detail="Exception is not in pending status")

    now = datetime.now(UTC)
    exception.reviewed_by = current_user.id
    exception.reviewed_at = now
    exception.review_notes = notes

    if action == "approve":
        exception.status = ExceptionStatus.APPROVED
        exception.approved_by = current_user.id
        exception.approved_at = now
        exception.approval_notes = notes
    else:
        exception.status = ExceptionStatus.DENIED

    await db.commit()
    return {
        "message": f"Exception {action}d",
        "exception_id": str(exception_id),
        "status": exception.status.value if hasattr(exception.status, 'value') else exception.status,
    }
