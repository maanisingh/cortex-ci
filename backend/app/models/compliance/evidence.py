"""
Evidence Management Models
Evidence collection, linking to controls, and review workflows
"""

from datetime import date, datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class EvidenceType(str, Enum):
    """Types of compliance evidence."""

    DOCUMENT = "DOCUMENT"
    SCREENSHOT = "SCREENSHOT"
    LOG_FILE = "LOG_FILE"
    CONFIG_FILE = "CONFIG_FILE"
    REPORT = "REPORT"
    ATTESTATION = "ATTESTATION"
    CERTIFICATE = "CERTIFICATE"
    POLICY = "POLICY"
    PROCEDURE = "PROCEDURE"
    AUDIT_RESULT = "AUDIT_RESULT"
    TRAINING_RECORD = "TRAINING_RECORD"
    TICKET = "TICKET"
    EMAIL = "EMAIL"
    MEETING_NOTES = "MEETING_NOTES"
    SCAN_RESULT = "SCAN_RESULT"
    AUTOMATED = "AUTOMATED"
    OTHER = "OTHER"


class EvidenceStatus(str, Enum):
    """Evidence lifecycle status."""

    DRAFT = "DRAFT"
    PENDING_REVIEW = "PENDING_REVIEW"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"
    SUPERSEDED = "SUPERSEDED"


class Evidence(Base, TimestampMixin, TenantMixin):
    """Evidence artifact for compliance."""

    __tablename__ = "evidence"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    evidence_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Type and category
    evidence_type: Mapped[EvidenceType] = mapped_column(String(50), nullable=False, index=True)
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Status
    status: Mapped[EvidenceStatus] = mapped_column(
        String(50), default=EvidenceStatus.DRAFT, index=True
    )

    # File info
    file_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    file_hash: Mapped[str | None] = mapped_column(String(128), nullable=True)  # SHA-512

    # External reference (if not a file)
    external_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    external_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    external_id: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Content (for text-based evidence)
    content_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Collection
    collected_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    collected_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    collection_method: Mapped[str | None] = mapped_column(
        String(100), nullable=True
    )  # MANUAL, AUTOMATED, API

    # Validity period
    valid_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    valid_to: Mapped[date | None] = mapped_column(Date, nullable=True)
    is_perpetual: Mapped[bool] = mapped_column(Boolean, default=False)

    # Review
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Metadata
    source_system: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    extra_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    control_links = relationship(
        "EvidenceLink", back_populates="evidence", cascade="all, delete-orphan"
    )
    reviews = relationship(
        "EvidenceReview", back_populates="evidence", cascade="all, delete-orphan"
    )


class EvidenceLink(Base, TimestampMixin, TenantMixin):
    """Link between evidence and controls."""

    __tablename__ = "evidence_links"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), index=True
    )
    control_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), index=True
    )

    # Link details
    link_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # PRIMARY, SUPPORTING, PARTIAL
    relevance_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Coverage
    coverage_percentage: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Who linked it
    linked_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    linked_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="control_links")
    control = relationship("Control", back_populates="evidence_links")


class EvidenceReview(Base, TimestampMixin, TenantMixin):
    """Evidence review history."""

    __tablename__ = "evidence_reviews"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    evidence_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("evidence.id", ondelete="CASCADE"), index=True
    )

    # Review details
    review_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INITIAL, PERIODIC, AUDIT
    reviewer_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=False
    )
    reviewed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    # Outcome
    decision: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # APPROVE, REJECT, REQUEST_CHANGES
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    changes_requested: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Quality assessment
    completeness_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    relevance_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    quality_score: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Relationships
    evidence = relationship("Evidence", back_populates="reviews")
