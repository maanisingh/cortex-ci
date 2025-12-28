"""
Case Management Models
Investigation cases, SAR reports, and case workflows
"""

from datetime import date, datetime
from decimal import Decimal
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class CaseType(str, Enum):
    """Type of investigation case."""

    AML_INVESTIGATION = "AML_INVESTIGATION"
    FRAUD_INVESTIGATION = "FRAUD_INVESTIGATION"
    SANCTIONS_MATCH = "SANCTIONS_MATCH"
    PEP_REVIEW = "PEP_REVIEW"
    UNUSUAL_ACTIVITY = "UNUSUAL_ACTIVITY"
    CUSTOMER_COMPLAINT = "CUSTOMER_COMPLAINT"
    REGULATORY_INQUIRY = "REGULATORY_INQUIRY"
    INTERNAL_AUDIT = "INTERNAL_AUDIT"
    WHISTLEBLOWER = "WHISTLEBLOWER"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    DATA_BREACH = "DATA_BREACH"
    VENDOR_ISSUE = "VENDOR_ISSUE"
    OTHER = "OTHER"


class CaseStatus(str, Enum):
    """Case workflow status."""

    NEW = "NEW"
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_INFO = "PENDING_INFO"
    UNDER_REVIEW = "UNDER_REVIEW"
    ESCALATED = "ESCALATED"
    CLOSED_NO_ACTION = "CLOSED_NO_ACTION"
    CLOSED_SAR_FILED = "CLOSED_SAR_FILED"
    CLOSED_RESOLVED = "CLOSED_RESOLVED"


class CasePriority(str, Enum):
    """Case priority levels."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class TaskStatus(str, Enum):
    """Case task status."""

    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    BLOCKED = "BLOCKED"
    CANCELLED = "CANCELLED"


class SARStatus(str, Enum):
    """SAR filing status."""

    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    FILED = "FILED"
    ACKNOWLEDGED = "ACKNOWLEDGED"
    REJECTED = "REJECTED"


class Case(Base, TimestampMixin, TenantMixin):
    """Investigation case."""

    __tablename__ = "cases"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    case_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    case_type: Mapped[CaseType] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[CaseStatus] = mapped_column(String(50), default=CaseStatus.NEW, index=True)
    priority: Mapped[CasePriority] = mapped_column(
        String(20), default=CasePriority.MEDIUM, index=True
    )

    # Source
    source_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # ALERT, SCREENING, MANUAL, EXTERNAL
    source_id: Mapped[str | None] = mapped_column(
        String(255), nullable=True
    )  # Alert ID, screening result ID, etc.

    # Related customer
    customer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # Timeline
    opened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    closed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Assignment
    assigned_to: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    assigned_team: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Opener
    opened_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Investigation summary
    risk_indicators: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    investigation_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    findings: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Financial summary (for AML cases)
    total_amount_involved: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)

    # Related transactions
    related_transactions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Related alerts
    related_alerts: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    alert_count: Mapped[int] = mapped_column(Integer, default=0)

    # Disposition
    disposition: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disposition_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    closed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # SAR decision
    sar_required: Mapped[bool] = mapped_column(Boolean, default=False)
    sar_decision_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    sar_decision_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    sar_decision_rationale: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Escalation
    is_escalated: Mapped[bool] = mapped_column(Boolean, default=False)
    escalated_to: Mapped[str | None] = mapped_column(String(100), nullable=True)
    escalation_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    escalated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # SLA tracking
    sla_due_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    sla_breached: Mapped[bool] = mapped_column(Boolean, default=False)

    # Tags and metadata
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # TheHive integration
    thehive_case_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="cases")
    notes = relationship("CaseNote", back_populates="case", cascade="all, delete-orphan")
    tasks = relationship("CaseTask", back_populates="case", cascade="all, delete-orphan")
    sar_reports = relationship("SARReport", back_populates="case", cascade="all, delete-orphan")


class CaseNote(Base, TimestampMixin, TenantMixin):
    """Case investigation note."""

    __tablename__ = "case_notes"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )

    # Note details
    note_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # INVESTIGATION, COMMUNICATION, DECISION, SYSTEM
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Author
    author_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )

    # Visibility
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True)

    # Attachments
    attachments: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    case = relationship("Case", back_populates="notes")


class CaseTask(Base, TimestampMixin, TenantMixin):
    """Case workflow task."""

    __tablename__ = "case_tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )

    # Task details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # REVIEW, COLLECT_INFO, INTERVIEW, DOCUMENT, DECISION

    # Status
    status: Mapped[TaskStatus] = mapped_column(String(50), default=TaskStatus.PENDING)

    # Assignment
    assigned_to: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Timeline
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Outcome
    outcome: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Order
    sequence: Mapped[int] = mapped_column(Integer, default=0)

    # Mandatory
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    case = relationship("Case", back_populates="tasks")


class SARReport(Base, TimestampMixin, TenantMixin):
    """Suspicious Activity Report."""

    __tablename__ = "sar_reports"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    case_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), index=True
    )

    # SAR identification
    sar_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    status: Mapped[SARStatus] = mapped_column(String(50), default=SARStatus.DRAFT, index=True)

    # SAR type
    sar_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INITIAL, CONTINUING, JOINT
    report_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SAR, CTR, 8300

    # Filing details
    filing_institution: Mapped[str] = mapped_column(String(255), nullable=False)
    filing_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    fincen_bsa_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Subject information
    subject_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INDIVIDUAL, BUSINESS
    subject_name: Mapped[str] = mapped_column(String(500), nullable=False)
    subject_dob: Mapped[date | None] = mapped_column(Date, nullable=True)
    subject_ssn_tin: Mapped[str | None] = mapped_column(String(20), nullable=True)
    subject_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    subject_account_numbers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Activity summary
    activity_start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    activity_end_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    total_amount: Mapped[Decimal | None] = mapped_column(Numeric(20, 2), nullable=True)
    transaction_count: Mapped[int] = mapped_column(Integer, default=0)

    # Suspicious activity types
    activity_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    # Structuring, Terrorist Financing, Money Laundering, etc.

    # Narrative
    narrative: Mapped[str] = mapped_column(Text, nullable=False)

    # Related law enforcement
    law_enforcement_contact: Mapped[bool] = mapped_column(Boolean, default=False)
    le_agency: Mapped[str | None] = mapped_column(String(255), nullable=True)
    le_case_number: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Approval workflow
    prepared_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    prepared_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approved_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Filing
    filed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    filed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    acknowledgement_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    acknowledgement_id: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Document
    document_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    case = relationship("Case", back_populates="sar_reports")
