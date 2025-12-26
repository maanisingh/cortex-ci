"""Transaction Monitoring Service

Real-time and batch transaction monitoring for AML compliance.
Evaluates transactions against configurable rules and generates alerts.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timezone, timedelta
from uuid import UUID, uuid4
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_

from app.models.compliance.transaction import (
    Transaction, TransactionType, TransactionStatus,
    TransactionAlert, AlertStatus, AlertPriority,
    MonitoringRule, RuleType
)
from app.models.compliance.customer import Customer

logger = logging.getLogger(__name__)


class TransactionMonitoringService:
    """Service for monitoring transactions and generating AML alerts"""

    def __init__(self):
        self.rules_cache: Dict[UUID, List[MonitoringRule]] = {}
        self.cache_ttl = 300  # 5 minutes

    async def load_rules(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        force_refresh: bool = False
    ) -> List[MonitoringRule]:
        """Load active monitoring rules for tenant"""
        if not force_refresh and tenant_id in self.rules_cache:
            return self.rules_cache[tenant_id]

        result = await db.execute(
            select(MonitoringRule).where(
                and_(
                    MonitoringRule.tenant_id == tenant_id,
                    MonitoringRule.is_active == True
                )
            ).order_by(MonitoringRule.priority)
        )
        rules = result.scalars().all()
        self.rules_cache[tenant_id] = list(rules)
        return list(rules)

    async def evaluate_transaction(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
    ) -> List[TransactionAlert]:
        """
        Evaluate a single transaction against all active rules.

        Returns list of generated alerts.
        """
        rules = await self.load_rules(db, tenant_id)
        alerts = []

        for rule in rules:
            triggered, details = await self._evaluate_rule(
                db, tenant_id, transaction, rule
            )
            if triggered:
                alert = await self._create_alert(
                    db, tenant_id, transaction, rule, details
                )
                alerts.append(alert)

        return alerts

    async def _evaluate_rule(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        rule: MonitoringRule,
    ) -> tuple[bool, Dict[str, Any]]:
        """Evaluate a single rule against a transaction"""
        config = rule.rule_config or {}
        details = {"rule_name": rule.name, "rule_type": rule.rule_type}

        try:
            if rule.rule_type == RuleType.THRESHOLD:
                return await self._check_threshold(transaction, config, details)

            elif rule.rule_type == RuleType.VELOCITY:
                return await self._check_velocity(
                    db, tenant_id, transaction, config, details
                )

            elif rule.rule_type == RuleType.GEOGRAPHIC:
                return await self._check_geographic(transaction, config, details)

            elif rule.rule_type == RuleType.PATTERN:
                return await self._check_pattern(
                    db, tenant_id, transaction, config, details
                )

            elif rule.rule_type == RuleType.STRUCTURING:
                return await self._check_structuring(
                    db, tenant_id, transaction, config, details
                )

            elif rule.rule_type == RuleType.DORMANT:
                return await self._check_dormant_account(
                    db, tenant_id, transaction, config, details
                )

            elif rule.rule_type == RuleType.BEHAVIORAL:
                return await self._check_behavioral(
                    db, tenant_id, transaction, config, details
                )

        except Exception as e:
            logger.error(f"Rule evaluation failed: {rule.name} - {e}")
            return False, {"error": str(e)}

        return False, details

    async def _check_threshold(
        self,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Check if transaction exceeds threshold"""
        threshold = Decimal(str(config.get("threshold", 10000)))
        currency = config.get("currency")

        if currency and transaction.currency != currency:
            return False, details

        if transaction.amount >= threshold:
            details["threshold"] = float(threshold)
            details["transaction_amount"] = float(transaction.amount)
            details["exceeded_by"] = float(transaction.amount - threshold)
            return True, details

        return False, details

    async def _check_velocity(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Check transaction velocity (count/amount over time)"""
        time_window_hours = config.get("time_window_hours", 24)
        max_count = config.get("max_count")
        max_amount = Decimal(str(config.get("max_amount", 0))) if config.get("max_amount") else None

        start_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)

        # Get recent transactions for same customer
        query = select(Transaction).where(
            and_(
                Transaction.tenant_id == tenant_id,
                Transaction.customer_id == transaction.customer_id,
                Transaction.transaction_date >= start_time,
                Transaction.id != transaction.id
            )
        )
        result = await db.execute(query)
        recent_txns = result.scalars().all()

        total_count = len(recent_txns) + 1  # Include current
        total_amount = sum(t.amount for t in recent_txns) + transaction.amount

        details["time_window_hours"] = time_window_hours
        details["transaction_count"] = total_count
        details["total_amount"] = float(total_amount)

        if max_count and total_count > max_count:
            details["max_count"] = max_count
            return True, details

        if max_amount and total_amount > max_amount:
            details["max_amount"] = float(max_amount)
            return True, details

        return False, details

    async def _check_geographic(
        self,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Check for high-risk geographic indicators"""
        high_risk_countries = config.get("high_risk_countries", [])

        # Check originator and beneficiary countries
        countries_involved = []
        if transaction.originator_country:
            countries_involved.append(transaction.originator_country)
        if transaction.beneficiary_country:
            countries_involved.append(transaction.beneficiary_country)

        matches = [c for c in countries_involved if c in high_risk_countries]

        if matches:
            details["high_risk_countries_involved"] = matches
            details["all_countries"] = countries_involved
            return True, details

        return False, details

    async def _check_structuring(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Detect potential structuring (smurfing) patterns"""
        reporting_threshold = Decimal(str(config.get("reporting_threshold", 10000)))
        time_window_hours = config.get("time_window_hours", 24)
        min_transactions = config.get("min_transactions", 3)
        proximity_percent = config.get("proximity_percent", 20)  # % below threshold

        start_time = datetime.now(timezone.utc) - timedelta(hours=time_window_hours)
        lower_bound = reporting_threshold * Decimal(str((100 - proximity_percent) / 100))

        # Find transactions just below threshold
        query = select(Transaction).where(
            and_(
                Transaction.tenant_id == tenant_id,
                Transaction.customer_id == transaction.customer_id,
                Transaction.transaction_date >= start_time,
                Transaction.amount >= lower_bound,
                Transaction.amount < reporting_threshold
            )
        )
        result = await db.execute(query)
        suspicious_txns = result.scalars().all()

        if len(suspicious_txns) >= min_transactions:
            total = sum(t.amount for t in suspicious_txns)
            details["structuring_detected"] = True
            details["transaction_count"] = len(suspicious_txns)
            details["total_amount"] = float(total)
            details["reporting_threshold"] = float(reporting_threshold)
            details["amounts"] = [float(t.amount) for t in suspicious_txns]
            return True, details

        return False, details

    async def _check_dormant_account(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Detect activity on dormant accounts"""
        dormant_days = config.get("dormant_days", 180)
        min_amount = Decimal(str(config.get("min_amount", 1000)))

        if transaction.amount < min_amount:
            return False, details

        cutoff = datetime.now(timezone.utc) - timedelta(days=dormant_days)

        # Check for recent activity
        query = select(func.count(Transaction.id)).where(
            and_(
                Transaction.tenant_id == tenant_id,
                Transaction.customer_id == transaction.customer_id,
                Transaction.transaction_date >= cutoff,
                Transaction.transaction_date < transaction.transaction_date,
                Transaction.id != transaction.id
            )
        )
        result = await db.execute(query)
        recent_count = result.scalar() or 0

        if recent_count == 0:
            details["dormant_period_days"] = dormant_days
            details["first_activity_after_dormancy"] = True
            details["transaction_amount"] = float(transaction.amount)
            return True, details

        return False, details

    async def _check_pattern(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Check for suspicious transaction patterns"""
        pattern_type = config.get("pattern_type", "round_amount")

        if pattern_type == "round_amount":
            # Check for suspiciously round amounts
            amount = transaction.amount
            if amount >= 1000 and amount % 1000 == 0:
                details["pattern"] = "round_amount"
                details["amount"] = float(amount)
                return True, details

        elif pattern_type == "rapid_movement":
            # Money in and out quickly
            time_window_minutes = config.get("time_window_minutes", 60)
            min_amount = Decimal(str(config.get("min_amount", 5000)))

            if transaction.amount < min_amount:
                return False, details

            start_time = transaction.transaction_date - timedelta(minutes=time_window_minutes)

            query = select(Transaction).where(
                and_(
                    Transaction.tenant_id == tenant_id,
                    Transaction.customer_id == transaction.customer_id,
                    Transaction.transaction_date >= start_time,
                    Transaction.transaction_date <= transaction.transaction_date,
                    Transaction.id != transaction.id,
                    Transaction.transaction_type != transaction.transaction_type
                )
            )
            result = await db.execute(query)
            related_txns = result.scalars().all()

            # Check for opposite direction transactions of similar amount
            for t in related_txns:
                if abs(t.amount - transaction.amount) / transaction.amount < 0.1:
                    details["pattern"] = "rapid_movement"
                    details["time_window_minutes"] = time_window_minutes
                    details["related_transaction_id"] = str(t.id)
                    return True, details

        return False, details

    async def _check_behavioral(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        config: Dict[str, Any],
        details: Dict[str, Any]
    ) -> tuple[bool, Dict[str, Any]]:
        """Detect behavioral anomalies"""
        # Calculate customer's historical average
        lookback_days = config.get("lookback_days", 90)
        deviation_multiplier = config.get("deviation_multiplier", 3)

        start_time = datetime.now(timezone.utc) - timedelta(days=lookback_days)

        query = select(
            func.avg(Transaction.amount),
            func.stddev(Transaction.amount)
        ).where(
            and_(
                Transaction.tenant_id == tenant_id,
                Transaction.customer_id == transaction.customer_id,
                Transaction.transaction_date >= start_time,
                Transaction.id != transaction.id
            )
        )
        result = await db.execute(query)
        row = result.first()

        if row and row[0] and row[1]:
            avg_amount = Decimal(str(row[0]))
            std_dev = Decimal(str(row[1]))

            if std_dev > 0:
                z_score = (transaction.amount - avg_amount) / std_dev
                if abs(z_score) > deviation_multiplier:
                    details["behavioral_anomaly"] = True
                    details["historical_avg"] = float(avg_amount)
                    details["std_deviation"] = float(std_dev)
                    details["z_score"] = float(z_score)
                    details["transaction_amount"] = float(transaction.amount)
                    return True, details

        return False, details

    async def _create_alert(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction: Transaction,
        rule: MonitoringRule,
        details: Dict[str, Any]
    ) -> TransactionAlert:
        """Create an alert for a triggered rule"""
        # Determine priority based on rule severity and amount
        priority = AlertPriority.MEDIUM
        if rule.severity == "CRITICAL" or transaction.amount >= 50000:
            priority = AlertPriority.CRITICAL
        elif rule.severity == "HIGH" or transaction.amount >= 25000:
            priority = AlertPriority.HIGH
        elif rule.severity == "LOW":
            priority = AlertPriority.LOW

        alert = TransactionAlert(
            id=uuid4(),
            tenant_id=tenant_id,
            alert_ref=f"ALT-{str(uuid4())[:8].upper()}",
            transaction_id=transaction.id,
            customer_id=transaction.customer_id,
            rule_id=rule.id,
            alert_type=rule.rule_type,
            priority=priority,
            status=AlertStatus.NEW,
            title=f"{rule.name} triggered",
            description=f"Transaction {transaction.transaction_ref} triggered rule: {rule.name}",
            triggered_at=datetime.now(timezone.utc),
            transaction_amount=transaction.amount,
            rule_details=details,
        )
        db.add(alert)

        # Update transaction status
        transaction.status = TransactionStatus.FLAGGED
        transaction.risk_flags = transaction.risk_flags or []
        transaction.risk_flags.append(rule.rule_type)

        await db.commit()
        await db.refresh(alert)

        logger.info(
            f"Alert created: {alert.alert_ref} for transaction {transaction.transaction_ref}"
        )

        return alert

    async def process_transaction_batch(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        transaction_ids: List[UUID]
    ) -> Dict[str, Any]:
        """Process a batch of transactions for monitoring"""
        results = {
            "processed": 0,
            "alerts_generated": 0,
            "errors": 0,
            "alerts": []
        }

        for txn_id in transaction_ids:
            try:
                txn_result = await db.execute(
                    select(Transaction).where(Transaction.id == txn_id)
                )
                transaction = txn_result.scalar_one_or_none()

                if transaction:
                    alerts = await self.evaluate_transaction(db, tenant_id, transaction)
                    results["processed"] += 1
                    results["alerts_generated"] += len(alerts)
                    results["alerts"].extend([
                        {"transaction_id": str(txn_id), "alert_id": str(a.id)}
                        for a in alerts
                    ])
            except Exception as e:
                results["errors"] += 1
                logger.error(f"Error processing transaction {txn_id}: {e}")

        return results

    async def get_alert_summary(
        self,
        db: AsyncSession,
        tenant_id: UUID
    ) -> Dict[str, Any]:
        """Get summary of current alerts"""
        # Count by status
        status_query = select(
            TransactionAlert.status,
            func.count(TransactionAlert.id)
        ).where(
            TransactionAlert.tenant_id == tenant_id
        ).group_by(TransactionAlert.status)

        status_result = await db.execute(status_query)

        # Count by priority
        priority_query = select(
            TransactionAlert.priority,
            func.count(TransactionAlert.id)
        ).where(
            and_(
                TransactionAlert.tenant_id == tenant_id,
                TransactionAlert.status.in_([AlertStatus.NEW, AlertStatus.UNDER_REVIEW])
            )
        ).group_by(TransactionAlert.priority)

        priority_result = await db.execute(priority_query)

        return {
            "by_status": {row[0]: row[1] for row in status_result},
            "open_by_priority": {row[0]: row[1] for row in priority_result}
        }


# Global service instance
transaction_monitoring_service = TransactionMonitoringService()
