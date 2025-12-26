"""
Vendor Risk Management Models
Third-party risk assessment, questionnaires, and monitoring
"""
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from datetime import date, datetime
from decimal import Decimal
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Date, DateTime, Boolean, Numeric
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class VendorTier(str, Enum):
    """Vendor criticality tier."""
    TIER_1 = "TIER_1"  # Critical - core business
    TIER_2 = "TIER_2"  # Important - significant impact
    TIER_3 = "TIER_3"  # Standard - limited impact
    TIER_4 = "TIER_4"  # Low - minimal impact


class VendorStatus(str, Enum):
    """Vendor lifecycle status."""
    PROSPECTIVE = "PROSPECTIVE"
    DUE_DILIGENCE = "DUE_DILIGENCE"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    APPROVED = "APPROVED"
    ACTIVE = "ACTIVE"
    ON_WATCH = "ON_WATCH"
    SUSPENDED = "SUSPENDED"
    TERMINATED = "TERMINATED"
    ARCHIVED = "ARCHIVED"


class ContractStatus(str, Enum):
    """Contract status."""
    DRAFT = "DRAFT"
    NEGOTIATION = "NEGOTIATION"
    PENDING_SIGNATURE = "PENDING_SIGNATURE"
    ACTIVE = "ACTIVE"
    EXPIRING_SOON = "EXPIRING_SOON"
    EXPIRED = "EXPIRED"
    TERMINATED = "TERMINATED"
    RENEWED = "RENEWED"


class Vendor(Base, TimestampMixin, TenantMixin):
    """Third-party vendor."""
    __tablename__ = "vendors"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Identification
    vendor_ref: Mapped[str] = mapped_column(String(50), nullable=False, unique=True)
    legal_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    trading_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Classification
    tier: Mapped[VendorTier] = mapped_column(String(20), nullable=False, index=True)
    status: Mapped[VendorStatus] = mapped_column(String(50), default=VendorStatus.PROSPECTIVE, index=True)

    # Category
    category: Mapped[str] = mapped_column(String(100), nullable=False)  # Technology, Professional Services, etc.
    subcategory: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    services_provided: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Contact info
    primary_contact_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_contact_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    primary_contact_phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    website: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)

    # Address
    address_line1: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)

    # Registration
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    duns_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Risk assessment
    inherent_risk: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    residual_risk: Mapped[str] = mapped_column(String(20), default="MEDIUM")
    risk_score: Mapped[float] = mapped_column(Float, default=50.0)
    risk_factors: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Data access
    has_data_access: Mapped[bool] = mapped_column(Boolean, default=False)
    data_types: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)  # PII, PHI, Financial, etc.
    data_classification: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)

    # System access
    has_system_access: Mapped[bool] = mapped_column(Boolean, default=False)
    systems_accessed: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Certifications
    certifications: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)  # SOC2, ISO27001, etc.

    # Financial
    annual_spend: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    payment_terms: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Review
    last_assessment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_assessment_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    assessment_frequency_months: Mapped[int] = mapped_column(Integer, default=12)

    # Internal ownership
    business_owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    risk_owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Onboarding/offboarding
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    terminated_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    termination_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Relationships
    assessments = relationship("VendorAssessment", back_populates="vendor", cascade="all, delete-orphan")
    contracts = relationship("VendorContract", back_populates="vendor", cascade="all, delete-orphan")
    questionnaire_responses = relationship("QuestionnaireResponse", back_populates="vendor", cascade="all, delete-orphan")


class VendorAssessment(Base, TimestampMixin, TenantMixin):
    """Vendor risk assessment."""
    __tablename__ = "vendor_assessments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)

    # Assessment info
    assessment_type: Mapped[str] = mapped_column(String(50), nullable=False)  # INITIAL, ANNUAL, TRIGGER
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")

    # Timeline
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Assessor
    assessor_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Scores by domain
    security_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    privacy_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    operational_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    financial_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    compliance_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    overall_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Risk determination
    risk_rating_before: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    risk_rating_after: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    # Findings
    findings_count: Mapped[int] = mapped_column(Integer, default=0)
    critical_findings: Mapped[int] = mapped_column(Integer, default=0)
    findings_summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    findings_detail: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Recommendations
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    required_actions: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Approval
    decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # APPROVE, CONDITIONAL, REJECT
    decision_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    approved_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="assessments")


class VendorQuestionnaire(Base, TimestampMixin, TenantMixin):
    """Questionnaire template for vendor assessments."""
    __tablename__ = "vendor_questionnaires"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Questionnaire info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Type
    questionnaire_type: Mapped[str] = mapped_column(String(50), nullable=False)  # SIG, CAIQ, CUSTOM

    # Questions (structured)
    sections: Mapped[dict] = mapped_column(JSONB, nullable=False)
    # Structure:
    # {
    #   "sections": [
    #     {
    #       "id": "sec1",
    #       "title": "Security Controls",
    #       "questions": [
    #         {"id": "q1", "text": "...", "type": "yes_no", "required": true, "weight": 1.0}
    #       ]
    #     }
    #   ]
    # }

    total_questions: Mapped[int] = mapped_column(Integer, default=0)

    # Applicability
    applicable_tiers: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    applicable_categories: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_default: Mapped[bool] = mapped_column(Boolean, default=False)


class QuestionnaireResponse(Base, TimestampMixin, TenantMixin):
    """Vendor's response to a questionnaire."""
    __tablename__ = "questionnaire_responses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)
    questionnaire_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vendor_questionnaires.id"), index=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="PENDING")  # PENDING, IN_PROGRESS, SUBMITTED, REVIEWED

    # Sent/received
    sent_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    sent_to_email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    submitted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Responses (structured to match questionnaire)
    responses: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    # {"q1": {"answer": "yes", "evidence": "...", "notes": "..."}}

    # Completion
    questions_answered: Mapped[int] = mapped_column(Integer, default=0)
    completion_percentage: Mapped[float] = mapped_column(Float, default=0.0)

    # Scoring
    auto_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    manual_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    final_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Review
    reviewed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    review_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="questionnaire_responses")
    questionnaire = relationship("VendorQuestionnaire")


class VendorContract(Base, TimestampMixin, TenantMixin):
    """Vendor contract."""
    __tablename__ = "vendor_contracts"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    vendor_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("vendors.id", ondelete="CASCADE"), index=True)

    # Contract info
    contract_ref: Mapped[str] = mapped_column(String(100), nullable=False)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    contract_type: Mapped[str] = mapped_column(String(100), nullable=False)  # MSA, SOW, SLA, NDA, DPA, BAA

    # Status
    status: Mapped[ContractStatus] = mapped_column(String(50), default=ContractStatus.DRAFT, index=True)

    # Dates
    effective_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiration_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    auto_renew: Mapped[bool] = mapped_column(Boolean, default=False)
    renewal_notice_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Value
    contract_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(20, 2), nullable=True)
    currency: Mapped[str] = mapped_column(String(3), default="USD")

    # Terms
    payment_terms: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    termination_notice_days: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    termination_clause: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Documents
    document_path: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    amendments: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Key clauses
    sla_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    data_protection_terms: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    liability_cap: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    insurance_requirements: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Signatures
    signed_by_vendor: Mapped[bool] = mapped_column(Boolean, default=False)
    signed_by_us: Mapped[bool] = mapped_column(Boolean, default=False)
    signed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Internal owner
    contract_owner_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Notes
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    vendor = relationship("Vendor", back_populates="contracts")
