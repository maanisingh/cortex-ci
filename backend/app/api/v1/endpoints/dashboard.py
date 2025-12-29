from datetime import datetime, timedelta
from typing import Any

from fastapi import APIRouter
from sqlalchemy import func, select

from app.api.v1.deps import DB, CurrentTenant, CurrentUser
from app.models import AuditLog, Constraint, ConstraintSeverity, Dependency, Entity, RiskScore

router = APIRouter()


@router.get("/stats")
async def get_dashboard_stats(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> dict[str, Any]:
    """Get dashboard statistics for the current tenant."""

    # Entity counts by type
    entity_query = (
        select(Entity.type, func.count(Entity.id).label("count"))
        .where(Entity.tenant_id == tenant.id, Entity.is_active)
        .group_by(Entity.type)
    )

    entity_result = await db.execute(entity_query)
    entity_by_type = {str(row.type): row.count for row in entity_result}

    # Total entities
    total_entities = sum(entity_by_type.values())

    # Constraint counts by severity
    constraint_query = (
        select(Constraint.severity, func.count(Constraint.id).label("count"))
        .where(Constraint.tenant_id == tenant.id, Constraint.is_active)
        .group_by(Constraint.severity)
    )

    constraint_result = await db.execute(constraint_query)
    constraints_by_severity = {str(row.severity): row.count for row in constraint_result}

    # Total constraints
    total_constraints = sum(constraints_by_severity.values())

    # Dependency count
    dep_query = select(func.count(Dependency.id)).where(
        Dependency.tenant_id == tenant.id, Dependency.is_active
    )
    total_dependencies = (await db.execute(dep_query)).scalar() or 0

    # Risk scores summary
    risk_query = select(
        func.avg(RiskScore.score).label("avg_risk"),
        func.max(RiskScore.score).label("max_risk"),
        func.count(RiskScore.id).label("count"),
    ).where(RiskScore.tenant_id == tenant.id)

    risk_result = (await db.execute(risk_query)).first()

    # High risk entities (score >= 70)
    high_risk_query = select(func.count(RiskScore.id)).where(
        RiskScore.tenant_id == tenant.id, RiskScore.score >= 70
    )
    high_risk_count = (await db.execute(high_risk_query)).scalar() or 0

    # Critical constraints (severity = critical)
    critical_query = select(func.count(Constraint.id)).where(
        Constraint.tenant_id == tenant.id,
        Constraint.severity == ConstraintSeverity.CRITICAL,
        Constraint.is_active == True,
    )
    critical_constraints = (await db.execute(critical_query)).scalar() or 0

    # Recent audit activity (last 7 days)
    week_ago = datetime.utcnow() - timedelta(days=7)
    audit_query = select(func.count(AuditLog.id)).where(
        AuditLog.tenant_id == tenant.id, AuditLog.created_at >= week_ago
    )
    recent_activity = (await db.execute(audit_query)).scalar() or 0

    return {
        "summary": {
            "total_entities": total_entities,
            "total_constraints": total_constraints,
            "total_dependencies": total_dependencies,
            "high_risk_entities": high_risk_count,
            "critical_constraints": critical_constraints,
        },
        "risk": {
            "average_score": round(risk_result.avg_risk or 0, 2),
            "max_score": round(risk_result.max_risk or 0, 2),
            "scored_entities": risk_result.count or 0,
        },
        "entities_by_type": entity_by_type,
        "constraints_by_severity": constraints_by_severity,
        "activity": {
            "recent_actions": recent_activity,
            "period_days": 7,
        },
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
        },
    }


@router.get("/risk-overview")
async def get_risk_overview(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> dict[str, Any]:
    """Get risk distribution overview."""

    # Get risk score distribution
    risk_query = (
        select(RiskScore.entity_id, RiskScore.score, Entity.name, Entity.type)
        .join(Entity, RiskScore.entity_id == Entity.id)
        .where(RiskScore.tenant_id == tenant.id)
        .order_by(RiskScore.score.desc())
        .limit(20)
    )

    result = await db.execute(risk_query)
    top_risks = [
        {
            "entity_id": str(row.entity_id),
            "entity_name": row.name,
            "entity_type": str(row.type),
            "risk_score": float(row.score),
        }
        for row in result
    ]

    # Risk distribution buckets
    buckets = [
        ("low", 0, 40),
        ("medium", 40, 60),
        ("high", 60, 80),
        ("critical", 80, 100),
    ]

    distribution = {}
    for name, low, high in buckets:
        query = select(func.count(RiskScore.id)).where(
            RiskScore.tenant_id == tenant.id,
            RiskScore.score >= low,
            RiskScore.score < high,
        )
        count = (await db.execute(query)).scalar() or 0
        distribution[name] = count

    return {
        "top_risks": top_risks,
        "distribution": distribution,
    }


@router.get("/sync-status")
async def get_sync_status(
    current_user: CurrentUser,
) -> dict[str, Any]:
    """Get data sync status and history."""
    import json
    from pathlib import Path

    sync_log_file = Path("/root/cortex-ci/data/sanctions/sync_log.json")

    if not sync_log_file.exists():
        return {
            "status": "no_sync_history",
            "message": "No sync has been performed yet",
            "last_sync": None,
            "history": [],
        }

    try:
        with open(sync_log_file) as f:
            sync_log = json.load(f)

        syncs = sync_log.get("syncs", [])
        last_sync = syncs[-1] if syncs else None

        return {
            "status": "ok",
            "last_sync": last_sync,
            "total_syncs": len(syncs),
            "history": syncs[-10:],  # Last 10 syncs
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e),
        }
