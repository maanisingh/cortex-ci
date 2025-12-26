"""Policy Management API Endpoints"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone, date
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.policy import Policy, PolicyStatus, PolicyVersion, PolicyAcknowledgement

router = APIRouter()

class PolicyCreate(BaseModel):
    policy_number: str
    title: str
    category: str
    content: str
    summary: Optional[str] = None
    requires_acknowledgement: bool = True

class PolicyResponse(BaseModel):
    id: UUID
    policy_number: str
    title: str
    category: str
    status: str
    current_version: str
    requires_acknowledgement: bool
    effective_date: Optional[date]

    class Config:
        from_attributes = True

@router.get("/", response_model=List[PolicyResponse])
async def list_policies(
    category: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Policy).where(Policy.tenant_id == tenant_id)
    if category:
        query = query.where(Policy.category == category)
    if status:
        query = query.where(Policy.status == status)
    result = await db.execute(query.order_by(Policy.policy_number))
    return result.scalars().all()

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
    current_user = Depends(get_current_user),
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
        acknowledged_at=datetime.now(timezone.utc),
    )
    db.add(ack)
    await db.commit()
    return {"message": "Policy acknowledged", "policy_id": str(policy_id)}

@router.patch("/{policy_id}/publish")
async def publish_policy(
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

    policy.status = PolicyStatus.PUBLISHED
    policy.effective_date = date.today()
    await db.commit()
    return {"message": "Policy published", "policy_id": str(policy_id)}
