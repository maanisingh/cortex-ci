"""
Transaction Monitoring Models
Real-time and batch transaction monitoring for AML
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class TransactionType(str, Enum):
    """Type of financial transaction."""

    WIRE_TRANSFER = "WIRE_TRANSFER"
    ACH = "ACH"
    CHECK = "CHECK"
    CASH_DEPOSIT = "CASH_DEPOSIT"
    CASH_WITHDRAWAL = "CASH_WITHDRAWAL"
    CARD_PAYMENT = "CARD_PAYMENT"
    CARD_ATM = "CARD_ATM"
    INTERNAL_TRANSFER = "INTERNAL_TRANSFER"
    LOAN_DISBURSEMENT = "LOAN_DISBURSEMENT"
    LOAN_PAYMENT = "LOAN_PAYMENT"
    CRYPTO_TRANSFER = "CRYPTO_TRANSFER"
    TRADE = "TRADE"
    FX = "FX"
    OTHER = "OTHER"


class TransactionStatus(str, Enum):
    """Transaction processing status."""

    PENDING = "PENDING"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REVERSED = "REVERSED"
    HELD = "HELD"
    BLOCKED = "BLOCKED"


class AlertSeverity(str, Enum):
    """Transaction alert severity."""

    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class AlertStatus(str, Enum):
    """Alert workflow status."""

    NEW = "NEW"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    CLOSED_LEGITIMATE = "CLOSED_LEGITIMATE"
    CLOSED_SUSPICIOUS = "CLOSED_SUSPICIOUS"
    SAR_FILED = "SAR_FILED"


class RuleType(str, Enum):
    """Type of monitoring rule."""

    THRESHOLD = "THRESHOLD"
    VELOCITY = "VELOCITY"
    PATTERN = "PATTERN"
    GEOGRAPHIC = "GEOGRAPHIC"
    BEHAVIORAL = "BEHAVIORAL"
    NETWORK = "NETWORK"
    ML_MODEL = "ML_MODEL"
    CUSTOM = "CUSTOM"


class Transaction(Base, TimestampMixin, TenantMixin):
    """Financial transaction record."""

    __tablename__ = "transactions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Customer link
    customer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Transaction identification
    transaction_ref: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    external_ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Type and status
    transaction_type: Mapped[TransactionType] = mapped_column(
        String(50), nullable=False, index=True
    )
    status: Mapped[TransactionStatus] = mapped_column(
        String(50), default=TransactionStatus.PENDING, index=True
    )

    # Amount
    amount: Mapped[Decimal] = mapped_column(Numeric(20, 4), nullable=False)
    currency: Mapped[str] = mapped_column(String(3), nullable=False, index=True)
    amount_usd: Mapped[Decimal | None] = mapped_column(Numeric(20, 4), nullable=True)
    fx_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Direction
    direction: Mapped[str] = mapped_column(
        String(10), nullable=False
    )  # INBOUND, OUTBOUND, INTERNAL

    # Originator (sender)
    originator_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    originator_account: Mapped[str | None] = mapped_column(String(100), nullable=True)
    originator_bank: Mapped[str | None] = mapped_column(String(255), nullable=True)
    originator_bank_country: Mapped[str | None] = mapped_column(
        String(3), nullable=True, index=True
    )
    originator_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Beneficiary (receiver)
    beneficiary_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    beneficiary_account: Mapped[str | None] = mapped_column(String(100), nullable=True)
    beneficiary_bank: Mapped[str | None] = mapped_column(String(255), nullable=True)
    beneficiary_bank_country: Mapped[str | None] = mapped_column(
        String(3), nullable=True, index=True
    )
    beneficiary_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Correspondent bank
    correspondent_bank: Mapped[str | None] = mapped_column(String(255), nullable=True)
    correspondent_country: Mapped[str | None] = mapped_column(String(3), nullable=True)

    # Purpose/description
    purpose: Mapped[str | None] = mapped_column(String(500), nullable=True)
    narrative: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timestamps
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    value_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Channel
    channel: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # ONLINE, BRANCH, ATM, API
    ip_address: Mapped[str | None] = mapped_column(String(45), nullable=True)
    device_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    geo_location: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Risk scoring
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)
    risk_factors: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Screening
    is_screened: Mapped[bool] = mapped_column(Boolean, default=False)
    screening_result: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Alert status
    has_alert: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    alert_count: Mapped[int] = mapped_column(Integer, default=0)

    # Additional data
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="transactions")
    alerts = relationship(
        "TransactionAlert", back_populates="transaction", cascade="all, delete-orphan"
    )


class TransactionAlert(Base, TimestampMixin, TenantMixin):
    """Alert generated from transaction monitoring."""

    __tablename__ = "transaction_alerts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    transaction_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("transactions.id", ondelete="CASCADE"), index=True
    )

    # Rule that triggered
    rule_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("monitoring_rules.id"), nullable=True
    )
    rule_name: Mapped[str] = mapped_column(String(255), nullable=False)
    rule_type: Mapped[RuleType] = mapped_column(String(50), nullable=False)

    # Alert details
    severity: Mapped[AlertSeverity] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[AlertStatus] = mapped_column(String(50), default=AlertStatus.NEW, index=True)

    # Description
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    triggered_values: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Risk scoring
    alert_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Timestamps
    triggered_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    first_viewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Assignment
    assigned_to: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_team: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Investigation
    investigation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disposition_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Escalation
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # SAR link
    sar_filed: Mapped[bool] = mapped_column(Boolean, default=False)
    sar_id: Mapped[UUID | None] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Case link
    case_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cases.id"), nullable=True
    )

    # Relationships
    transaction = relationship("Transaction", back_populates="alerts")
    rule = relationship("MonitoringRule")


class MonitoringRule(Base, TimestampMixin, TenantMixin):
    """Transaction monitoring rules."""

    __tablename__ = "monitoring_rules"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Rule identification
    rule_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Type and category
    rule_type: Mapped[RuleType] = mapped_column(String(50), nullable=False)
    category: Mapped[str] = mapped_column(
        String(100), nullable=False
    )  # AML, FRAUD, SANCTIONS, etc.

    # Severity
    default_severity: Mapped[AlertSeverity] = mapped_column(String(50), nullable=False)

    # Rule logic
    conditions: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Example conditions:
    # {"type": "threshold", "field": "amount_usd", "operator": ">", "value": 10000}
    # {"type": "velocity", "count": 5, "period": "1d", "field": "amount"}
    # {"type": "geographic", "countries": ["IR", "KP", "SY"]}

    # Thresholds (for threshold rules)
    threshold_value: Mapped[float | None] = mapped_column(Float, nullable=True)
    threshold_currency: Mapped[str | None] = mapped_column(String(3), nullable=True)

    # Velocity (for velocity rules)
    velocity_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    velocity_period: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # 1h, 1d, 7d, 30d
    velocity_amount: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Applicability
    applies_to_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applies_to_customers: Mapped[list[str]] = mapped_column(
        ARRAY(String), default=list
    )  # risk ratings

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_production: Mapped[bool] = mapped_column(Boolean, default=False)

    # Tuning
    tuning_parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    last_tuned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Statistics
    total_alerts: Mapped[int] = mapped_column(Integer, default=0)
    true_positives: Mapped[int] = mapped_column(Integer, default=0)
    false_positives: Mapped[int] = mapped_column(Integer, default=0)
    precision_rate: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Regulatory mapping
    regulatory_reference: Mapped[str | None] = mapped_column(String(255), nullable=True)
