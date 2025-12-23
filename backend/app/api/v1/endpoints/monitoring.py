"""
Monitoring and alerting endpoints for CORTEX-CI.
Provides system health, metrics, and alert management.
"""
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import text, func
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database import get_db
from app.models.entity import Entity
from app.models.constraint import Constraint
from app.models.dependency import Dependency
from app.models.risk import RiskScore
from app.models.audit import AuditLog
from app.models.scenario_chain import ScenarioChain
from app.models.ai_analysis import AIAnalysis, AnomalyDetection

router = APIRouter()


class SystemHealth(BaseModel):
    status: str
    database: str
    timestamp: str
    uptime_check: bool
    version: str


class SystemMetrics(BaseModel):
    entities_count: int
    constraints_count: int
    dependencies_count: int
    risk_scores_count: int
    scenario_chains_count: int
    ai_analyses_count: int
    pending_anomalies_count: int
    recent_audit_events: int
    high_risk_entities: int
    critical_constraints: int


class Alert(BaseModel):
    id: str
    type: str
    severity: str
    message: str
    entity_id: Optional[str] = None
    created_at: str
    is_acknowledged: bool = False


class AlertsResponse(BaseModel):
    alerts: List[Alert]
    total_count: int
    unacknowledged_count: int


@router.get("/health", response_model=SystemHealth)
async def detailed_health_check(db: AsyncSession = Depends(get_db)):
    """Comprehensive health check including database connectivity."""
    try:
        # Test database connection
        result = await db.execute(text("SELECT 1"))
        db_status = "connected" if result.scalar() == 1 else "error"
    except Exception as e:
        db_status = f"error: {str(e)}"

    return SystemHealth(
        status="healthy" if db_status == "connected" else "degraded",
        database=db_status,
        timestamp=datetime.utcnow().isoformat(),
        uptime_check=True,
        version="2.0.0"  # Phase 2
    )


