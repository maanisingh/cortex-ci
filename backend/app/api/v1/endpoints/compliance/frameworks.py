"""
Regulatory Framework API Endpoints
Manage compliance frameworks (NIST, ISO, SOC2, etc.) and their controls
"""
from uuid import UUID
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from pydantic import BaseModel, Field
from datetime import date

from app.core.database import get_db
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.framework import (
    Framework, FrameworkType, Control, ControlMapping,
    Assessment, AssessmentStatus, AssessmentResult
)

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class FrameworkCreate(BaseModel):
    type: str = Field(..., description="Framework type (NIST_800_53, ISO_27001, etc.)")
    name: str = Field(..., max_length=255)
    version: str = Field(..., max_length=50)
    description: Optional[str] = None
    source_url: Optional[str] = None
    publisher: Optional[str] = None


class FrameworkResponse(BaseModel):
    id: UUID
    type: str
    name: str
    version: str
    description: Optional[str]
    source_url: Optional[str]
    publisher: Optional[str]
    total_controls: int
    is_active: bool

    class Config:
        from_attributes = True


class ControlResponse(BaseModel):
    id: UUID
    framework_id: UUID
    control_id: str
    title: str
    description: str
    family: Optional[str]
    category: Optional[str]
    baseline_impact: Optional[str]
    implementation_status: str
    guidance: Optional[str]

    class Config:
        from_attributes = True


class ControlMappingResponse(BaseModel):
    id: UUID
    source_control_id: UUID
    target_control_id: UUID
    relationship_type: str
    confidence: float

    class Config:
        from_attributes = True


class GapAnalysisResponse(BaseModel):
    framework_id: UUID
    framework_name: str
    total_controls: int
    implemented: int
    partially_implemented: int
    not_implemented: int
    not_applicable: int
    not_assessed: int
    compliance_percentage: float
    gaps: List[dict]


# ============================================================================
# FRAMEWORK ENDPOINTS
# ============================================================================

