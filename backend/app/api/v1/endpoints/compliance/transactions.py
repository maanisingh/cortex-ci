"""
Transaction Monitoring API Endpoints
AML transaction monitoring, alerts, and rules management
"""

from datetime import UTC, datetime
from decimal import Decimal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.transaction import (
    AlertSeverity,
    AlertStatus,
    MonitoringRule,
    RuleType,
    Transaction,
    TransactionAlert,
    TransactionStatus,
)

router = APIRouter()


class TransactionCreate(BaseModel):
    transaction_ref: str
    transaction_type: str
    amount: Decimal
    currency: str = "USD"
    direction: str  # INBOUND, OUTBOUND
    originator_name: str | None = None
    originator_bank_country: str | None = None
    beneficiary_name: str | None = None
    beneficiary_bank_country: str | None = None
    purpose: str | None = None
    customer_id: UUID | None = None


class TransactionResponse(BaseModel):
    id: UUID
    transaction_ref: str
    transaction_type: str
    status: str
    amount: Decimal
    currency: str
    direction: str
    originator_name: str | None
    beneficiary_name: str | None
    risk_score: float
    has_alert: bool
    initiated_at: datetime

    class Config:
        from_attributes = True


class AlertResponse(BaseModel):
    id: UUID
    transaction_id: UUID
    rule_name: str
    severity: str
    status: str
    title: str
    description: str
    triggered_at: datetime

    class Config:
        from_attributes = True


class MonitoringRuleResponse(BaseModel):
    id: UUID
    rule_code: str
    name: str
    description: str
    rule_type: str
    category: str
    default_severity: str
    is_active: bool
    total_alerts: int
    precision_rate: float | None

    class Config:
        from_attributes = True


@router.post("/", response_model=TransactionResponse, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    txn: TransactionCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Create and analyze a transaction."""
    # Calculate risk score
    risk_score = 0.0
    risk_factors = []

    # High-risk country check
    high_risk = ["KP", "IR", "MM", "SY"]
    if txn.originator_bank_country and txn.originator_bank_country.upper() in high_risk:
        risk_score += 40
        risk_factors.append("HIGH_RISK_ORIGINATOR_COUNTRY")
    if txn.beneficiary_bank_country and txn.beneficiary_bank_country.upper() in high_risk:
        risk_score += 40
        risk_factors.append("HIGH_RISK_BENEFICIARY_COUNTRY")

    # Large amount check
    if txn.amount >= 10000:
        risk_score += 20
        risk_factors.append("LARGE_TRANSACTION")

    db_txn = Transaction(
        id=uuid4(),
        tenant_id=tenant_id,
        customer_id=txn.customer_id,
        transaction_ref=txn.transaction_ref,
        transaction_type=txn.transaction_type,
        status=TransactionStatus.COMPLETED,
        amount=txn.amount,
        currency=txn.currency,
        direction=txn.direction,
        originator_name=txn.originator_name,
        originator_bank_country=txn.originator_bank_country,
        beneficiary_name=txn.beneficiary_name,
        beneficiary_bank_country=txn.beneficiary_bank_country,
        purpose=txn.purpose,
        risk_score=risk_score,
        risk_factors=risk_factors,
        initiated_at=datetime.now(UTC),
        has_alert=risk_score >= 50,
    )

    db.add(db_txn)

    # Create alert if high risk
    if risk_score >= 50:
        alert = TransactionAlert(
            id=uuid4(),
            tenant_id=tenant_id,
            transaction_id=db_txn.id,
            rule_name="HIGH_RISK_TRANSACTION",
            rule_type=RuleType.THRESHOLD,
            severity=AlertSeverity.HIGH if risk_score >= 70 else AlertSeverity.MEDIUM,
            status=AlertStatus.NEW,
            title=f"High-risk transaction detected: {txn.transaction_ref}",
            description=f"Risk factors: {', '.join(risk_factors)}",
            triggered_at=datetime.now(UTC),
        )
        db.add(alert)
        db_txn.alert_count = 1

    await db.commit()
    await db.refresh(db_txn)
    return db_txn


@router.get("/", response_model=list[TransactionResponse])
async def list_transactions(
    customer_id: UUID | None = Query(None),
    status: str | None = Query(None),
    has_alert: bool | None = Query(None),
    min_amount: Decimal | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List transactions with filters."""
    query = select(Transaction).where(Transaction.tenant_id == tenant_id)

    if customer_id:
        query = query.where(Transaction.customer_id == customer_id)
    if status:
        query = query.where(Transaction.status == status)
    if has_alert is not None:
        query = query.where(Transaction.has_alert == has_alert)
    if min_amount:
        query = query.where(Transaction.amount >= min_amount)

    result = await db.execute(
        query.order_by(Transaction.initiated_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/alerts", response_model=list[AlertResponse])
async def list_alerts(
    status: str | None = Query(None),
    severity: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List transaction alerts."""
    query = select(TransactionAlert).where(TransactionAlert.tenant_id == tenant_id)

    if status:
        query = query.where(TransactionAlert.status == status)
    if severity:
        query = query.where(TransactionAlert.severity == severity)

    result = await db.execute(
        query.order_by(TransactionAlert.triggered_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.patch("/alerts/{alert_id}/status")
async def update_alert_status(
    alert_id: UUID,
    new_status: str = Query(...),
    notes: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Update alert status."""
    result = await db.execute(
        select(TransactionAlert).where(
            and_(TransactionAlert.id == alert_id, TransactionAlert.tenant_id == tenant_id)
        )
    )
    alert = result.scalar_one_or_none()
    if not alert:
        raise HTTPException(status_code=404, detail="Alert not found")

    alert.status = new_status
    if notes:
        alert.investigation_notes = notes
    if new_status in ["CLOSED_LEGITIMATE", "CLOSED_SUSPICIOUS", "SAR_FILED"]:
        alert.closed_at = datetime.now(UTC)

    await db.commit()
    return {"message": "Alert status updated", "alert_id": str(alert_id)}


@router.get("/rules", response_model=list[MonitoringRuleResponse])
async def list_monitoring_rules(
    category: str | None = Query(None),
    is_active: bool = Query(True),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List monitoring rules."""
    query = select(MonitoringRule).where(
        and_(MonitoringRule.tenant_id == tenant_id, MonitoringRule.is_active == is_active)
    )
    if category:
        query = query.where(MonitoringRule.category == category)

    result = await db.execute(query.order_by(MonitoringRule.rule_code))
    return result.scalars().all()


@router.get("/stats")
async def get_transaction_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get transaction monitoring statistics."""
    # Total transactions
    total = await db.execute(
        select(func.count(Transaction.id)).where(Transaction.tenant_id == tenant_id)
    )

    # Alerts by status
    alert_counts = await db.execute(
        select(TransactionAlert.status, func.count(TransactionAlert.id))
        .where(TransactionAlert.tenant_id == tenant_id)
        .group_by(TransactionAlert.status)
    )

    # Total volume
    volume = await db.execute(
        select(func.sum(Transaction.amount)).where(Transaction.tenant_id == tenant_id)
    )

    return {
        "total_transactions": total.scalar() or 0,
        "total_volume": float(volume.scalar() or 0),
        "alerts_by_status": {row[0]: row[1] for row in alert_counts.fetchall()},
    }
