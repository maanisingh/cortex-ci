"""
Training & Awareness Models
Compliance training, courses, assignments, and phishing simulations
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


class CourseType(str, Enum):
    """Type of training course."""
    SECURITY_AWARENESS = "SECURITY_AWARENESS"
    PHISHING_AWARENESS = "PHISHING_AWARENESS"
    DATA_PRIVACY = "DATA_PRIVACY"
    AML_COMPLIANCE = "AML_COMPLIANCE"
    SANCTIONS_COMPLIANCE = "SANCTIONS_COMPLIANCE"
    CODE_OF_CONDUCT = "CODE_OF_CONDUCT"
    ANTI_CORRUPTION = "ANTI_CORRUPTION"
    INSIDER_TRADING = "INSIDER_TRADING"
    HIPAA = "HIPAA"
    PCI_DSS = "PCI_DSS"
    GDPR = "GDPR"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    ROLE_SPECIFIC = "ROLE_SPECIFIC"
    ONBOARDING = "ONBOARDING"
    CUSTOM = "CUSTOM"


class CourseStatus(str, Enum):
    """Course lifecycle status."""
    DRAFT = "DRAFT"
    UNDER_REVIEW = "UNDER_REVIEW"
    PUBLISHED = "PUBLISHED"
    ARCHIVED = "ARCHIVED"


class AssignmentStatus(str, Enum):
    """Training assignment status."""
    ASSIGNED = "ASSIGNED"
    IN_PROGRESS = "IN_PROGRESS"
    COMPLETED = "COMPLETED"
    OVERDUE = "OVERDUE"
    EXEMPT = "EXEMPT"


class Course(Base, TimestampMixin, TenantMixin):
    """Training course."""
    __tablename__ = "courses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    course_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Type and status
    course_type: Mapped[CourseType] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[CourseStatus] = mapped_column(String(50), default=CourseStatus.DRAFT, index=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Content
    content_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)  # LMS URL or internal
    content_type: Mapped[str] = mapped_column(String(50), default="SCORM")  # SCORM, VIDEO, PDF, INTERACTIVE
    duration_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Assessment
    has_quiz: Mapped[bool] = mapped_column(Boolean, default=True)
    passing_score: Mapped[int] = mapped_column(Integer, default=80)
    max_attempts: Mapped[int] = mapped_column(Integer, default=3)
    quiz_questions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Applicability
    required_for_all: Mapped[bool] = mapped_column(Boolean, default=False)
    required_for_roles: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    required_for_departments: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    required_for_new_hires: Mapped[bool] = mapped_column(Boolean, default=False)

    # Frequency
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)
    recurrence_months: Mapped[int] = mapped_column(Integer, default=12)

    # Regulatory mapping
    regulatory_requirement: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    control_ids: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Ownership
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Effectiveness
    average_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    completion_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    total_completions: Mapped[int] = mapped_column(Integer, default=0)

    # Moodle/LMS integration
    external_course_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    lms_platform: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Tags
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Relationships
    assignments = relationship("TrainingAssignment", back_populates="course", cascade="all, delete-orphan")


class TrainingAssignment(Base, TimestampMixin, TenantMixin):
    """Training assignment to user."""
    __tablename__ = "training_assignments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    course_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("courses.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Assignment details
    status: Mapped[AssignmentStatus] = mapped_column(String(50), default=AssignmentStatus.ASSIGNED, index=True)

    # Timeline
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[date] = mapped_column(Date, nullable=False)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Progress
    progress_percentage: Mapped[int] = mapped_column(Integer, default=0)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, default=0)

    # Quiz attempts
    attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_attempt_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    best_score: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    passed: Mapped[bool] = mapped_column(Boolean, default=False)

    # Reminders
    reminders_sent: Mapped[int] = mapped_column(Integer, default=0)
    last_reminder_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Exemption
    is_exempt: Mapped[bool] = mapped_column(Boolean, default=False)
    exemption_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    exempted_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    course = relationship("Course", back_populates="assignments")
    completions = relationship("TrainingCompletion", back_populates="assignment", cascade="all, delete-orphan")


class TrainingCompletion(Base, TimestampMixin, TenantMixin):
    """Training completion record."""
    __tablename__ = "training_completions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    assignment_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("training_assignments.id", ondelete="CASCADE"), index=True)

    # Completion details
    completed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)
    passed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    time_spent_minutes: Mapped[int] = mapped_column(Integer, nullable=False)

    # Quiz details
    quiz_answers: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Certificate
    certificate_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    certificate_url: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    certificate_expires: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Validity (for recurring training)
    valid_from: Mapped[date] = mapped_column(Date, nullable=False)
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    assignment = relationship("TrainingAssignment", back_populates="completions")


class PhishingCampaign(Base, TimestampMixin, TenantMixin):
    """Phishing simulation campaign (Gophish integration)."""
    __tablename__ = "phishing_campaigns"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Campaign info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Type
    campaign_type: Mapped[str] = mapped_column(String(50), nullable=False)  # EMAIL, SMS, VOICE

    # Template
    template_name: Mapped[str] = mapped_column(String(255), nullable=False)
    template_category: Mapped[str] = mapped_column(String(100), nullable=False)  # CREDENTIAL_HARVEST, LINK_CLICK, ATTACHMENT
    difficulty_level: Mapped[str] = mapped_column(String(20), default="MEDIUM")

    # Timeline
    scheduled_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="DRAFT")  # DRAFT, SCHEDULED, IN_PROGRESS, COMPLETED

    # Target
    target_all: Mapped[bool] = mapped_column(Boolean, default=False)
    target_departments: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    target_roles: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    target_users: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Statistics
    total_targets: Mapped[int] = mapped_column(Integer, default=0)
    emails_sent: Mapped[int] = mapped_column(Integer, default=0)
    emails_opened: Mapped[int] = mapped_column(Integer, default=0)
    links_clicked: Mapped[int] = mapped_column(Integer, default=0)
    credentials_submitted: Mapped[int] = mapped_column(Integer, default=0)
    attachments_opened: Mapped[int] = mapped_column(Integer, default=0)
    reported: Mapped[int] = mapped_column(Integer, default=0)

    # Rates
    open_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    click_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    submission_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    report_rate: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Gophish integration
    gophish_campaign_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Ownership
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Relationships
    results = relationship("PhishingResult", back_populates="campaign", cascade="all, delete-orphan")


class PhishingResult(Base, TimestampMixin, TenantMixin):
    """Individual phishing simulation result."""
    __tablename__ = "phishing_results"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    campaign_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("phishing_campaigns.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="SENT")  # SENT, OPENED, CLICKED, SUBMITTED, REPORTED

    # Timeline
    sent_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    opened_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    clicked_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reported_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Details
    ip_address: Mapped[Optional[str]] = mapped_column(String(45), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Did they report?
    did_report: Mapped[bool] = mapped_column(Boolean, default=False)
    report_time_seconds: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Risk score
    risk_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Follow-up training
    training_assigned: Mapped[bool] = mapped_column(Boolean, default=False)
    training_assignment_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), nullable=True)

    # Relationships
    campaign = relationship("PhishingCampaign", back_populates="results")
