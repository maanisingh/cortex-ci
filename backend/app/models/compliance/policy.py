"""
Policy Management Models
Policy creation, versioning, acknowledgements, and exceptions
"""

from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, INET, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


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
    short_title: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Classification
    category: Mapped[PolicyCategory] = mapped_column(String(50), nullable=False, index=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Status
    status: Mapped[PolicyStatus] = mapped_column(String(50), default=PolicyStatus.DRAFT, index=True)
    current_version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Content
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    purpose: Mapped[str | None] = mapped_column(Text, nullable=True)
    scope: Mapped[str | None] = mapped_column(Text, nullable=True)
    content: Mapped[str] = mapped_column(Text, nullable=False)

    # Document storage
    document_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    document_format: Mapped[str | None] = mapped_column(
        String(20), nullable=True
    )  # PDF, DOCX, HTML

    # Ownership
    owner_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    owner_department: Mapped[str | None] = mapped_column(String(255), nullable=True)
    author_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Approval
    approver_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Effective dates
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_frequency_months: Mapped[int] = mapped_column(Integer, default=12)

    # Applicability
    applies_to_all: Mapped[bool] = mapped_column(Boolean, default=True)
    applies_to_departments: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applies_to_roles: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applies_to_locations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Acknowledgement requirements
    requires_acknowledgement: Mapped[bool] = mapped_column(Boolean, default=True)
    acknowledgement_frequency_months: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Control mapping
    related_controls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    related_frameworks: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Supersession
    supersedes_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("policies.id"), nullable=True
    )
    superseded_by_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("policies.id"), nullable=True
    )

    # Relationships
    versions = relationship("PolicyVersion", back_populates="policy", cascade="all, delete-orphan")
    acknowledgements = relationship(
        "PolicyAcknowledgement", back_populates="policy", cascade="all, delete-orphan"
    )
    exceptions = relationship(
        "PolicyException", back_populates="policy", cascade="all, delete-orphan"
    )


class PolicyVersion(Base, TimestampMixin, TenantMixin):
    """Policy version history."""

    __tablename__ = "policy_versions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True
    )

    # Version info
    version_number: Mapped[str] = mapped_column(String(20), nullable=False)
    version_type: Mapped[str] = mapped_column(String(20), nullable=False)  # MAJOR, MINOR, PATCH

    # Content
    content: Mapped[str] = mapped_column(Text, nullable=False)
    change_summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    change_details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Document
    document_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Authorship
    created_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Effective dates
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    is_current: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    policy = relationship("Policy", back_populates="versions")


class PolicyAcknowledgement(Base, TimestampMixin, TenantMixin):
    """Policy acknowledgement by users."""

    __tablename__ = "policy_acknowledgements"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True
    )
    user_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), index=True
    )

    # Version acknowledged
    policy_version: Mapped[str] = mapped_column(String(20), nullable=False)

    # Acknowledgement details
    acknowledged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ip_address: Mapped[str | None] = mapped_column(INET, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # E-signature (if required)
    signature: Mapped[str | None] = mapped_column(Text, nullable=True)
    signature_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # CLICK, DRAW, DOCUSEAL

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=True)
    verification_method: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Expiration (for periodic reacknowledgement)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    policy = relationship("Policy", back_populates="acknowledgements")


class PolicyException(Base, TimestampMixin, TenantMixin):
    """Policy exception/waiver requests."""

    __tablename__ = "policy_exceptions"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    policy_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("policies.id", ondelete="CASCADE"), index=True
    )

    # Request details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    justification: Mapped[str] = mapped_column(Text, nullable=False)
    scope: Mapped[str] = mapped_column(Text, nullable=False)

    # Risk assessment
    risk_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    compensating_controls: Mapped[str | None] = mapped_column(Text, nullable=True)
    residual_risk: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Requestor
    requested_by: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    requested_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    department: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Approval
    status: Mapped[ExceptionStatus] = mapped_column(
        String(50), default=ExceptionStatus.PENDING, index=True
    )
    reviewed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    approved_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Validity
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_permanent: Mapped[bool] = mapped_column(Boolean, default=False)

    # Review
    review_required: Mapped[bool] = mapped_column(Boolean, default=True)
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Relationships
    policy = relationship("Policy", back_populates="exceptions")
