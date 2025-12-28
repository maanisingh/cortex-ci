from datetime import UTC, datetime, timedelta
from uuid import UUID

from fastapi import APIRouter, BackgroundTasks, HTTPException, Query, status
from sqlalchemy import func, select

from app.api.v1.deps import DB, CurrentTenant, CurrentUser, RequireWriter
from app.models import AuditAction, AuditLog, RiskLevel, RiskScore
from app.models.risk import RiskRegister, RiskCategory, RiskStatus
from app.schemas.risk import (
    RiskCalculateRequest,
    RiskCalculateResponse,
    RiskJustification,
    RiskScoreResponse,
    RiskSummary,
    RiskTrend,
    RiskRegisterCreate,
    RiskRegisterUpdate,
    RiskRegisterResponse,
    RiskRegisterList,
    RiskRegisterSummary,
)

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

    query = select(RiskScore).join(
        subquery,
        (RiskScore.entity_id == subquery.c.entity_id)
        & (RiskScore.calculated_at == subquery.c.latest),
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
    datetime.now(UTC) - timedelta(days=30)
    escalations = sum(
        1
        for s in scores
        if s.level_changed
        and s.previous_level
        and RiskLevel[s.level.value].value > RiskLevel[s.previous_level.value].value
    )
    improvements = sum(
        1
        for s in scores
        if s.level_changed
        and s.previous_level
        and RiskLevel[s.level.value].value < RiskLevel[s.previous_level.value].value
    )

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


@router.get("/trends", response_model=list[RiskTrend])
async def get_risk_trends(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    days: int = Query(30, ge=7, le=365),
):
    """Get risk trends over time."""
    from sqlalchemy import case

    start_date = datetime.now(UTC) - timedelta(days=days)
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


@router.get("/entity/{entity_id}/history", response_model=list[RiskScoreResponse])
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
        assumptions=factors.get(
            "assumptions",
            [
                "Entity name matching uses 85% threshold",
                "Country risk based on FATF and sanctions lists",
            ],
        ),
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


# ============== Risk Register Endpoints ==============

async def generate_risk_id(db: DB, tenant_id: UUID) -> str:
    """Generate a unique risk ID."""
    year = datetime.now(UTC).year
    result = await db.execute(
        select(func.count(RiskRegister.id))
        .where(RiskRegister.tenant_id == tenant_id)
    )
    count = result.scalar() or 0
    return f"RISK-{year}-{count + 1:04d}"


@router.get("/register", response_model=RiskRegisterList)
async def list_risk_register(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    category: RiskCategory | None = None,
    status_filter: RiskStatus | None = Query(None, alias="status"),
    level: RiskLevel | None = None,
    search: str | None = None,
):
    """List all risks in the risk register."""
    query = select(RiskRegister).where(RiskRegister.tenant_id == tenant.id)

    if category:
        query = query.where(RiskRegister.category == category)
    if status_filter:
        query = query.where(RiskRegister.status == status_filter)
    if level:
        query = query.where(RiskRegister.inherent_risk_level == level)
    if search:
        query = query.where(RiskRegister.title.ilike(f"%{search}%"))

    # Count total
    count_result = await db.execute(select(func.count()).select_from(query.subquery()))
    total = count_result.scalar() or 0

    # Paginate
    query = query.order_by(RiskRegister.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    risks = result.scalars().all()

    return RiskRegisterList(
        items=risks,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/register/summary", response_model=RiskRegisterSummary)
async def get_risk_register_summary(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get summary of the risk register."""
    result = await db.execute(
        select(RiskRegister).where(RiskRegister.tenant_id == tenant.id)
    )
    risks = result.scalars().all()

    by_category = {}
    by_status = {}
    by_level = {}
    exceeds_count = 0
    overdue_count = 0
    inherent_scores = []
    residual_scores = []
    now = datetime.now(UTC)

    for risk in risks:
        # Category counts
        cat = risk.category.value
        by_category[cat] = by_category.get(cat, 0) + 1

        # Status counts
        stat = risk.status.value
        by_status[stat] = by_status.get(stat, 0) + 1

        # Level counts
        if risk.inherent_risk_level:
            lvl = risk.inherent_risk_level.value
            by_level[lvl] = by_level.get(lvl, 0) + 1

        # Exceeds appetite
        if risk.exceeds_appetite:
            exceeds_count += 1

        # Overdue review
        if risk.review_date and risk.review_date < now:
            overdue_count += 1

        # Scores
        if risk.inherent_risk_score:
            inherent_scores.append(float(risk.inherent_risk_score))
        if risk.residual_risk_score:
            residual_scores.append(float(risk.residual_risk_score))

    return RiskRegisterSummary(
        total_risks=len(risks),
        by_category=by_category,
        by_status=by_status,
        by_level=by_level,
        exceeds_appetite_count=exceeds_count,
        overdue_review_count=overdue_count,
        average_inherent_score=sum(inherent_scores) / len(inherent_scores) if inherent_scores else 0,
        average_residual_score=sum(residual_scores) / len(residual_scores) if residual_scores else None,
    )


@router.post("/register", response_model=RiskRegisterResponse, status_code=status.HTTP_201_CREATED)
async def create_risk(
    data: RiskRegisterCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new risk in the risk register."""
    risk_id = await generate_risk_id(db, tenant.id)

    risk = RiskRegister(
        tenant_id=tenant.id,
        risk_id=risk_id,
        **data.model_dump(exclude_unset=True),
    )

    # Calculate scores
    risk.calculate_inherent_score()
    risk.calculate_residual_score()
    risk.check_appetite()

    db.add(risk)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="risk_register",
        resource_id=risk.id,
        description=f"Created risk: {risk.title}",
        metadata={"risk_id": risk_id, "category": risk.category.value},
        success=True,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(risk)

    return risk


@router.get("/register/{risk_uuid}", response_model=RiskRegisterResponse)
async def get_risk(
    risk_uuid: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific risk from the risk register."""
    result = await db.execute(
        select(RiskRegister).where(
            RiskRegister.id == risk_uuid,
            RiskRegister.tenant_id == tenant.id,
        )
    )
    risk = result.scalar_one_or_none()

    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found",
        )

    return risk


@router.put("/register/{risk_uuid}", response_model=RiskRegisterResponse)
async def update_risk(
    risk_uuid: UUID,
    data: RiskRegisterUpdate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Update a risk in the risk register."""
    result = await db.execute(
        select(RiskRegister).where(
            RiskRegister.id == risk_uuid,
            RiskRegister.tenant_id == tenant.id,
        )
    )
    risk = result.scalar_one_or_none()

    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found",
        )

    # Update fields
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(risk, field, value)

    # Recalculate scores
    risk.calculate_inherent_score()
    risk.calculate_residual_score()
    risk.check_appetite()

    # Update assessment timestamp
    risk.last_assessed_at = datetime.now(UTC)
    risk.last_assessed_by = current_user.email

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="risk_register",
        resource_id=risk.id,
        description=f"Updated risk: {risk.title}",
        metadata={"updated_fields": list(update_data.keys())},
        success=True,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(risk)

    return risk


@router.delete("/register/{risk_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_risk(
    risk_uuid: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete a risk from the risk register."""
    result = await db.execute(
        select(RiskRegister).where(
            RiskRegister.id == risk_uuid,
            RiskRegister.tenant_id == tenant.id,
        )
    )
    risk = result.scalar_one_or_none()

    if not risk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Risk not found",
        )

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="risk_register",
        resource_id=risk.id,
        description=f"Deleted risk: {risk.title}",
        metadata={"risk_id": risk.risk_id},
        success=True,
    )
    db.add(audit)

    await db.delete(risk)
    await db.commit()
