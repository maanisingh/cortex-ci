from typing import Optional, List
from uuid import UUID
from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import select, func

from app.models import RiskScore, RiskLevel, Entity, AuditLog, AuditAction
from app.schemas.risk import (
    RiskScoreResponse,
    RiskSummary,
    RiskTrend,
    RiskCalculateRequest,
    RiskCalculateResponse,
    RiskJustification,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


@router.get("/summary", response_model=RiskSummary)
async def get_risk_summary(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get risk summary across all entities."""
    # Get latest risk score for each entity
    subquery = (
        select(
            RiskScore.entity_id,
            func.max(RiskScore.calculated_at).label("latest"),
        )
        .where(RiskScore.tenant_id == tenant.id)
        .group_by(RiskScore.entity_id)
        .subquery()
    )

    query = (
        select(RiskScore)
        .join(
            subquery,
            (RiskScore.entity_id == subquery.c.entity_id)
            & (RiskScore.calculated_at == subquery.c.latest),
        )
    )

    result = await db.execute(query)
    scores = result.scalars().all()

    # Count by level
    level_counts = {level.value: 0 for level in RiskLevel}
    total_score = 0

    for score in scores:
        level_counts[score.level.value] += 1
        total_score += float(score.score)

    # Recent changes (last 30 days)
    thirty_days_ago = datetime.now(timezone.utc) - timedelta(days=30)
    escalations = sum(1 for s in scores if s.level_changed and s.previous_level and
                      RiskLevel[s.level.value].value > RiskLevel[s.previous_level.value].value)
    improvements = sum(1 for s in scores if s.level_changed and s.previous_level and
                       RiskLevel[s.level.value].value < RiskLevel[s.previous_level.value].value)

    return RiskSummary(
        total_entities=len(scores),
        entities_by_level=level_counts,
        average_score=total_score / len(scores) if scores else 0,
        critical_count=level_counts["CRITICAL"],
        high_count=level_counts["HIGH"],
        medium_count=level_counts["MEDIUM"],
        low_count=level_counts["LOW"],
        recent_escalations=escalations,
        recent_improvements=improvements,
    )


@router.get("/trends", response_model=List[RiskTrend])
async def get_risk_trends(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    days: int = Query(30, ge=7, le=365),
):
    """Get risk trends over time."""
    from sqlalchemy import case

    start_date = datetime.now(timezone.utc) - timedelta(days=days)
    date_col = func.date_trunc("day", RiskScore.calculated_at)

    # Get daily aggregates using CASE WHEN for conditional counts
    query = (
        select(
            date_col.label("date"),
            func.avg(RiskScore.score).label("avg_score"),
            func.sum(case((RiskScore.level == RiskLevel.CRITICAL, 1), else_=0)).label("critical"),
            func.sum(case((RiskScore.level == RiskLevel.HIGH, 1), else_=0)).label("high"),
            func.sum(case((RiskScore.level == RiskLevel.MEDIUM, 1), else_=0)).label("medium"),
            func.sum(case((RiskScore.level == RiskLevel.LOW, 1), else_=0)).label("low"),
        )
        .where(
            RiskScore.tenant_id == tenant.id,
            RiskScore.calculated_at >= start_date,
        )
        .group_by(date_col)
        .order_by(date_col)
    )

    result = await db.execute(query)
    rows = result.all()

    # Return empty list if no data
    if not rows:
        return []

    return [
        RiskTrend(
            date=row.date,
            average_score=float(row.avg_score) if row.avg_score else 0,
            critical_count=int(row.critical or 0),
            high_count=int(row.high or 0),
            medium_count=int(row.medium or 0),
            low_count=int(row.low or 0),
        )
        for row in rows
    ]


@router.get("/entity/{entity_id}", response_model=RiskScoreResponse)
async def get_entity_risk(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get latest risk score for an entity."""
    result = await db.execute(
        select(RiskScore)
        .where(
            RiskScore.entity_id == entity_id,
            RiskScore.tenant_id == tenant.id,
        )
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk score found for this entity",
        )

    return score


@router.get("/entity/{entity_id}/history", response_model=List[RiskScoreResponse])
async def get_entity_risk_history(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    limit: int = Query(30, ge=1, le=100),
):
    """Get risk score history for an entity."""
    result = await db.execute(
        select(RiskScore)
        .where(
            RiskScore.entity_id == entity_id,
            RiskScore.tenant_id == tenant.id,
        )
        .order_by(RiskScore.calculated_at.desc())
        .limit(limit)
    )
    scores = result.scalars().all()

    return scores


@router.get("/entity/{entity_id}/justification", response_model=RiskJustification)
async def get_risk_justification(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get detailed justification for an entity's risk score (Phase 2)."""
    result = await db.execute(
        select(RiskScore)
        .where(
            RiskScore.entity_id == entity_id,
            RiskScore.tenant_id == tenant.id,
        )
        .order_by(RiskScore.calculated_at.desc())
        .limit(1)
    )
    score = result.scalar_one_or_none()

    if not score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No risk score found for this entity",
        )

    # Build justification from factors
    factors = score.factors or {}

    return RiskJustification(
        risk_level=score.level,
        primary_factors=factors.get("primary_factors", []),
        assumptions=factors.get("assumptions", [
            "Entity name matching uses 85% threshold",
            "Country risk based on FATF and sanctions lists",
        ]),
        supporting_sources=factors.get("sources", []),
        uncertainty=factors.get("uncertainty", "Standard confidence level"),
        recommendation=factors.get("recommendation", "Review if score exceeds threshold"),
        calculation_details={
            "direct_match": float(score.direct_match_score),
            "indirect_match": float(score.indirect_match_score),
            "country_risk": float(score.country_risk_score),
            "dependency_risk": float(score.dependency_risk_score),
            "total": float(score.score),
        },
    )


@router.post("/calculate", response_model=RiskCalculateResponse)
async def calculate_risks(
    request: RiskCalculateRequest,
    background_tasks: BackgroundTasks,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Calculate risk scores for entities."""
    from app.services.risk_engine import RiskEngine

    engine = RiskEngine(db, tenant)

    if request.entity_ids:
        # Calculate for specific entities
        count = await engine.calculate_for_entities(
            request.entity_ids,
            force=request.force_recalculate,
        )
    else:
        # Calculate for all entities in background
        background_tasks.add_task(
            engine.calculate_all,
            force=request.force_recalculate,
        )
        count = -1  # Indicates background processing

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.RISK_CALCULATE,
        description=f"Risk calculation triggered for {len(request.entity_ids) if request.entity_ids else 'all'} entities",
        metadata={
            "entity_count": len(request.entity_ids) if request.entity_ids else "all",
            "force": request.force_recalculate,
        },
        success=True,
    )
    db.add(audit)
    await db.commit()

    return RiskCalculateResponse(
        calculated=count if count >= 0 else 0,
        errors=[],
    )
