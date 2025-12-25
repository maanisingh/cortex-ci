"""Phase 2.4: Institutional Memory - Historical tracking API."""

from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime, date, timedelta

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, and_

from app.models import (
    HistoricalSnapshot,
    DecisionOutcome,
    ConstraintChange,
    TransitionReport,
    Entity,
    RiskScore,
    Constraint,
    AuditLog,
    AuditAction,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


# Schemas
class TimelinePoint(BaseModel):
    date: str
    risk_score: float
    risk_level: str
    constraint_count: int
    notes: Optional[str] = None


class EntityTimelineResponse(BaseModel):
    entity_id: str
    entity_name: str
    timeline: List[TimelinePoint]
    trend: str  # "increasing", "decreasing", "stable"
    first_seen: str
    last_updated: str


class DecisionOutcomeCreate(BaseModel):
    decision_date: date
    decision_summary: str
    decision_type: str
    entities_involved: List[UUID] = []
    context_snapshot: Dict[str, Any] = {}


class DecisionOutcomeResponse(BaseModel):
    id: UUID
    decision_date: str
    decision_summary: str
    decision_type: str
    entities_involved: List[str]
    outcome_date: Optional[str] = None
    outcome_summary: Optional[str] = None
    outcome_success: Optional[bool] = None
    lessons_learned: Optional[str] = None
    is_resolved: bool
    created_at: str

    class Config:
        from_attributes = True


class ConstraintChangeResponse(BaseModel):
    id: UUID
    constraint_id: UUID
    constraint_name: Optional[str] = None
    change_date: str
    change_type: str
    change_summary: str
    entities_affected: int

    class Config:
        from_attributes = True


class TransitionReportCreate(BaseModel):
    title: str
    period_start: date
    period_end: date
    executive_summary: str


@router.get("/entity/{entity_id}/timeline")
async def get_entity_timeline(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    days: int = Query(90, ge=7, le=365),
) -> EntityTimelineResponse:
    """
    Get risk timeline for an entity.

    Shows how risk score has changed over time.
    """
    # Get entity
    entity_result = await db.execute(
        select(Entity).where(Entity.id == entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get historical snapshots
    cutoff = date.today() - timedelta(days=days)
    snapshots_result = await db.execute(
        select(HistoricalSnapshot)
        .where(
            HistoricalSnapshot.entity_id == entity_id,
            HistoricalSnapshot.tenant_id == tenant.id,
            HistoricalSnapshot.snapshot_date >= cutoff,
        )
        .order_by(HistoricalSnapshot.snapshot_date)
    )
    snapshots = snapshots_result.scalars().all()

    # If no snapshots, generate from current state
    if not snapshots:
        risk_result = await db.execute(
            select(RiskScore).where(
                RiskScore.entity_id == entity_id,
                RiskScore.tenant_id == tenant.id,
            )
        )
        risk_score = risk_result.scalar_one_or_none()
        current_score = float(risk_score.score) if risk_score else 0.0

        timeline = [
            TimelinePoint(
                date=date.today().isoformat(),
                risk_score=current_score,
                risk_level=_get_risk_level(current_score),
                constraint_count=0,
                notes="Current state",
            )
        ]
        trend = "stable"
    else:
        timeline = [
            TimelinePoint(
                date=s.snapshot_date.isoformat(),
                risk_score=float(s.risk_score),
                risk_level=s.risk_level,
                constraint_count=len(s.constraints_applied or []),
                notes=s.notes,
            )
            for s in snapshots
        ]

        # Calculate trend
        if len(timeline) >= 2:
            first_score = timeline[0].risk_score
            last_score = timeline[-1].risk_score
            if last_score > first_score + 5:
                trend = "increasing"
            elif last_score < first_score - 5:
                trend = "decreasing"
            else:
                trend = "stable"
        else:
            trend = "stable"

    return EntityTimelineResponse(
        entity_id=str(entity_id),
        entity_name=entity.name,
        timeline=timeline,
        trend=trend,
        first_seen=entity.created_at.isoformat()
        if entity.created_at
        else date.today().isoformat(),
        last_updated=entity.updated_at.isoformat()
        if entity.updated_at
        else date.today().isoformat(),
    )


@router.post("/snapshot")
async def create_snapshot(
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """
    Create a snapshot of all entities' current risk state.

    Typically run daily by a scheduled job.
    """
    today = date.today()

    # Get all entities with risk scores
    result = await db.execute(
        select(Entity, RiskScore)
        .outerjoin(
            RiskScore,
            and_(
                Entity.id == RiskScore.entity_id,
                RiskScore.tenant_id == tenant.id,
            ),
        )
        .where(
            Entity.tenant_id == tenant.id,
            Entity.is_active,
        )
    )

    created = 0
    for entity, risk_score in result:
        # Check if snapshot already exists for today
        existing = await db.execute(
            select(HistoricalSnapshot).where(
                HistoricalSnapshot.entity_id == entity.id,
                HistoricalSnapshot.snapshot_date == today,
            )
        )
        if existing.scalar_one_or_none():
            continue

        score = float(risk_score.score) if risk_score else 0.0

        snapshot = HistoricalSnapshot(
            tenant_id=tenant.id,
            entity_id=entity.id,
            snapshot_date=today,
            risk_score=Decimal(str(score)),
            risk_level=_get_risk_level(score),
            constraints_applied=[],
            entity_data={
                "name": entity.name,
                "type": entity.type.value if entity.type else None,
                "country": entity.country_code,
                "criticality": entity.criticality,
            },
        )
        db.add(snapshot)
        created += 1

    await db.commit()

    return {
        "success": True,
        "snapshot_date": today.isoformat(),
        "entities_snapshotted": created,
    }


@router.get("/constraints/changes")
async def get_constraint_changes(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    days: int = Query(30, ge=1, le=365),
) -> List[ConstraintChangeResponse]:
    """Get recent constraint changes."""
    cutoff = date.today() - timedelta(days=days)

    result = await db.execute(
        select(ConstraintChange, Constraint.name)
        .outerjoin(Constraint, ConstraintChange.constraint_id == Constraint.id)
        .where(
            ConstraintChange.tenant_id == tenant.id,
            ConstraintChange.change_date >= cutoff,
        )
        .order_by(ConstraintChange.change_date.desc())
    )

    changes = []
    for change, constraint_name in result:
        changes.append(
            ConstraintChangeResponse(
                id=change.id,
                constraint_id=change.constraint_id,
                constraint_name=constraint_name,
                change_date=change.change_date.isoformat(),
                change_type=change.change_type,
                change_summary=change.change_summary,
                entities_affected=change.entities_affected,
            )
        )

    return changes


@router.post("/decisions")
async def create_decision_outcome(
    data: DecisionOutcomeCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> DecisionOutcomeResponse:
    """Record a decision for outcome tracking."""
    # Get current risk scores for involved entities
    risk_scores = {}
    if data.entities_involved:
        result = await db.execute(
            select(RiskScore).where(
                RiskScore.entity_id.in_(data.entities_involved),
                RiskScore.tenant_id == tenant.id,
            )
        )
        for rs in result.scalars():
            risk_scores[str(rs.entity_id)] = float(rs.score)

    decision = DecisionOutcome(
        tenant_id=tenant.id,
        decision_date=data.decision_date,
        decision_summary=data.decision_summary,
        decision_type=data.decision_type,
        decision_maker_id=current_user.id,
        decision_maker_name=current_user.email,
        entities_involved=[str(e) for e in data.entities_involved],
        context_snapshot=data.context_snapshot,
        risk_scores_at_decision=risk_scores,
    )
    db.add(decision)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="decision_outcome",
        resource_id=decision.id,
        success=True,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(decision)

    return DecisionOutcomeResponse(
        id=decision.id,
        decision_date=decision.decision_date.isoformat(),
        decision_summary=decision.decision_summary,
        decision_type=decision.decision_type,
        entities_involved=decision.entities_involved,
        outcome_date=None,
        outcome_summary=None,
        outcome_success=None,
        lessons_learned=None,
        is_resolved=False,
        created_at=decision.created_at.isoformat()
        if decision.created_at
        else datetime.utcnow().isoformat(),
    )


@router.get("/decisions")
async def list_decisions(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    include_resolved: bool = False,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """List decision outcomes."""
    query = select(DecisionOutcome).where(
        DecisionOutcome.tenant_id == tenant.id,
    )

    if not include_resolved:
        query = query.where(not DecisionOutcome.is_resolved)

    query = query.order_by(DecisionOutcome.decision_date.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    decisions = result.scalars().all()

    return {
        "items": [
            DecisionOutcomeResponse(
                id=d.id,
                decision_date=d.decision_date.isoformat(),
                decision_summary=d.decision_summary,
                decision_type=d.decision_type,
                entities_involved=d.entities_involved,
                outcome_date=d.outcome_date.isoformat() if d.outcome_date else None,
                outcome_summary=d.outcome_summary,
                outcome_success=d.outcome_success,
                lessons_learned=d.lessons_learned,
                is_resolved=d.is_resolved,
                created_at=d.created_at.isoformat()
                if d.created_at
                else datetime.utcnow().isoformat(),
            )
            for d in decisions
        ],
        "page": page,
        "page_size": page_size,
    }


@router.put("/decisions/{decision_id}/outcome")
async def record_decision_outcome(
    decision_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
    outcome_summary: str = Query(..., min_length=10),
    outcome_success: bool = Query(...),
    lessons_learned: Optional[str] = None,
) -> DecisionOutcomeResponse:
    """Record the outcome of a decision."""
    result = await db.execute(
        select(DecisionOutcome).where(
            DecisionOutcome.id == decision_id,
            DecisionOutcome.tenant_id == tenant.id,
        )
    )
    decision = result.scalar_one_or_none()

    if not decision:
        raise HTTPException(status_code=404, detail="Decision not found")

    decision.outcome_date = date.today()
    decision.outcome_summary = outcome_summary
    decision.outcome_success = outcome_success
    decision.lessons_learned = lessons_learned
    decision.is_resolved = True

    await db.commit()
    await db.refresh(decision)

    return DecisionOutcomeResponse(
        id=decision.id,
        decision_date=decision.decision_date.isoformat(),
        decision_summary=decision.decision_summary,
        decision_type=decision.decision_type,
        entities_involved=decision.entities_involved,
        outcome_date=decision.outcome_date.isoformat()
        if decision.outcome_date
        else None,
        outcome_summary=decision.outcome_summary,
        outcome_success=decision.outcome_success,
        lessons_learned=decision.lessons_learned,
        is_resolved=decision.is_resolved,
        created_at=decision.created_at.isoformat()
        if decision.created_at
        else datetime.utcnow().isoformat(),
    )


@router.post("/transition-report")
async def generate_transition_report(
    data: TransitionReportCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """Generate a leadership transition report."""
    # Gather statistics for the period
    stats = await _gather_period_statistics(
        db, tenant.id, data.period_start, data.period_end
    )

    # Get high-risk entities
    high_risk_result = await db.execute(
        select(Entity, RiskScore)
        .join(RiskScore, Entity.id == RiskScore.entity_id)
        .where(
            Entity.tenant_id == tenant.id,
            RiskScore.score >= 60,
        )
        .order_by(RiskScore.score.desc())
        .limit(10)
    )
    critical_entities = [
        {"id": str(e.id), "name": e.name, "risk_score": float(rs.score)}
        for e, rs in high_risk_result
    ]

    # Get pending decisions
    pending_result = await db.execute(
        select(DecisionOutcome).where(
            DecisionOutcome.tenant_id == tenant.id,
            not DecisionOutcome.is_resolved,
        )
    )
    pending = [
        {"id": str(d.id), "summary": d.decision_summary, "type": d.decision_type}
        for d in pending_result.scalars()
    ]

    # Get recent lessons learned
    lessons_result = await db.execute(
        select(DecisionOutcome)
        .where(
            DecisionOutcome.tenant_id == tenant.id,
            DecisionOutcome.is_resolved,
            DecisionOutcome.lessons_learned.isnot(None),
        )
        .order_by(DecisionOutcome.outcome_date.desc())
        .limit(5)
    )
    lessons = [
        {"decision": d.decision_summary, "lesson": d.lessons_learned}
        for d in lessons_result.scalars()
    ]

    report = TransitionReport(
        tenant_id=tenant.id,
        title=data.title,
        report_date=date.today(),
        period_start=data.period_start,
        period_end=data.period_end,
        executive_summary=data.executive_summary,
        key_risks=stats.get("key_risks", []),
        critical_entities=critical_entities,
        pending_decisions=pending,
        lessons_learned=lessons,
        recommendations=[
            "Continue monitoring high-risk entities",
            "Review pending decisions within 30 days",
            "Update risk models based on lessons learned",
        ],
        statistics=stats,
        generated_by_id=current_user.id,
        is_draft=True,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return {
        "id": str(report.id),
        "title": report.title,
        "period": f"{data.period_start} to {data.period_end}",
        "critical_entities_count": len(critical_entities),
        "pending_decisions_count": len(pending),
        "lessons_learned_count": len(lessons),
        "is_draft": True,
        "created_at": report.created_at.isoformat() if report.created_at else None,
    }


async def _gather_period_statistics(
    db: DB,
    tenant_id: UUID,
    start: date,
    end: date,
) -> Dict[str, Any]:
    """Gather statistics for a period."""
    # Count entities
    entity_count = await db.execute(
        select(func.count(Entity.id)).where(Entity.tenant_id == tenant_id)
    )

    # Count constraints
    constraint_count = await db.execute(
        select(func.count(Constraint.id)).where(Constraint.tenant_id == tenant_id)
    )

    # Average risk score
    avg_risk = await db.execute(
        select(func.avg(RiskScore.score)).where(RiskScore.tenant_id == tenant_id)
    )

    return {
        "total_entities": entity_count.scalar() or 0,
        "total_constraints": constraint_count.scalar() or 0,
        "average_risk_score": round(float(avg_risk.scalar() or 0), 2),
        "period_start": start.isoformat(),
        "period_end": end.isoformat(),
        "key_risks": [
            "Ongoing sanctions exposure in key markets",
            "Dependency concentration in operational layer",
        ],
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
