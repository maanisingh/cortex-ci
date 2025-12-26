"""
Incident Management Models
Security incidents, breaches, response, and notifications
"""
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from datetime import date, datetime
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class IncidentSeverity(str, Enum):
    """Incident severity levels."""
    CRITICAL = "CRITICAL"  # P1 - Major breach, immediate response
    HIGH = "HIGH"          # P2 - Significant impact, urgent response
    MEDIUM = "MEDIUM"      # P3 - Moderate impact
    LOW = "LOW"            # P4 - Minor impact


class IncidentStatus(str, Enum):
    """Incident lifecycle status."""
    NEW = "NEW"
    TRIAGED = "TRIAGED"
    INVESTIGATING = "INVESTIGATING"
    CONTAINMENT = "CONTAINMENT"
    ERADICATION = "ERADICATION"
    RECOVERY = "RECOVERY"
    POST_INCIDENT = "POST_INCIDENT"
    CLOSED = "CLOSED"


class IncidentCategory(str, Enum):
    """Incident categories."""
    DATA_BREACH = "DATA_BREACH"
    MALWARE = "MALWARE"
    RANSOMWARE = "RANSOMWARE"
    PHISHING = "PHISHING"
    UNAUTHORIZED_ACCESS = "UNAUTHORIZED_ACCESS"
    INSIDER_THREAT = "INSIDER_THREAT"
    DDOS = "DDOS"
    SYSTEM_COMPROMISE = "SYSTEM_COMPROMISE"
    DATA_LOSS = "DATA_LOSS"
    POLICY_VIOLATION = "POLICY_VIOLATION"
    FRAUD = "FRAUD"
    PHYSICAL_SECURITY = "PHYSICAL_SECURITY"
    VENDOR_INCIDENT = "VENDOR_INCIDENT"
    REGULATORY = "REGULATORY"
    OTHER = "OTHER"


class ResponseAction(str, Enum):
    """Incident response actions."""
    ISOLATE_SYSTEM = "ISOLATE_SYSTEM"
    BLOCK_USER = "BLOCK_USER"
    RESET_CREDENTIALS = "RESET_CREDENTIALS"
    PATCH_SYSTEM = "PATCH_SYSTEM"
    RESTORE_BACKUP = "RESTORE_BACKUP"
    FORENSIC_ANALYSIS = "FORENSIC_ANALYSIS"
    NOTIFY_USERS = "NOTIFY_USERS"
    NOTIFY_REGULATORS = "NOTIFY_REGULATORS"
    LEGAL_REVIEW = "LEGAL_REVIEW"
    EXTERNAL_INVESTIGATION = "EXTERNAL_INVESTIGATION"
    OTHER = "OTHER"


class NotificationStatus(str, Enum):
    """Breach notification status."""
    NOT_REQUIRED = "NOT_REQUIRED"
    PENDING_ASSESSMENT = "PENDING_ASSESSMENT"
    REQUIRED = "REQUIRED"
    DRAFTED = "DRAFTED"
    SENT = "SENT"
    ACKNOWLEDGED = "ACKNOWLEDGED"


class Incident(Base, TimestampMixin, TenantMixin):
    """Security incident."""
    __tablename__ = "incidents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    incident_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Classification
    category: Mapped[IncidentCategory] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    severity: Mapped[IncidentSeverity] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[IncidentStatus] = mapped_column(String(50), default=IncidentStatus.NEW, index=True)

    # Timeline
    detected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reported_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    occurred_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    contained_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    eradicated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    recovered_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    closed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Detection
    detection_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)  # SIEM, User Report, Monitoring, etc.
    detection_source: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    reported_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Assignment
    assigned_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    response_team: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Impact assessment
    affected_systems: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    affected_users_count: Mapped[int] = mapped_column(Integer, default=0)
    affected_records_count: Mapped[int] = mapped_column(Integer, default=0)
    data_types_affected: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)  # PII, PHI, Financial, etc.

    # Business impact
    business_impact: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    financial_impact: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reputation_impact: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Technical details
    attack_vector: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    indicators_of_compromise: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {"ip_addresses": [], "domains": [], "file_hashes": [], "urls": []}

    threat_actor: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    malware_family: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # MITRE ATT&CK mapping
    mitre_tactics: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    mitre_techniques: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Root cause
    root_cause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    root_cause_category: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Resolution
    resolution_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    lessons_learned: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    preventive_measures: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Breach determination
    is_breach: Mapped[bool] = mapped_column(Boolean, default=False)
    breach_determination_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    breach_determined_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    breach_determined_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # External reporting
    reported_to_law_enforcement: Mapped[bool] = mapped_column(Boolean, default=False)
    law_enforcement_case_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reported_to_regulators: Mapped[bool] = mapped_column(Boolean, default=False)
    regulator_reference: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # TheHive integration
    thehive_case_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tags and metadata
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    timeline_entries = relationship("IncidentTimeline", back_populates="incident", cascade="all, delete-orphan")
    response_actions = relationship("IncidentResponse", back_populates="incident", cascade="all, delete-orphan")
    notifications = relationship("BreachNotification", back_populates="incident", cascade="all, delete-orphan")


class IncidentTimeline(Base, TimestampMixin, TenantMixin):
    """Incident timeline entry."""
    __tablename__ = "incident_timeline"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True)

    # Entry details
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    entry_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EVENT, ACTION, COMMUNICATION, STATUS_CHANGE
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Actor
    actor_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    actor_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Attachments
    attachments: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Visibility
    is_internal: Mapped[bool] = mapped_column(Boolean, default=True)

    # Relationships
    incident = relationship("Incident", back_populates="timeline_entries")


class IncidentResponse(Base, TimestampMixin, TenantMixin):
    """Incident response action."""
    __tablename__ = "incident_responses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True)

    # Action details
    action_type: Mapped[ResponseAction] = mapped_column(String(50), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, COMPLETED, FAILED

    # Assignment
    assigned_to: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Timeline
    due_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Outcome
    outcome: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    was_effective: Mapped[Optional[bool]] = mapped_column(Boolean, nullable=True)

    # Playbook reference
    playbook_step: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    incident = relationship("Incident", back_populates="response_actions")


class BreachNotification(Base, TimestampMixin, TenantMixin):
    """Breach notification record."""
    __tablename__ = "breach_notifications"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    incident_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("incidents.id", ondelete="CASCADE"), index=True)

    # Notification type
    notification_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INDIVIDUAL, REGULATOR, MEDIA, LAW_ENFORCEMENT

    # Recipient
    recipient_type: Mapped[str] = mapped_column(String(100), nullable=False)  # DPA, State AG, HHS, Customer, etc.
    recipient_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    recipient_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Regulatory basis
    regulation: Mapped[str] = mapped_column(String(50), nullable=False)  # GDPR, HIPAA, CCPA, State
    notification_deadline: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[NotificationStatus] = mapped_column(String(50), default=NotificationStatus.PENDING_ASSESSMENT)

    # Content
    notification_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Delivery
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    delivery_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # EMAIL, MAIL, PORTAL
    delivery_confirmation: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Response
    acknowledged_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    response_received: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Individual notification tracking
    total_individuals: Mapped[int] = mapped_column(Integer, default=0)
    notifications_sent: Mapped[int] = mapped_column(Integer, default=0)
    notifications_failed: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    incident = relationship("Incident", back_populates="notifications")
