"""Vendor Risk Management API Endpoints"""

from datetime import UTC
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id
from app.core.database import get_db
from app.models.compliance.vendor import Vendor, VendorAssessment, VendorStatus

router = APIRouter()


class VendorCreate(BaseModel):
    legal_name: str
    tier: str
    category: str
    country: str | None = None
    services_provided: list[str] = []
    has_data_access: bool = False


class VendorResponse(BaseModel):
    id: UUID
    vendor_ref: str
    legal_name: str
    tier: str
    status: str
    category: str
    risk_score: float
    has_data_access: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=list[VendorResponse])
async def list_vendors(
    tier: str | None = Query(None),
    status: str | None = Query(None),
    category: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Vendor).where(Vendor.tenant_id == tenant_id)
    if tier:
        query = query.where(Vendor.tier == tier)
    if status:
        query = query.where(Vendor.status == status)
    if category:
        query = query.where(Vendor.category == category)
    result = await db.execute(query.order_by(Vendor.legal_name))
    return result.scalars().all()


@router.post("/", response_model=VendorResponse, status_code=status.HTTP_201_CREATED)
async def create_vendor(
    vendor: VendorCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    vendor_id = uuid4()
    db_vendor = Vendor(
        id=vendor_id,
        tenant_id=tenant_id,
        vendor_ref=f"VND-{str(vendor_id)[:8].upper()}",
        legal_name=vendor.legal_name,
        tier=vendor.tier,
        category=vendor.category,
        country=vendor.country,
        services_provided=vendor.services_provided,
        has_data_access=vendor.has_data_access,
        status=VendorStatus.PROSPECTIVE,
        risk_score=50.0,
    )
    db.add(db_vendor)
    await db.commit()
    await db.refresh(db_vendor)
    return db_vendor


@router.get("/{vendor_id}", response_model=VendorResponse)
async def get_vendor(
    vendor_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Vendor).where(and_(Vendor.id == vendor_id, Vendor.tenant_id == tenant_id))
    )
    vendor = result.scalar_one_or_none()
    if not vendor:
        raise HTTPException(status_code=404, detail="Vendor not found")
    return vendor


@router.post("/{vendor_id}/assess")
async def create_vendor_assessment(
    vendor_id: UUID,
    assessment_type: str = Query("INITIAL"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    from datetime import datetime

    assessment = VendorAssessment(
        id=uuid4(),
        tenant_id=tenant_id,
        vendor_id=vendor_id,
        assessment_type=assessment_type,
        status="IN_PROGRESS",
        initiated_at=datetime.now(UTC),
    )
    db.add(assessment)
    await db.commit()
    return {"message": "Assessment initiated", "assessment_id": str(assessment.id)}
