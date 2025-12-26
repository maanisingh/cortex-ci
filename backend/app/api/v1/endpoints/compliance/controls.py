"""Control Management API Endpoints"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, func
from pydantic import BaseModel

from app.core.database import get_db
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.framework import (
    Control, ControlMapping,
    Assessment, AssessmentStatus, AssessmentResult
)

router = APIRouter()

class ControlResponse(BaseModel):
    id: UUID
    control_id: str
    title: str
    framework_id: UUID
    implementation_status: Optional[str] = None

    class Config:
        from_attributes = True

class ControlUpdateSchema(BaseModel):
    implementation_status: Optional[str] = None
    implementation_notes: Optional[str] = None

class AssessmentCreate(BaseModel):
    control_id: UUID
    assessment_type: str = "SELF_ASSESSMENT"
    findings: Optional[str] = None
    result: str

class AssessmentResponse(BaseModel):
    id: UUID
    control_id: UUID
    assessment_type: str
    result: str
    assessed_at: datetime
    assessed_by: Optional[UUID]

    class Config:
        from_attributes = True

class ControlMappingCreate(BaseModel):
    source_control_id: UUID
    target_control_id: UUID
    relationship_type: str = "EQUIVALENT"
    notes: Optional[str] = None

@router.get("/", response_model=List[ControlResponse])
async def list_controls(
    framework_id: Optional[UUID] = Query(None),
    implementation_status: Optional[str] = Query(None),
    search: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Control).where(Control.tenant_id == tenant_id)
    if framework_id:
        query = query.where(Control.framework_id == framework_id)
    if implementation_status:
        query = query.where(Control.implementation_status == implementation_status)
    if search:
        query = query.where(
            Control.title.ilike(f"%{search}%") | Control.control_id.ilike(f"%{search}%")
        )
    result = await db.execute(
        query.order_by(Control.control_id).offset(skip).limit(limit)
    )
    return result.scalars().all()

@router.get("/{control_id}", response_model=ControlResponse)
async def get_control(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Control).where(and_(Control.id == control_id, Control.tenant_id == tenant_id))
    )
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")
    return control

@router.patch("/{control_id}")
async def update_control(
    control_id: UUID,
    update: ControlUpdateSchema,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Control).where(and_(Control.id == control_id, Control.tenant_id == tenant_id))
    )
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    if update.implementation_status:
        control.implementation_status = update.implementation_status
    if update.implementation_notes:
        control.implementation_notes = update.implementation_notes
    await db.commit()
    return {"message": "Control updated", "control_id": str(control_id)}

# Control Assessments
@router.get("/{control_id}/assessments", response_model=List[AssessmentResponse])
async def list_control_assessments(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Assessment).where(
            and_(Assessment.control_id == control_id, Assessment.tenant_id == tenant_id)
        ).order_by(Assessment.assessed_at.desc())
    )
    return result.scalars().all()

@router.post("/{control_id}/assessments", response_model=AssessmentResponse)
async def create_assessment(
    control_id: UUID,
    assessment: AssessmentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    db_assessment = Assessment(
        id=uuid4(),
        tenant_id=tenant_id,
        control_id=control_id,
        assessment_type=assessment.assessment_type,
        status=AssessmentStatus.COMPLETED,
        result=assessment.result,
        findings=assessment.findings,
        assessed_at=datetime.now(timezone.utc),
        assessed_by=current_user.id,
    )
    db.add(db_assessment)

    # Update control status based on assessment result
    control_result = await db.execute(
        select(Control).where(Control.id == control_id)
    )
    control = control_result.scalar_one_or_none()
    if control:
        if assessment.result == "PASS":
            control.implementation_status = "IMPLEMENTED"
        elif assessment.result == "FAIL":
            control.implementation_status = "NOT_IMPLEMENTED"
        elif assessment.result == "PARTIAL":
            control.implementation_status = "PARTIALLY_IMPLEMENTED"

    await db.commit()
    await db.refresh(db_assessment)
    return db_assessment

# Control Mappings
@router.get("/{control_id}/mappings")
async def get_control_mappings(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    # Get mappings where this control is the source
    source_result = await db.execute(
        select(ControlMapping).where(
            and_(ControlMapping.source_control_id == control_id, ControlMapping.tenant_id == tenant_id)
        )
    )
    # Get mappings where this control is the target
    target_result = await db.execute(
        select(ControlMapping).where(
            and_(ControlMapping.target_control_id == control_id, ControlMapping.tenant_id == tenant_id)
        )
    )

    return {
        "maps_to": [
            {
                "mapping_id": str(m.id),
                "target_control_id": str(m.target_control_id),
                "relationship": m.relationship_type,
            }
            for m in source_result.scalars().all()
        ],
        "mapped_from": [
            {
                "mapping_id": str(m.id),
                "source_control_id": str(m.source_control_id),
                "relationship": m.relationship_type,
            }
            for m in target_result.scalars().all()
        ],
    }

@router.post("/mappings")
async def create_control_mapping(
    mapping: ControlMappingCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    db_mapping = ControlMapping(
        id=uuid4(),
        tenant_id=tenant_id,
        source_control_id=mapping.source_control_id,
        target_control_id=mapping.target_control_id,
        relationship_type=mapping.relationship_type,
        notes=mapping.notes,
    )
    db.add(db_mapping)
    await db.commit()
    return {"message": "Control mapping created", "mapping_id": str(db_mapping.id)}

@router.delete("/mappings/{mapping_id}")
async def delete_control_mapping(
    mapping_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(ControlMapping).where(
            and_(ControlMapping.id == mapping_id, ControlMapping.tenant_id == tenant_id)
        )
    )
    mapping = result.scalar_one_or_none()
    if not mapping:
        raise HTTPException(status_code=404, detail="Mapping not found")

    await db.delete(mapping)
    await db.commit()
    return {"message": "Mapping deleted"}

# Statistics
@router.get("/stats/summary")
async def get_control_statistics(
    framework_id: Optional[UUID] = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get control implementation statistics"""
    base_query = select(Control).where(Control.tenant_id == tenant_id)
    if framework_id:
        base_query = base_query.where(Control.framework_id == framework_id)

    # Total controls
    total_result = await db.execute(
        select(func.count(Control.id)).where(Control.tenant_id == tenant_id)
    )
    total = total_result.scalar() or 0

    # By implementation status
    implemented = await db.execute(
        select(func.count(Control.id)).where(
            and_(Control.tenant_id == tenant_id, Control.implementation_status == "IMPLEMENTED")
        )
    )
    partially = await db.execute(
        select(func.count(Control.id)).where(
            and_(Control.tenant_id == tenant_id, Control.implementation_status == "PARTIALLY_IMPLEMENTED")
        )
    )
    not_impl = await db.execute(
        select(func.count(Control.id)).where(
            and_(Control.tenant_id == tenant_id, Control.implementation_status == "NOT_IMPLEMENTED")
        )
    )

    impl_count = implemented.scalar() or 0
    partial_count = partially.scalar() or 0
    not_impl_count = not_impl.scalar() or 0

    compliance_rate = (impl_count / total * 100) if total > 0 else 0

    return {
        "total_controls": total,
        "implemented": impl_count,
        "partially_implemented": partial_count,
        "not_implemented": not_impl_count,
        "not_assessed": total - impl_count - partial_count - not_impl_count,
        "compliance_rate": round(compliance_rate, 1),
    }

@router.get("/stats/by-framework")
async def get_stats_by_framework(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get control statistics grouped by framework"""
    from app.models.compliance.framework import Framework

    frameworks_result = await db.execute(
        select(Framework).where(Framework.tenant_id == tenant_id)
    )

    stats = []
    for framework in frameworks_result.scalars().all():
        total = await db.execute(
            select(func.count(Control.id)).where(
                and_(Control.tenant_id == tenant_id, Control.framework_id == framework.id)
            )
        )
        implemented = await db.execute(
            select(func.count(Control.id)).where(
                and_(
                    Control.tenant_id == tenant_id,
                    Control.framework_id == framework.id,
                    Control.implementation_status == "IMPLEMENTED"
                )
            )
        )

        total_count = total.scalar() or 0
        impl_count = implemented.scalar() or 0

        stats.append({
            "framework_id": str(framework.id),
            "framework_name": framework.name,
            "total_controls": total_count,
            "implemented": impl_count,
            "compliance_rate": round((impl_count / total_count * 100) if total_count > 0 else 0, 1),
        })

    return stats
