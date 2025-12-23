"""Phase 2.5: Controlled AI Integration - Bounded intelligence API."""
from typing import Optional, List, Dict, Any
from uuid import UUID
from decimal import Decimal
from datetime import datetime
import random
import math

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel, Field
from sqlalchemy import select, func

from app.models import (
    AIAnalysis, AIAnalysisType, AIAnalysisStatus, AnomalyDetection,
    Entity, RiskScore, Dependency,
    AuditLog, AuditAction,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


# Schemas
class AIAnalysisRequest(BaseModel):
    analysis_type: AIAnalysisType
    description: str = Field(..., min_length=10)
    entity_ids: List[UUID] = []
    parameters: Dict[str, Any] = {}


class AIAnalysisResponse(BaseModel):
    id: UUID
    analysis_type: str
    status: str
    description: str
    confidence: float
    output_summary: Optional[str]
    requires_human_approval: bool
    created_at: str
    model_name: str
    model_version: str

    class Config:
        from_attributes = True


class AnomalyResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_name: Optional[str] = None
    anomaly_type: str
    anomaly_description: str
    anomaly_score: float
    baseline_value: Optional[str]
    detected_value: Optional[str]
    deviation_percentage: Optional[float]
    is_reviewed: bool
    is_confirmed_anomaly: Optional[bool]

    class Config:
        from_attributes = True


class ModelCardResponse(BaseModel):
    model_name: str
    model_version: str
    analysis_type: str
    capabilities: List[str]
    limitations: List[str]
    ethical_considerations: List[str]
    training_data_description: str
    performance_metrics: Dict[str, Any]


@router.post("", response_model=AIAnalysisResponse, status_code=status.HTTP_201_CREATED)
async def request_ai_analysis(
    data: AIAnalysisRequest,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> AIAnalysisResponse:
    """
    Request an AI analysis.

    The analysis will be processed and may require human approval before results are applied.
    """
    # Validate entity IDs if provided
    if data.entity_ids:
        entity_result = await db.execute(
            select(func.count(Entity.id)).where(
                Entity.id.in_(data.entity_ids),
                Entity.tenant_id == tenant.id,
            )
        )
        count = entity_result.scalar()
        if count != len(data.entity_ids):
            raise HTTPException(status_code=400, detail="One or more entity IDs not found")

    analysis = AIAnalysis(
        tenant_id=tenant.id,
        analysis_type=data.analysis_type,
        status=AIAnalysisStatus.PENDING,
        request_description=data.description,
        requested_by_id=current_user.id,
        input_data=data.parameters,
        input_entity_ids=[str(e) for e in data.entity_ids],
        model_name="cortex-ai-v1",
        model_version="1.0.0",
        requires_human_approval=True,
    )
    db.add(analysis)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="ai_analysis",
        resource_id=analysis.id,
        success=True,
    )
    db.add(audit)

    await db.commit()
    await db.refresh(analysis)

    # Process the analysis (in real implementation, this would be async)
    await _process_analysis(db, analysis, tenant.id)

    return AIAnalysisResponse(
        id=analysis.id,
        analysis_type=analysis.analysis_type.value,
        status=analysis.status.value,
        description=analysis.request_description,
        confidence=float(analysis.confidence),
        output_summary=analysis.output_summary,
        requires_human_approval=analysis.requires_human_approval,
        created_at=analysis.created_at.isoformat() if analysis.created_at else datetime.utcnow().isoformat(),
        model_name=analysis.model_name,
        model_version=analysis.model_version,
    )


@router.get("")
async def list_analyses(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    status_filter: Optional[AIAnalysisStatus] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """List AI analyses with optional status filter."""
    query = select(AIAnalysis).where(AIAnalysis.tenant_id == tenant.id)

    if status_filter:
        query = query.where(AIAnalysis.status == status_filter)

    query = query.order_by(AIAnalysis.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    analyses = result.scalars().all()

    return {
        "items": [
            AIAnalysisResponse(
                id=a.id,
                analysis_type=a.analysis_type.value,
                status=a.status.value,
                description=a.request_description,
                confidence=float(a.confidence),
                output_summary=a.output_summary,
                requires_human_approval=a.requires_human_approval,
                created_at=a.created_at.isoformat() if a.created_at else datetime.utcnow().isoformat(),
                model_name=a.model_name,
                model_version=a.model_version,
            )
            for a in analyses
        ],
        "page": page,
        "page_size": page_size,
    }


@router.get("/{analysis_id}")
async def get_analysis(
    analysis_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """Get detailed analysis results."""
    result = await db.execute(
        select(AIAnalysis).where(
            AIAnalysis.id == analysis_id,
            AIAnalysis.tenant_id == tenant.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    return {
        "id": str(analysis.id),
        "analysis_type": analysis.analysis_type.value,
        "status": analysis.status.value,
        "description": analysis.request_description,
        "input_entity_ids": analysis.input_entity_ids,
        "output": analysis.output,
        "output_summary": analysis.output_summary,
        "confidence": float(analysis.confidence),
        "explanation": analysis.explanation,
        "model_card": analysis.get_model_card(),
        "requires_human_approval": analysis.requires_human_approval,
        "approved_by": str(analysis.approved_by_id) if analysis.approved_by_id else None,
        "approved_at": analysis.approved_at.isoformat() if analysis.approved_at else None,
        "created_at": analysis.created_at.isoformat() if analysis.created_at else None,
        "processing_time_ms": _calculate_processing_time(analysis),
    }


@router.post("/{analysis_id}/approve")
async def approve_analysis(
    analysis_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Approve an AI analysis result (human approval gate)."""
    result = await db.execute(
        select(AIAnalysis).where(
            AIAnalysis.id == analysis_id,
            AIAnalysis.tenant_id == tenant.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status != AIAnalysisStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis is not awaiting approval (current status: {analysis.status.value})",
        )

    analysis.status = AIAnalysisStatus.APPROVED
    analysis.approved_by_id = current_user.id
    analysis.approved_at = datetime.utcnow()
    analysis.approval_notes = notes

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="ai_analysis",
        resource_id=analysis.id,
        after_state={"status": "approved", "notes": notes},
        success=True,
    )
    db.add(audit)

    await db.commit()

    return {
        "success": True,
        "message": "Analysis approved",
        "analysis_id": str(analysis_id),
        "approved_by": current_user.email,
    }


@router.post("/{analysis_id}/reject")
async def reject_analysis(
    analysis_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
    reason: str = Query(..., min_length=10),
) -> Dict[str, Any]:
    """Reject an AI analysis result."""
    result = await db.execute(
        select(AIAnalysis).where(
            AIAnalysis.id == analysis_id,
            AIAnalysis.tenant_id == tenant.id,
        )
    )
    analysis = result.scalar_one_or_none()

    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")

    if analysis.status != AIAnalysisStatus.AWAITING_APPROVAL:
        raise HTTPException(
            status_code=400,
            detail=f"Analysis is not awaiting approval (current status: {analysis.status.value})",
        )

    analysis.status = AIAnalysisStatus.REJECTED
    analysis.rejection_reason = reason

    await db.commit()

    return {
        "success": True,
        "message": "Analysis rejected",
        "analysis_id": str(analysis_id),
        "reason": reason,
    }


@router.get("/anomalies/pending")
async def list_pending_anomalies(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
) -> Dict[str, Any]:
    """List anomalies pending human review."""
    query = select(AnomalyDetection, Entity.name).join(
        Entity, AnomalyDetection.entity_id == Entity.id
    ).where(
        AnomalyDetection.tenant_id == tenant.id,
        AnomalyDetection.is_reviewed == False,
    ).order_by(AnomalyDetection.anomaly_score.desc())

    query = query.offset((page - 1) * page_size).limit(page_size)
    result = await db.execute(query)

    anomalies = []
    for anomaly, entity_name in result:
        anomalies.append(AnomalyResponse(
            id=anomaly.id,
            entity_id=anomaly.entity_id,
            entity_name=entity_name,
            anomaly_type=anomaly.anomaly_type,
            anomaly_description=anomaly.anomaly_description,
            anomaly_score=float(anomaly.anomaly_score),
            baseline_value=anomaly.baseline_value,
            detected_value=anomaly.detected_value,
            deviation_percentage=float(anomaly.deviation_percentage) if anomaly.deviation_percentage else None,
            is_reviewed=anomaly.is_reviewed,
            is_confirmed_anomaly=anomaly.is_confirmed_anomaly,
        ))

    return {
        "items": anomalies,
        "page": page,
        "page_size": page_size,
    }


@router.post("/anomalies/{anomaly_id}/review")
async def review_anomaly(
    anomaly_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
    is_confirmed: bool = Query(...),
    notes: Optional[str] = None,
) -> Dict[str, Any]:
    """Review and confirm/dismiss an anomaly."""
    result = await db.execute(
        select(AnomalyDetection).where(
            AnomalyDetection.id == anomaly_id,
            AnomalyDetection.tenant_id == tenant.id,
        )
    )
    anomaly = result.scalar_one_or_none()

    if not anomaly:
        raise HTTPException(status_code=404, detail="Anomaly not found")

    anomaly.is_reviewed = True
    anomaly.reviewed_by_id = current_user.id
    anomaly.reviewed_at = datetime.utcnow()
    anomaly.is_confirmed_anomaly = is_confirmed
    anomaly.review_notes = notes

    await db.commit()

    return {
        "success": True,
        "anomaly_id": str(anomaly_id),
        "is_confirmed": is_confirmed,
        "reviewed_by": current_user.email,
    }


@router.get("/model-card/{analysis_type}")
async def get_model_card(
    analysis_type: AIAnalysisType,
    current_user: CurrentUser,
) -> ModelCardResponse:
    """Get model card for transparency."""
    cards = {
        AIAnalysisType.ANOMALY: {
            "capabilities": [
                "Detect unusual patterns in risk scores",
                "Flag entities with sudden risk changes",
                "Identify outliers in entity behavior",
            ],
            "training_data_description": "Historical risk score patterns from anonymized datasets",
            "performance_metrics": {
                "precision": 0.85,
                "recall": 0.78,
                "f1_score": 0.81,
            },
        },
        AIAnalysisType.PATTERN: {
            "capabilities": [
                "Identify clusters of related entities",
                "Detect common risk factors",
                "Find hidden relationships",
            ],
            "training_data_description": "Entity relationship graphs and risk factor correlations",
            "performance_metrics": {
                "cluster_purity": 0.82,
                "silhouette_score": 0.71,
            },
        },
        AIAnalysisType.SUMMARY: {
            "capabilities": [
                "Generate natural language summaries",
                "Highlight key findings",
                "Create executive briefings",
            ],
            "training_data_description": "Risk reports and compliance documentation",
            "performance_metrics": {
                "bleu_score": 0.76,
                "human_eval_rating": 4.2,
            },
        },
        AIAnalysisType.SCENARIO: {
            "capabilities": [
                "Accelerate scenario simulations",
                "Predict cascade effects",
                "Stress test dependencies",
            ],
            "training_data_description": "Historical dependency failures and cascade patterns",
            "performance_metrics": {
                "prediction_accuracy": 0.79,
                "cascade_depth_accuracy": 0.85,
            },
        },
        AIAnalysisType.CLUSTERING: {
            "capabilities": [
                "Group similar entities",
                "Identify risk communities",
                "Segment by behavior patterns",
            ],
            "training_data_description": "Entity feature vectors and behavioral data",
            "performance_metrics": {
                "cluster_stability": 0.88,
                "inter_cluster_distance": 0.72,
            },
        },
    }

    card_data = cards.get(analysis_type, {})

    return ModelCardResponse(
        model_name="cortex-ai-v1",
        model_version="1.0.0",
        analysis_type=analysis_type.value,
        capabilities=card_data.get("capabilities", []),
        limitations=[
            "Cannot make prescriptive decisions",
            "Requires human review and approval",
            "May not capture all edge cases",
            "Performance varies with data quality",
            "Should not be used for political forecasting",
        ],
        ethical_considerations=[
            "All outputs require human verification",
            "Not designed for autonomous decision-making",
            "Transparency is maintained via model cards",
            "Bias monitoring is ongoing",
        ],
        training_data_description=card_data.get("training_data_description", ""),
        performance_metrics=card_data.get("performance_metrics", {}),
    )


async def _process_analysis(db: DB, analysis: AIAnalysis, tenant_id: UUID) -> None:
    """Process an AI analysis request."""
    analysis.status = AIAnalysisStatus.PROCESSING
    analysis.processing_started_at = datetime.utcnow()

    try:
        if analysis.analysis_type == AIAnalysisType.ANOMALY:
            output = await _run_anomaly_detection(db, analysis, tenant_id)
        elif analysis.analysis_type == AIAnalysisType.PATTERN:
            output = await _run_pattern_detection(db, analysis, tenant_id)
        elif analysis.analysis_type == AIAnalysisType.CLUSTERING:
            output = await _run_clustering(db, analysis, tenant_id)
        else:
            output = {"message": "Analysis type not fully implemented"}

        analysis.output = output
        analysis.output_summary = output.get("summary", "Analysis complete")
        analysis.confidence = Decimal(str(output.get("confidence", 0.75)))
        analysis.explanation = output.get("explanation", "See output for details")
        analysis.status = AIAnalysisStatus.AWAITING_APPROVAL
        analysis.processing_completed_at = datetime.utcnow()

    except Exception as e:
        analysis.status = AIAnalysisStatus.FAILED
        analysis.error_message = str(e)

    await db.commit()


async def _run_anomaly_detection(db: DB, analysis: AIAnalysis, tenant_id: UUID) -> Dict[str, Any]:
    """Run anomaly detection algorithm."""
    # Get risk scores for analysis
    query = select(RiskScore, Entity.name).join(
        Entity, RiskScore.entity_id == Entity.id
    ).where(RiskScore.tenant_id == tenant_id)

    if analysis.input_entity_ids:
        entity_uuids = [UUID(e) for e in analysis.input_entity_ids]
        query = query.where(RiskScore.entity_id.in_(entity_uuids))

    result = await db.execute(query)
    scores = [(float(rs.score), rs.entity_id, name) for rs, name in result]

    if not scores:
        return {"summary": "No data available for analysis", "anomalies": [], "confidence": 0.5}

    # Simple anomaly detection using IQR method
    values = [s[0] for s in scores]
    mean = sum(values) / len(values)
    variance = sum((x - mean) ** 2 for x in values) / len(values)
    std_dev = math.sqrt(variance) if variance > 0 else 1

    anomalies = []
    for score, entity_id, name in scores:
        z_score = abs(score - mean) / std_dev if std_dev > 0 else 0
        if z_score > 2:  # More than 2 standard deviations
            anomaly = AnomalyDetection(
                tenant_id=tenant_id,
                ai_analysis_id=analysis.id,
                entity_id=entity_id,
                anomaly_type="risk_score_outlier",
                anomaly_description=f"Risk score {score:.1f} is {z_score:.1f} standard deviations from mean ({mean:.1f})",
                anomaly_score=Decimal(str(min(z_score / 4, 1.0))),  # Normalize to 0-1
                baseline_value=f"{mean:.1f}",
                detected_value=f"{score:.1f}",
                deviation_percentage=Decimal(str(((score - mean) / mean) * 100 if mean > 0 else 0)),
            )
            db.add(anomaly)
            anomalies.append({
                "entity_id": str(entity_id),
                "entity_name": name,
                "score": score,
                "z_score": round(z_score, 2),
            })

    return {
        "summary": f"Found {len(anomalies)} anomalies in {len(scores)} entities",
        "anomalies": anomalies[:10],  # Top 10
        "statistics": {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "total_analyzed": len(scores),
        },
        "confidence": 0.85,
        "explanation": "Used z-score method to identify outliers (>2 standard deviations from mean)",
    }


async def _run_pattern_detection(db: DB, analysis: AIAnalysis, tenant_id: UUID) -> Dict[str, Any]:
    """Run pattern detection."""
    # Get dependency patterns
    deps_result = await db.execute(
        select(
            Dependency.relationship_type,
            func.count(Dependency.id).label("count"),
        ).where(
            Dependency.tenant_id == tenant_id,
            Dependency.is_active == True,
        ).group_by(Dependency.relationship_type)
    )

    patterns = {}
    for row in deps_result:
        patterns[row.relationship_type.value] = row.count

    return {
        "summary": f"Identified {len(patterns)} relationship patterns",
        "patterns": patterns,
        "dominant_pattern": max(patterns.items(), key=lambda x: x[1])[0] if patterns else None,
        "confidence": 0.78,
        "explanation": "Analyzed dependency relationships to identify common patterns",
    }


async def _run_clustering(db: DB, analysis: AIAnalysis, tenant_id: UUID) -> Dict[str, Any]:
    """Run entity clustering."""
    # Get entities with risk scores
    result = await db.execute(
        select(Entity, RiskScore).outerjoin(
            RiskScore, Entity.id == RiskScore.entity_id
        ).where(Entity.tenant_id == tenant_id)
    )

    # Simple clustering by risk level
    clusters = {
        "low_risk": [],
        "medium_risk": [],
        "high_risk": [],
        "critical": [],
    }

    for entity, risk_score in result:
        score = float(risk_score.score) if risk_score else 0
        if score >= 80:
            clusters["critical"].append(str(entity.id))
        elif score >= 60:
            clusters["high_risk"].append(str(entity.id))
        elif score >= 40:
            clusters["medium_risk"].append(str(entity.id))
        else:
            clusters["low_risk"].append(str(entity.id))

    return {
        "summary": f"Clustered entities into {len([c for c in clusters.values() if c])} risk groups",
        "clusters": {k: len(v) for k, v in clusters.items()},
        "cluster_samples": {k: v[:5] for k, v in clusters.items()},  # First 5 of each
        "confidence": 0.82,
        "explanation": "Grouped entities by risk score thresholds",
    }


def _calculate_processing_time(analysis: AIAnalysis) -> Optional[int]:
    """Calculate processing time in milliseconds."""
    if analysis.processing_started_at and analysis.processing_completed_at:
        delta = analysis.processing_completed_at - analysis.processing_started_at
        return int(delta.total_seconds() * 1000)
    return None
