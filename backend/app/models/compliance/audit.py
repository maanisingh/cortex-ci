"""
Audit Management Models
Internal and external audits, findings, and remediation
"""

from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class AuditType(str, Enum):
    """Type of audit."""

    INTERNAL = "INTERNAL"
    EXTERNAL = "EXTERNAL"
    REGULATORY = "REGULATORY"
    CERTIFICATION = "CERTIFICATION"
    SOC2_TYPE1 = "SOC2_TYPE1"
    SOC2_TYPE2 = "SOC2_TYPE2"
    ISO27001 = "ISO27001"
    PCI_DSS = "PCI_DSS"
    HIPAA = "HIPAA"
    PENETRATION_TEST = "PENETRATION_TEST"
    VULNERABILITY_ASSESSMENT = "VULNERABILITY_ASSESSMENT"
    VENDOR = "VENDOR"
    CUSTOM = "CUSTOM"


class AuditStatus(str, Enum):
    """Audit lifecycle status."""

    PLANNED = "PLANNED"
    IN_PROGRESS = "IN_PROGRESS"
    FIELDWORK_COMPLETE = "FIELDWORK_COMPLETE"
    DRAFT_REPORT = "DRAFT_REPORT"
    FINAL_REPORT = "FINAL_REPORT"
    REMEDIATION = "REMEDIATION"
    CLOSED = "CLOSED"
    CANCELLED = "CANCELLED"


class FindingSeverity(str, Enum):
    """Audit finding severity."""

    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFORMATIONAL = "INFORMATIONAL"


class FindingStatus(str, Enum):
    """Finding remediation status."""

    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    PENDING_VERIFICATION = "PENDING_VERIFICATION"
    REMEDIATED = "REMEDIATED"
    RISK_ACCEPTED = "RISK_ACCEPTED"
    DEFERRED = "DEFERRED"
    CLOSED = "CLOSED"


class RemediationStatus(str, Enum):
    """Remediation plan status."""

    DRAFT = "DRAFT"
    APPROVED = "APPROVED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    CANCELLED = "CANCELLED"


class Audit(Base, TimestampMixin, TenantMixin):
    """Audit engagement."""

    __tablename__ = "audits"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    audit_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Type and status
    audit_type: Mapped[AuditType] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[AuditStatus] = mapped_column(String(50), default=AuditStatus.PLANNED, index=True)

    # Scope
    scope_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    in_scope_systems: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    in_scope_processes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    in_scope_frameworks: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    exclusions: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Timeline
    planned_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    planned_end: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_start: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_end: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Auditor info
    lead_auditor_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    auditor_organization: Mapped[str | None] = mapped_column(String(255), nullable=True)
    auditor_team: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Internal contacts
    audit_sponsor_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    internal_lead_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Results summary
    total_findings: Mapped[int] = mapped_column(Integer, default=0)
    critical_findings: Mapped[int] = mapped_column(Integer, default=0)
    high_findings: Mapped[int] = mapped_column(Integer, default=0)
    medium_findings: Mapped[int] = mapped_column(Integer, default=0)
    low_findings: Mapped[int] = mapped_column(Integer, default=0)

    # Overall assessment
    overall_rating: Mapped[str | None] = mapped_column(String(50), nullable=True)
    opinion: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Reports
    draft_report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    final_report_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    report_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Cost
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Metadata
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    findings = relationship("AuditFinding", back_populates="audit", cascade="all, delete-orphan")


class AuditFinding(Base, TimestampMixin, TenantMixin):
    """Audit finding/observation."""

    __tablename__ = "audit_findings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    audit_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("audits.id", ondelete="CASCADE"), index=True
    )

    # Identification
    finding_ref: Mapped[str] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)

    # Severity and status
    severity: Mapped[FindingSeverity] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[FindingStatus] = mapped_column(
        String(50), default=FindingStatus.OPEN, index=True
    )

    # Finding details
    description: Mapped[str] = mapped_column(Text, nullable=False)
    root_cause: Mapped[str | None] = mapped_column(Text, nullable=True)
    impact: Mapped[str | None] = mapped_column(Text, nullable=True)
    recommendation: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Evidence
    evidence_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Control mapping
    affected_controls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    control_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("controls.id"), nullable=True
    )

    # Risk
    inherent_risk: Mapped[str | None] = mapped_column(String(50), nullable=True)
    residual_risk: Mapped[str | None] = mapped_column(String(50), nullable=True)
    risk_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Ownership
    owner_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    owner_department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Remediation timeline
    target_remediation_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    actual_remediation_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Management response
    management_response: Mapped[str | None] = mapped_column(Text, nullable=True)
    response_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    response_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Verification
    verification_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    verified_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # If risk accepted
    risk_acceptance_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    risk_accepted_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    risk_accepted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Repeat finding
    is_repeat: Mapped[bool] = mapped_column(Boolean, default=False)
    previous_finding_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("audit_findings.id"), nullable=True
    )

    # Relationships
    audit = relationship("Audit", back_populates="findings")
    remediation_plans = relationship(
        "RemediationPlan", back_populates="finding", cascade="all, delete-orphan"
    )


class RemediationPlan(Base, TimestampMixin, TenantMixin):
    """Remediation plan for audit findings."""

    __tablename__ = "remediation_plans"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    finding_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("audit_findings.id", ondelete="CASCADE"), index=True
    )

    # Plan details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[RemediationStatus] = mapped_column(
        String(50), default=RemediationStatus.DRAFT, index=True
    )

    # Actions
    action_steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    # [{"step": 1, "action": "...", "owner": "...", "due_date": "...", "status": "..."}]

    # Timeline
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Ownership
    owner_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    team_members: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Approval
    approved_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Progress
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    progress_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    last_updated_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Cost
    estimated_cost: Mapped[float | None] = mapped_column(Float, nullable=True)
    actual_cost: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Relationships
    finding = relationship("AuditFinding", back_populates="remediation_plans")
