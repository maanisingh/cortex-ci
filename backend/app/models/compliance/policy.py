"""
Policy Management Models
Policy creation, versioning, acknowledgements, and exceptions
"""
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from datetime import date, datetime
from sqlalchemy import String, Text, Integer, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY, INET

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class PolicyStatus(str, Enum):
    """Policy lifecycle status."""
    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    PUBLISHED = "PUBLISHED"
    UNDER_REVISION = "UNDER_REVISION"
    SUPERSEDED = "SUPERSEDED"
    RETIRED = "RETIRED"


class PolicyCategory(str, Enum):
    """Policy categories."""
    INFORMATION_SECURITY = "INFORMATION_SECURITY"
    DATA_PRIVACY = "DATA_PRIVACY"
    ACCEPTABLE_USE = "ACCEPTABLE_USE"
    ACCESS_CONTROL = "ACCESS_CONTROL"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    BUSINESS_CONTINUITY = "BUSINESS_CONTINUITY"
    DISASTER_RECOVERY = "DISASTER_RECOVERY"
    VENDOR_MANAGEMENT = "VENDOR_MANAGEMENT"
    AML_KYC = "AML_KYC"
    SANCTIONS = "SANCTIONS"
    CODE_OF_CONDUCT = "CODE_OF_CONDUCT"
    WHISTLEBLOWER = "WHISTLEBLOWER"
    ANTI_CORRUPTION = "ANTI_CORRUPTION"
    CONFLICT_OF_INTEREST = "CONFLICT_OF_INTEREST"
    RECORD_RETENTION = "RECORD_RETENTION"
    HR_EMPLOYEE = "HR_EMPLOYEE"
    PHYSICAL_SECURITY = "PHYSICAL_SECURITY"
    CHANGE_MANAGEMENT = "CHANGE_MANAGEMENT"
    RISK_MANAGEMENT = "RISK_MANAGEMENT"
    COMPLIANCE = "COMPLIANCE"
    OTHER = "OTHER"


class ExceptionStatus(str, Enum):
    """Policy exception status."""
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    DENIED = "DENIED"
    EXPIRED = "EXPIRED"
    REVOKED = "REVOKED"


class Policy(Base, TimestampMixin, TenantMixin):
    """Policy document."""
    __tablename__ = "policies"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    policy_number: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    short_title: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Classification
    category: Mapped[PolicyCategory] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Status
    status: Mapped[PolicyStatus] = mapped_column(String(50), default=PolicyStatus.DRAFT, index=True)
    current_version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Content
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    purpose: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    scope: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Document storage
    document_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    document_format: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # PDF, DOCX, HTML

    # Ownership
    owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    owner_department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    author_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Approval
    approver_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Effective dates
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_frequency_months: Mapped[int] = mapped_column(Integer, default=12)

    # Applicability
    applies_to_all: Mapped[bool] = mapped_column(Boolean, default=True)
    applies_to_departments: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    applies_to_roles: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    applies_to_locations: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Acknowledgement requirements
    requires_acknowledgement: Mapped[bool] = mapped_column(Boolean, default=True)
    acknowledgement_frequency_months: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Control mapping
    related_controls: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    related_frameworks: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Supersession
    supersedes_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("policies.id"), nullable=True)
    superseded_by_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("policies.id"), nullable=True)

    # Relationships
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")
    acknowledgements = relationship("PolicyAcknowledgement", back_populates="policy", cascade="all, delete-orphan")
    exceptions = relationship("PolicyException", back_populates="policy", cascade="all, delete-orphan")


class PolicyVersion(Base, TimestampMixin, TenantMixin):
    """Policy version history."""
    __tablename__ = "policy_versions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True)

    # Version info
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    version_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MAJOR, MINOR, PATCH

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    change_details: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Document
    document_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)

    # Authorship
    created_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Effective dates
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Status
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    policy = relationship("Policy", back_populates="versions")


class PolicyAcknowledgement(Base, TimestampMixin, TenantMixin):
    """Policy acknowledgement by users."""
    __tablename__ = "policy_acknowledgements"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True)

    # Version acknowledged
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Acknowledgement details
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[Optional[str]] = mapped_column(INET, nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # E-signature (if required)
    signature: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    signature_type: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # CLICK, DRAW, DOCUSEAL

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_method: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Expiration (for periodic reacknowledgement)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    policy = relationship("Policy", back_populates="acknowledgements")


class PolicyException(Base, TimestampMixin, TenantMixin):
    """Policy exception/waiver requests."""
    __tablename__ = "policy_exceptions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True)

    # Request details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)

    # Risk assessment
    risk_description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    compensating_controls: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    residual_risk: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # Requestor
    requested_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    department: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Approval
    status: Mapped[ExceptionStatus] = mapped_column(String(50), default=ExceptionStatus.PENDING, index=True)
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Validity
    effective_from: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    effective_to: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_permanent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Review
    review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    next_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Relationships
    policy = relationship("Policy", back_populates="exceptions")