@router.get("/", response_model=List[FrameworkResponse])
async def list_frameworks(
    type: Optional[str] = Query(None, description="Filter by framework type"),
    is_active: bool = Query(True, description="Filter by active status"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List all regulatory frameworks."""
    query = select(Framework).where(
        and_(Framework.tenant_id == tenant_id, Framework.is_active == is_active)
    )
    if type:
        query = query.where(Framework.type == type)

    result = await db.execute(query.order_by(Framework.name))
    frameworks = result.scalars().all()
    return frameworks


@router.get("/{framework_id}", response_model=FrameworkResponse)
async def get_framework(
    framework_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get a specific framework."""
    result = await db.execute(
        select(Framework).where(
            and_(Framework.id == framework_id, Framework.tenant_id == tenant_id)
        )
    )
    framework = result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")
    return framework


@router.get("/{framework_id}/controls", response_model=List[ControlResponse])
async def get_framework_controls(
    framework_id: UUID,
    family: Optional[str] = Query(None, description="Filter by control family"),
    status: Optional[str] = Query(None, description="Filter by implementation status"),
    search: Optional[str] = Query(None, description="Search in title/description"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get all controls for a framework."""
    query = select(Control).where(
        and_(Control.framework_id == framework_id, Control.tenant_id == tenant_id)
    )

    if family:
        query = query.where(Control.family == family)
    if status:
        query = query.where(Control.implementation_status == status)
    if search:
        query = query.where(
            Control.title.ilike(f"%{search}%") | Control.description.ilike(f"%{search}%")
        )

    result = await db.execute(query.order_by(Control.control_id).offset(skip).limit(limit))
    controls = result.scalars().all()
    return controls


@router.get("/{framework_id}/gap-analysis", response_model=GapAnalysisResponse)
async def get_gap_analysis(
    framework_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get gap analysis for a framework."""
    # Get framework
    result = await db.execute(
        select(Framework).where(
            and_(Framework.id == framework_id, Framework.tenant_id == tenant_id)
        )
    )
    framework = result.scalar_one_or_none()
    if not framework:
        raise HTTPException(status_code=404, detail="Framework not found")

    # Get control counts by status
    status_counts = await db.execute(
        select(
            Control.implementation_status,
            func.count(Control.id).label("count")
        ).where(
            and_(Control.framework_id == framework_id, Control.tenant_id == tenant_id)
        ).group_by(Control.implementation_status)
    )

    counts = {row[0]: row[1] for row in status_counts.fetchall()}

    implemented = counts.get("FULLY_IMPLEMENTED", 0)
    partial = counts.get("PARTIALLY_IMPLEMENTED", 0)
    not_impl = counts.get("NOT_IMPLEMENTED", 0)
    not_app = counts.get("NOT_APPLICABLE", 0)
    not_assessed = counts.get("NOT_ASSESSED", 0)

    total = implemented + partial + not_impl + not_app + not_assessed
    applicable = total - not_app

    compliance_pct = (implemented + (partial * 0.5)) / applicable * 100 if applicable > 0 else 0

    # Get gaps (not implemented or partially implemented controls)
    gaps_result = await db.execute(
        select(Control).where(
            and_(
                Control.framework_id == framework_id,
                Control.tenant_id == tenant_id,
                Control.implementation_status.in_(["NOT_IMPLEMENTED", "PARTIALLY_IMPLEMENTED"])
            )
        ).order_by(Control.control_id).limit(50)
    )
    gaps = [
        {"control_id": c.control_id, "title": c.title, "status": c.implementation_status}
        for c in gaps_result.scalars().all()
    ]

    return GapAnalysisResponse(
        framework_id=framework_id,
        framework_name=framework.name,
        total_controls=total,
        implemented=implemented,
        partially_implemented=partial,
        not_implemented=not_impl,
        not_applicable=not_app,
        not_assessed=not_assessed,
        compliance_percentage=round(compliance_pct, 2),
        gaps=gaps
    )


@router.patch("/controls/{control_id}/status")
async def update_control_status(
    control_id: UUID,
    status: str = Query(..., description="New implementation status"),
    notes: Optional[str] = Query(None, description="Implementation notes"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    """Update control implementation status."""
    result = await db.execute(
        select(Control).where(
            and_(Control.id == control_id, Control.tenant_id == tenant_id)
        )
    )
    control = result.scalar_one_or_none()
    if not control:
        raise HTTPException(status_code=404, detail="Control not found")

    valid_statuses = ["NOT_ASSESSED", "FULLY_IMPLEMENTED", "PARTIALLY_IMPLEMENTED",
                      "NOT_IMPLEMENTED", "NOT_APPLICABLE", "PLANNED"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}")

    control.implementation_status = status
    if notes:
        control.implementation_notes = notes

    await db.commit()
    return {"message": "Control status updated", "control_id": str(control_id), "new_status": status}


@router.get("/controls/{control_id}/mappings", response_model=List[ControlMappingResponse])
async def get_control_mappings(
    control_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get cross-framework mappings for a control."""
    result = await db.execute(
        select(ControlMapping).where(
            and_(
                ControlMapping.tenant_id == tenant_id,
                (ControlMapping.source_control_id == control_id) |
                (ControlMapping.target_control_id == control_id)
            )
        )
    )
    mappings = result.scalars().all()
    return mappings


@router.get("/types")
async def list_framework_types():
    """List all supported framework types."""
    return {
        "types": [
            {"code": "NIST_800_53", "name": "NIST SP 800-53", "description": "Security and Privacy Controls"},
            {"code": "NIST_CSF", "name": "NIST Cybersecurity Framework", "description": "Cybersecurity Framework"},
            {"code": "ISO_27001", "name": "ISO/IEC 27001", "description": "Information Security Management"},
            {"code": "SOC_2", "name": "SOC 2", "description": "Trust Services Criteria"},
            {"code": "PCI_DSS", "name": "PCI-DSS", "description": "Payment Card Industry Data Security"},
            {"code": "HIPAA", "name": "HIPAA", "description": "Health Insurance Portability and Accountability"},
            {"code": "GDPR", "name": "GDPR", "description": "General Data Protection Regulation"},
            {"code": "CIS_CONTROLS", "name": "CIS Controls", "description": "Critical Security Controls"},
            {"code": "MITRE_ATTACK", "name": "MITRE ATT&CK", "description": "Adversarial Tactics and Techniques"},
            {"code": "CMMC", "name": "CMMC", "description": "Cybersecurity Maturity Model Certification"},
            {"code": "FEDRAMP", "name": "FedRAMP", "description": "Federal Risk and Authorization Management"},
        ]
    }
