"""Compliance Scoring API Endpoints"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id
from app.core.database import get_db
from app.models.compliance.framework import Control, Framework

router = APIRouter()


# ============================================================
# Response Schemas
# ============================================================


class FrameworkScore(BaseModel):
    """Score for a single framework."""

    framework_id: str
    framework_name: str
    framework_type: str
    total_controls: int
    implemented: int
    partially_implemented: int
    not_implemented: int
    not_assessed: int
    score: float
    grade: str

    class Config:
        from_attributes = True


class OverallScore(BaseModel):
    """Overall compliance score."""

    overall_score: float
    overall_grade: str
    total_frameworks: int
    total_controls: int
    implemented: int
    partially_implemented: int
    not_implemented: int
    not_assessed: int
    frameworks: list[FrameworkScore]
    trend: dict | None = None


class GapItem(BaseModel):
    """A compliance gap item."""

    control_id: str
    control_title: str
    framework_id: str
    framework_name: str
    category: str
    status: str
    priority: int
    severity: str


class GapAnalysis(BaseModel):
    """Gap analysis response."""

    total_gaps: int
    critical: list[GapItem]
    high: list[GapItem]
    medium: list[GapItem]
    low: list[GapItem]


class FrameworkMapping(BaseModel):
    """Cross-framework control mapping."""

    source_framework: str
    target_framework: str
    mapped_controls: int
    efficiency_score: float


# ============================================================
# Helper Functions
# ============================================================


def calculate_grade(score: float) -> str:
    """Convert numeric score to letter grade."""
    if score >= 90:
        return "A"
    elif score >= 80:
        return "B"
    elif score >= 70:
        return "C"
    elif score >= 60:
        return "D"
    else:
        return "F"


def calculate_severity(priority: int, status: str) -> str:
    """Calculate gap severity based on priority and status."""
    if priority == 1 and status == "NOT_IMPLEMENTED":
        return "CRITICAL"
    elif priority == 1 or (priority == 2 and status == "NOT_IMPLEMENTED"):
        return "HIGH"
    elif priority == 2:
        return "MEDIUM"
    else:
        return "LOW"


# ============================================================
# Endpoints
# ============================================================


@router.get("/score", response_model=OverallScore)
async def get_compliance_score(
    framework_id: UUID | None = Query(None, description="Filter by framework"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """
    Get overall compliance score and per-framework breakdown.

    Returns real-time compliance percentage based on control implementation status.
    """
    # Get all frameworks for tenant
    frameworks_query = select(Framework).where(
        Framework.tenant_id == tenant_id, Framework.is_active == True
    )
    if framework_id:
        frameworks_query = frameworks_query.where(Framework.id == framework_id)

    result = await db.execute(frameworks_query.order_by(Framework.name))
    frameworks = result.scalars().all()

    framework_scores = []
    total_implemented = 0
    total_partial = 0
    total_not_impl = 0
    total_not_assessed = 0
    total_controls = 0

    for fw in frameworks:
        # Count controls by implementation status
        impl_count = await db.execute(
            select(func.count(Control.id)).where(
                and_(
                    Control.framework_id == fw.id,
                    Control.tenant_id == tenant_id,
                    Control.implementation_status == "FULLY_IMPLEMENTED",
                )
            )
        )
        implemented = impl_count.scalar() or 0

        partial_count = await db.execute(
            select(func.count(Control.id)).where(
                and_(
                    Control.framework_id == fw.id,
                    Control.tenant_id == tenant_id,
                    Control.implementation_status == "PARTIALLY_IMPLEMENTED",
                )
            )
        )
        partially = partial_count.scalar() or 0

        not_impl_count = await db.execute(
            select(func.count(Control.id)).where(
                and_(
                    Control.framework_id == fw.id,
                    Control.tenant_id == tenant_id,
                    Control.implementation_status == "NOT_IMPLEMENTED",
                )
            )
        )
        not_impl = not_impl_count.scalar() or 0

        total_count = await db.execute(
            select(func.count(Control.id)).where(
                and_(Control.framework_id == fw.id, Control.tenant_id == tenant_id)
            )
        )
        fw_total = total_count.scalar() or 0
        not_assessed = fw_total - implemented - partially - not_impl

        # Calculate score (fully = 100%, partial = 50%, not implemented = 0%)
        if fw_total > 0:
            score = ((implemented * 100) + (partially * 50)) / fw_total
        else:
            score = 0.0

        framework_scores.append(
            FrameworkScore(
                framework_id=str(fw.id),
                framework_name=fw.name,
                framework_type=fw.type.value
                if hasattr(fw.type, "value")
                else (fw.type or "CUSTOM"),
                total_controls=fw_total,
                implemented=implemented,
                partially_implemented=partially,
                not_implemented=not_impl,
                not_assessed=not_assessed,
                score=round(score, 1),
                grade=calculate_grade(score),
            )
        )

        # Accumulate totals
        total_implemented += implemented
        total_partial += partially
        total_not_impl += not_impl
        total_not_assessed += not_assessed
        total_controls += fw_total

    # Calculate overall score
    if total_controls > 0:
        overall = ((total_implemented * 100) + (total_partial * 50)) / total_controls
    else:
        overall = 0.0

    return OverallScore(
        overall_score=round(overall, 1),
        overall_grade=calculate_grade(overall),
        total_frameworks=len(frameworks),
        total_controls=total_controls,
        implemented=total_implemented,
        partially_implemented=total_partial,
        not_implemented=total_not_impl,
        not_assessed=total_not_assessed,
        frameworks=framework_scores,
        trend={"direction": "up" if overall > 50 else "down", "change": 0.0, "period": "30d"},
    )


@router.get("/gaps", response_model=GapAnalysis)
async def get_compliance_gaps(
    framework_id: UUID | None = Query(None, description="Filter by framework"),
    severity: str | None = Query(
        None, description="Filter by severity: CRITICAL, HIGH, MEDIUM, LOW"
    ),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """
    Get compliance gaps - controls that are not fully implemented.

    Returns gaps categorized by severity (CRITICAL, HIGH, MEDIUM, LOW).
    """
    # Query controls that are NOT fully implemented
    query = (
        select(Control, Framework)
        .join(Framework, Control.framework_id == Framework.id)
        .where(
            and_(
                Control.tenant_id == tenant_id, Control.implementation_status != "FULLY_IMPLEMENTED"
            )
        )
    )

    if framework_id:
        query = query.where(Control.framework_id == framework_id)

    result = await db.execute(query.order_by(Control.priority, Control.control_id).limit(limit * 4))
    rows = result.all()

    critical = []
    high = []
    medium = []
    low = []

    for control, framework in rows:
        gap_severity = calculate_severity(
            control.priority or 2, control.implementation_status or "NOT_ASSESSED"
        )

        # Filter by severity if specified
        if severity and gap_severity != severity.upper():
            continue

        gap = GapItem(
            control_id=control.control_id,
            control_title=control.title,
            framework_id=str(framework.id),
            framework_name=framework.name,
            category=control.category.value
            if hasattr(control.category, "value")
            else (control.category or "UNKNOWN"),
            status=control.implementation_status or "NOT_ASSESSED",
            priority=control.priority or 2,
            severity=gap_severity,
        )

        if gap_severity == "CRITICAL":
            if len(critical) < limit:
                critical.append(gap)
        elif gap_severity == "HIGH":
            if len(high) < limit:
                high.append(gap)
        elif gap_severity == "MEDIUM":
            if len(medium) < limit:
                medium.append(gap)
        else:
            if len(low) < limit:
                low.append(gap)

    return GapAnalysis(
        total_gaps=len(critical) + len(high) + len(medium) + len(low),
        critical=critical,
        high=high,
        medium=medium,
        low=low,
    )


@router.get("/gaps/{framework_id}", response_model=GapAnalysis)
async def get_framework_gaps(
    framework_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """
    Get compliance gaps for a specific framework.
    """
    return await get_compliance_gaps(framework_id=framework_id, db=db, tenant_id=tenant_id)


@router.get("/mapping")
async def get_framework_mapping(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """
    Get cross-framework control mapping.

    Shows how controls from one framework map to another,
    enabling "comply once, satisfy multiple frameworks" efficiency.
    """
    # Get all frameworks
    result = await db.execute(
        select(Framework)
        .where(Framework.tenant_id == tenant_id, Framework.is_active == True)
        .order_by(Framework.name)
    )
    frameworks = result.scalars().all()

    # For now, return a simple mapping based on control categories
    mappings = []

    # Predefined category mappings between frameworks
    # In a real implementation, this would use actual control mapping data
    category_mappings = {
        ("ISO/IEC 27001:2022", "SOC 2 Type II"): 0.85,
        ("ISO/IEC 27001:2022", "152-FZ Personal Data Protection"): 0.60,
        ("ISO/IEC 27001:2022", "GOST R 57580.1-2017 Financial Sector Security"): 0.75,
        ("SOC 2 Type II", "ISO/IEC 27001:2022"): 0.85,
        ("GDPR", "152-FZ Personal Data Protection"): 0.70,
        ("PCI DSS v4.0", "CBR 382-P Banking Information Security"): 0.65,
        ("152-FZ Personal Data Protection", "GDPR"): 0.70,
        (
            "CBR 382-P Banking Information Security",
            "GOST R 57580.1-2017 Financial Sector Security",
        ): 0.80,
        ("187-FZ Critical Information Infrastructure", "ISO/IEC 27001:2022"): 0.55,
    }

    for fw1 in frameworks:
        for fw2 in frameworks:
            if fw1.id != fw2.id:
                key = (fw1.name, fw2.name)
                if key in category_mappings:
                    efficiency = category_mappings[key]
                    mappings.append(
                        {
                            "source_framework_id": str(fw1.id),
                            "source_framework_name": fw1.name,
                            "target_framework_id": str(fw2.id),
                            "target_framework_name": fw2.name,
                            "efficiency_score": efficiency,
                            "description": f"Complying with {fw1.name} satisfies approximately {int(efficiency * 100)}% of {fw2.name} requirements",
                        }
                    )

    return {
        "total_frameworks": len(frameworks),
        "total_mappings": len(mappings),
        "mappings": mappings,
        "summary": {
            "most_efficient": sorted(mappings, key=lambda x: x["efficiency_score"], reverse=True)[
                :5
            ]
            if mappings
            else [],
            "recommended_priority": [
                "ISO/IEC 27001:2022",
                "152-FZ Personal Data Protection",
                "GOST R 57580.1-2017 Financial Sector Security",
            ],
        },
    }


@router.get("/dashboard")
async def get_compliance_dashboard(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """
    Get compliance dashboard summary.

    Returns all key metrics for the compliance dashboard in a single call.
    """
    # Get overall score
    score_data = await get_compliance_score(framework_id=None, db=db, tenant_id=tenant_id)

    # Get top gaps (critical and high only)
    gaps_data = await get_compliance_gaps(
        framework_id=None, severity=None, limit=10, db=db, tenant_id=tenant_id
    )

    # Get framework mapping summary
    mapping_data = await get_framework_mapping(db=db, tenant_id=tenant_id)

    # Recent activity (placeholder)
    recent_activity = [
        {
            "type": "ASSESSMENT",
            "description": "ISO 27001 control A.5.1 assessed as IMPLEMENTED",
            "timestamp": datetime.now(UTC).isoformat(),
            "user": "System",
        },
        {
            "type": "GAP_CLOSED",
            "description": "Access Control gap remediated",
            "timestamp": (datetime.now(UTC) - timedelta(hours=2)).isoformat(),
            "user": "System",
        },
    ]

    return {
        "score": {
            "overall": score_data.overall_score,
            "grade": score_data.overall_grade,
            "trend": score_data.trend,
        },
        "summary": {
            "total_frameworks": score_data.total_frameworks,
            "total_controls": score_data.total_controls,
            "implemented": score_data.implemented,
            "gaps": gaps_data.total_gaps,
        },
        "frameworks": [
            {
                "id": fw.framework_id,
                "name": fw.framework_name,
                "score": fw.score,
                "grade": fw.grade,
                "total": fw.total_controls,
                "implemented": fw.implemented,
            }
            for fw in score_data.frameworks
        ],
        "top_gaps": {
            "critical_count": len(gaps_data.critical),
            "high_count": len(gaps_data.high),
            "items": gaps_data.critical[:5] + gaps_data.high[:5],
        },
        "efficiency": {
            "cross_framework_mappings": mapping_data.get("total_mappings", 0),
            "recommended_priority": mapping_data.get("summary", {}).get("recommended_priority", []),
        },
        "recent_activity": recent_activity,
    }
