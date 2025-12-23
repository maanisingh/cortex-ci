"""Phase 2.3: Risk Justification Engine - Legal defensibility API."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.models import (
    RiskJustification, Entity, RiskScore, Constraint,
    AuditLog, AuditAction,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


# Schemas
class RiskFactorContribution(BaseModel):
    factor: str
    contribution: float
    source: str
    evidence: str


class RiskJustificationResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_name: Optional[str] = None
    risk_score: float
    risk_level: str
    primary_factors: List[Dict[str, Any]]
    assumptions: List[str]
    confidence: float
    uncertainty_factors: List[str]
    source_citations: List[Dict[str, Any]]
    analyst_can_override: bool
    was_overridden: bool
    override_reason: Optional[str] = None
    created_at: datetime
    version: int

    class Config:
        from_attributes = True


class JustificationOverrideRequest(BaseModel):
    new_score: float = Field(..., ge=0, le=100)
    reason: str = Field(..., min_length=10)


class LegalExportResponse(BaseModel):
    entity_id: str
    risk_score: float
    level: str
    justification: Dict[str, Any]
    override: Optional[Dict[str, Any]] = None
    export_timestamp: str
    export_format: str = "legal_defense"


@router.get("/{entity_id}")
async def get_risk_justification(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """
    Get detailed risk justification for an entity.

    Returns "why this rating" with factor breakdowns, assumptions, and source citations.
    """
    # Get entity
    entity_result = await db.execute(
        select(Entity).where(Entity.id == entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get risk score
    risk_result = await db.execute(
        select(RiskScore).where(
            RiskScore.entity_id == entity_id,
            RiskScore.tenant_id == tenant.id,
        )
    )
    risk_score = risk_result.scalar_one_or_none()

    # Check for existing justification
    just_result = await db.execute(
        select(RiskJustification).where(
            RiskJustification.entity_id == entity_id,
            RiskJustification.tenant_id == tenant.id,
        ).order_by(RiskJustification.version.desc())
    )
    justification = just_result.scalar_one_or_none()

    if justification:
        return _format_justification_response(justification, entity)

    # Generate justification on-the-fly if none exists
    generated = await _generate_justification(db, entity, risk_score, tenant.id)
    return _format_justification_response(generated, entity)


@router.get("/{entity_id}/export")
async def export_risk_justification(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    format: str = Query("json", regex="^(json|legal)$"),
) -> LegalExportResponse:
    """
    Export risk justification in legal defense format.

    Suitable for compliance documentation and audit trails.
    """
    # Get entity
    entity_result = await db.execute(
        select(Entity).where(Entity.id == entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get or generate justification
    just_result = await db.execute(
        select(RiskJustification).where(
            RiskJustification.entity_id == entity_id,
            RiskJustification.tenant_id == tenant.id,
        ).order_by(RiskJustification.version.desc())
    )
    justification = just_result.scalar_one_or_none()

    if not justification:
        risk_result = await db.execute(
            select(RiskScore).where(
                RiskScore.entity_id == entity_id,
                RiskScore.tenant_id == tenant.id,
            )
        )
        risk_score = risk_result.scalar_one_or_none()
        justification = await _generate_justification(db, entity, risk_score, tenant.id)

    return LegalExportResponse(
        entity_id=str(entity_id),
        risk_score=float(justification.risk_score),
        level=justification.risk_level,
        justification={
            "primary_factors": justification.primary_factors,
            "assumptions": justification.assumptions,
            "uncertainty": {
                "confidence": float(justification.confidence),
                "factors": justification.uncertainty_factors,
            },
            "sources": justification.source_citations,
            "generated_at": justification.created_at.isoformat() if justification.created_at else None,
            "analyst_can_override": justification.analyst_can_override,
        },
        override={
            "was_overridden": justification.overridden_by is not None,
            "overridden_at": justification.overridden_at.isoformat() if justification.overridden_at else None,
            "reason": justification.override_reason,
            "original_score": float(justification.original_score) if justification.original_score else None,
        } if justification.overridden_by else None,
        export_timestamp=datetime.utcnow().isoformat(),
        export_format="legal_defense",
    )


@router.post("/{entity_id}/override")
async def override_risk_score(
    entity_id: UUID,
    override_data: JustificationOverrideRequest,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """
    Override a risk score with analyst justification.

    Creates a new version of the justification with override tracking.
    """
    # Get entity
    entity_result = await db.execute(
        select(Entity).where(Entity.id == entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get current justification
    just_result = await db.execute(
        select(RiskJustification).where(
            RiskJustification.entity_id == entity_id,
            RiskJustification.tenant_id == tenant.id,
        ).order_by(RiskJustification.version.desc())
    )
    current_just = just_result.scalar_one_or_none()

    if not current_just:
        risk_result = await db.execute(
            select(RiskScore).where(
                RiskScore.entity_id == entity_id,
                RiskScore.tenant_id == tenant.id,
            )
        )
        risk_score = risk_result.scalar_one_or_none()
        current_just = await _generate_justification(db, entity, risk_score, tenant.id)

    if not current_just.analyst_can_override:
        raise HTTPException(
            status_code=403,
            detail="This risk score cannot be overridden",
        )

    # Create new version with override
    new_justification = RiskJustification(
        tenant_id=tenant.id,
        entity_id=entity_id,
        risk_score_id=current_just.risk_score_id,
        risk_score=Decimal(str(override_data.new_score)),
        risk_level=_get_risk_level(override_data.new_score),
        primary_factors=current_just.primary_factors + [{
            "factor": "analyst_override",
            "contribution": override_data.new_score - float(current_just.risk_score),
            "source": "Analyst Override",
            "evidence": override_data.reason,
        }],
        assumptions=current_just.assumptions + [
            f"Analyst override applied by {current_user.email}",
        ],
        confidence=Decimal("0.95"),  # Higher confidence with human review
        uncertainty_factors=["Manual override applied"],
        source_citations=current_just.source_citations,
        analyst_can_override=True,
        overridden_by=current_user.id,
        overridden_at=datetime.utcnow(),
        override_reason=override_data.reason,
        original_score=current_just.risk_score,
        version=current_just.version + 1,
        previous_version_id=current_just.id,
    )
    db.add(new_justification)

    # Update actual risk score
    risk_result = await db.execute(
        select(RiskScore).where(
            RiskScore.entity_id == entity_id,
            RiskScore.tenant_id == tenant.id,
        )
    )
    risk_score = risk_result.scalar_one_or_none()
    if risk_score:
        risk_score.score = Decimal(str(override_data.new_score))

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="risk_justification",
        resource_id=new_justification.id,
        before_state={"score": float(current_just.risk_score)},
        after_state={"score": override_data.new_score, "reason": override_data.reason},
        success=True,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(new_justification)

    return {
        "success": True,
        "message": "Risk score overridden successfully",
        "previous_score": float(current_just.risk_score),
        "new_score": override_data.new_score,
        "new_level": _get_risk_level(override_data.new_score),
        "justification_version": new_justification.version,
    }


@router.get("/{entity_id}/history")
async def get_justification_history(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> List[Dict[str, Any]]:
    """Get history of all justification versions for an entity."""
    result = await db.execute(
        select(RiskJustification).where(
            RiskJustification.entity_id == entity_id,
            RiskJustification.tenant_id == tenant.id,
        ).order_by(RiskJustification.version.desc())
    )
    justifications = result.scalars().all()

    return [
        {
            "version": j.version,
            "risk_score": float(j.risk_score),
            "risk_level": j.risk_level,
            "confidence": float(j.confidence),
            "was_overridden": j.overridden_by is not None,
            "override_reason": j.override_reason,
            "created_at": j.created_at.isoformat() if j.created_at else None,
        }
        for j in justifications
    ]


async def _generate_justification(
    db: DB,
    entity: Entity,
    risk_score: Optional[RiskScore],
    tenant_id: UUID,
) -> RiskJustification:
    """Generate a justification for an entity's risk score."""
    score = float(risk_score.score) if risk_score else 0.0
    level = _get_risk_level(score)

    # Build factors based on entity properties
    factors = []

    # Country risk factor
    high_risk_countries = {"RU": 95, "IR": 95, "KP": 95, "SY": 90, "BY": 80, "VE": 75, "CU": 70}
    if entity.country_code and entity.country_code in high_risk_countries:
        factors.append({
            "factor": "country_risk",
            "contribution": high_risk_countries[entity.country_code] * 0.35,
            "source": "OFAC Country Sanctions",
            "evidence": f"Entity located in sanctioned jurisdiction ({entity.country_code})",
        })

    # Source-based factor
    if entity.source and "OFAC" in entity.source.upper():
        factors.append({
            "factor": "sanctions_list_match",
            "contribution": 30.0,
            "source": "OFAC SDN List",
            "evidence": f"Direct match on OFAC sanctions list",
        })
    elif entity.source and "UN" in entity.source.upper():
        factors.append({
            "factor": "sanctions_list_match",
            "contribution": 28.0,
            "source": "UN Consolidated List",
            "evidence": f"Direct match on UN sanctions list",
        })

    # Entity type factor
    type_risk = {
        "VESSEL": 15,
        "AIRCRAFT": 12,
        "ORGANIZATION": 10,
        "INDIVIDUAL": 8,
    }
    if entity.type and entity.type.value in type_risk:
        factors.append({
            "factor": "entity_type",
            "contribution": type_risk[entity.type.value],
            "source": "Internal Classification",
            "evidence": f"Entity type {entity.type.value} has elevated baseline risk",
        })

    # Criticality factor
    if entity.criticality and entity.criticality >= 4:
        factors.append({
            "factor": "criticality",
            "contribution": entity.criticality * 3,
            "source": "Internal Assessment",
            "evidence": f"Criticality level {entity.criticality}/5",
        })

    # Assumptions
    assumptions = [
        "Country code derived from registered address or nationality",
        "Sanctions list matching uses exact name match algorithm",
        "Entity type classification based on available metadata",
        "Risk scores are calculated deterministically",
    ]

    # Uncertainty factors
    uncertainty = [
        "Name variations may not be captured",
        "Beneficial ownership not fully verified",
        "Historical data may be incomplete",
    ]

    # Source citations
    sources = []
    if entity.source:
        sources.append({
            "source": entity.source,
            "date": entity.created_at.strftime("%Y-%m-%d") if entity.created_at else None,
            "record_id": entity.external_id or str(entity.id),
        })

    justification = RiskJustification(
        tenant_id=tenant_id,
        entity_id=entity.id,
        risk_score=Decimal(str(score)),
        risk_level=level,
        primary_factors=factors,
        assumptions=assumptions,
        confidence=Decimal("0.85"),
        uncertainty_factors=uncertainty,
        source_citations=sources,
        analyst_can_override=True,
        version=1,
    )
    db.add(justification)
    await db.commit()
    await db.refresh(justification)

    return justification


def _format_justification_response(justification: RiskJustification, entity: Entity) -> Dict[str, Any]:
    """Format justification for API response."""
    return {
        "entity_id": str(justification.entity_id),
        "entity_name": entity.name,
        "risk_score": float(justification.risk_score),
        "risk_level": justification.risk_level,
        "primary_factors": justification.primary_factors,
        "assumptions": justification.assumptions,
        "confidence": float(justification.confidence),
        "uncertainty_factors": justification.uncertainty_factors,
        "source_citations": justification.source_citations,
        "analyst_can_override": justification.analyst_can_override,
        "was_overridden": justification.overridden_by is not None,
        "override_reason": justification.override_reason,
        "created_at": justification.created_at.isoformat() if justification.created_at else None,
        "version": justification.version,
    }


def _get_risk_level(score: float) -> str:
    """Convert score to risk level."""
    if score >= 80:
        return "CRITICAL"
    elif score >= 60:
        return "HIGH"
    elif score >= 40:
        return "MEDIUM"
    elif score >= 20:
        return "LOW"
    else:
        return "MINIMAL"