@router.get("/metrics", response_model=SystemMetrics)
async def get_system_metrics(db: AsyncSession = Depends(get_db)):
    """Get current system metrics and counts."""
    try:
        # Entity count
        entities_result = await db.execute(
            text("SELECT COUNT(*) FROM entities WHERE is_active = true")
        )
        entities_count = entities_result.scalar() or 0

        # Constraints count
        constraints_result = await db.execute(
            text("SELECT COUNT(*) FROM constraints WHERE is_active = true")
        )
        constraints_count = constraints_result.scalar() or 0

        # Dependencies count
        deps_result = await db.execute(
            text("SELECT COUNT(*) FROM dependencies")
        )
        dependencies_count = deps_result.scalar() or 0

        # Risk scores count
        risks_result = await db.execute(
            text("SELECT COUNT(*) FROM risk_scores")
        )
        risk_scores_count = risks_result.scalar() or 0

        # High risk entities
        high_risk_result = await db.execute(
            text("SELECT COUNT(*) FROM risk_scores WHERE score >= 70")
        )
        high_risk_entities = high_risk_result.scalar() or 0

        # Critical constraints
        critical_result = await db.execute(
            text("SELECT COUNT(*) FROM constraints WHERE severity = 'critical' AND is_active = true")
        )
        critical_constraints = critical_result.scalar() or 0

        # Scenario chains count (Phase 2)
        try:
            chains_result = await db.execute(
                text("SELECT COUNT(*) FROM scenario_chains")
            )
            scenario_chains_count = chains_result.scalar() or 0
        except:
            scenario_chains_count = 0

        # AI analyses count (Phase 2)
        try:
            ai_result = await db.execute(
                text("SELECT COUNT(*) FROM ai_analyses")
            )
            ai_analyses_count = ai_result.scalar() or 0
        except:
            ai_analyses_count = 0

        # Pending anomalies (Phase 2)
        try:
            anomalies_result = await db.execute(
                text("SELECT COUNT(*) FROM anomaly_detections WHERE is_confirmed IS NULL")
            )
            pending_anomalies_count = anomalies_result.scalar() or 0
        except:
            pending_anomalies_count = 0

        # Recent audit events (last 24h)
        recent_audit_result = await db.execute(
            text("""
                SELECT COUNT(*) FROM audit_logs
                WHERE created_at >= NOW() - INTERVAL '24 hours'
            """)
        )
        recent_audit_events = recent_audit_result.scalar() or 0

        return SystemMetrics(
            entities_count=entities_count,
            constraints_count=constraints_count,
            dependencies_count=dependencies_count,
            risk_scores_count=risk_scores_count,
            scenario_chains_count=scenario_chains_count,
            ai_analyses_count=ai_analyses_count,
            pending_anomalies_count=pending_anomalies_count,
            recent_audit_events=recent_audit_events,
            high_risk_entities=high_risk_entities,
            critical_constraints=critical_constraints
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch metrics: {str(e)}")


@router.get("/alerts", response_model=AlertsResponse)
async def get_alerts(
    severity: Optional[str] = None,
    acknowledged: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """Get system alerts based on current data conditions."""
    alerts = []

    try:
        # Alert 1: High risk entities exceeding threshold
        high_risk_result = await db.execute(
            text("""
                SELECT e.id, e.name, rs.score
                FROM entities e
                JOIN risk_scores rs ON e.id = rs.entity_id
                WHERE rs.score >= 80
                ORDER BY rs.score DESC
                LIMIT 10
            """)
        )
        for row in high_risk_result.fetchall():
            alerts.append(Alert(
                id=f"high-risk-{row[0]}",
                type="high_risk",
                severity="critical" if row[2] >= 90 else "high",
                message=f"Entity '{row[1]}' has critical risk score: {row[2]:.1f}",
                entity_id=str(row[0]),
                created_at=datetime.utcnow().isoformat(),
                is_acknowledged=False
            ))

        # Alert 2: Pending AI anomalies requiring review
        try:
            anomalies_result = await db.execute(
                text("""
                    SELECT id, entity_id, anomaly_type, description
                    FROM anomaly_detections
                    WHERE is_confirmed IS NULL
                    LIMIT 5
                """)
            )
            for row in anomalies_result.fetchall():
                alerts.append(Alert(
                    id=f"anomaly-{row[0]}",
                    type="pending_anomaly",
                    severity="medium",
                    message=f"Unreviewed anomaly: {row[2]} - {row[3][:100]}...",
                    entity_id=str(row[1]) if row[1] else None,
                    created_at=datetime.utcnow().isoformat(),
                    is_acknowledged=False
                ))
        except:
            pass

        # Alert 3: AI analyses awaiting approval
        try:
            ai_pending_result = await db.execute(
                text("""
                    SELECT id, analysis_type, description
                    FROM ai_analyses
                    WHERE status = 'completed' AND requires_human_approval = true
                    AND approved_by IS NULL AND rejection_reason IS NULL
                    LIMIT 5
                """)
            )
            for row in ai_pending_result.fetchall():
                alerts.append(Alert(
                    id=f"ai-approval-{row[0]}",
                    type="ai_pending_approval",
                    severity="medium",
                    message=f"AI {row[1]} analysis awaiting approval: {row[2][:80]}...",
                    created_at=datetime.utcnow().isoformat(),
                    is_acknowledged=False
                ))
        except:
            pass

        # Alert 4: Check for entities with no recent risk calculation
        stale_risk_result = await db.execute(
            text("""
                SELECT COUNT(*)
                FROM entities e
                LEFT JOIN risk_scores rs ON e.id = rs.entity_id
                WHERE e.is_active = true
                AND (rs.calculated_at IS NULL OR rs.calculated_at < NOW() - INTERVAL '7 days')
            """)
        )
        stale_count = stale_risk_result.scalar() or 0
        if stale_count > 100:
            alerts.append(Alert(
                id="stale-risk-scores",
                type="stale_data",
                severity="low",
                message=f"{stale_count} entities have stale or missing risk scores (>7 days old)",
                created_at=datetime.utcnow().isoformat(),
                is_acknowledged=False
            ))

        # Filter by severity if specified
        if severity:
            alerts = [a for a in alerts if a.severity == severity]

        return AlertsResponse(
            alerts=alerts,
            total_count=len(alerts),
            unacknowledged_count=sum(1 for a in alerts if not a.is_acknowledged)
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate alerts: {str(e)}")


@router.get("/dashboard")
async def monitoring_dashboard(db: AsyncSession = Depends(get_db)):
    """Get combined monitoring dashboard data."""
    health = await detailed_health_check(db)
    metrics = await get_system_metrics(db)
    alerts = await get_alerts(db=db)

    return {
        "health": health,
        "metrics": metrics,
        "alerts": {
            "total": alerts.total_count,
            "unacknowledged": alerts.unacknowledged_count,
            "critical": sum(1 for a in alerts.alerts if a.severity == "critical"),
            "recent": alerts.alerts[:5]
        },
        "generated_at": datetime.utcnow().isoformat()
    }
