"""
Customer/KYC Models
AML/KYC customer onboarding, due diligence, and ongoing monitoring
"""
from uuid import UUID, uuid4
from typing import Optional, List
from enum import Enum
from datetime import date, datetime
from sqlalchemy import String, Text, Integer, Float, ForeignKey, Date, DateTime, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID as PGUUID, JSONB, ARRAY, INET

from app.core.database import Base
from app.models.base import TimestampMixin, TenantMixin


class CustomerType(str, Enum):
    """Type of customer entity."""
    INDIVIDUAL = "INDIVIDUAL"
    CORPORATION = "CORPORATION"
    PARTNERSHIP = "PARTNERSHIP"
    LLC = "LLC"
    TRUST = "TRUST"
    FOUNDATION = "FOUNDATION"
    GOVERNMENT = "GOVERNMENT"
    NON_PROFIT = "NON_PROFIT"
    FINANCIAL_INSTITUTION = "FINANCIAL_INSTITUTION"
    CORRESPONDENT_BANK = "CORRESPONDENT_BANK"
    MONEY_SERVICE_BUSINESS = "MONEY_SERVICE_BUSINESS"


class CustomerStatus(str, Enum):
    """Customer lifecycle status."""
    PROSPECT = "PROSPECT"
    PENDING_KYC = "PENDING_KYC"
    KYC_IN_PROGRESS = "KYC_IN_PROGRESS"
    PENDING_APPROVAL = "PENDING_APPROVAL"
    ACTIVE = "ACTIVE"
    UNDER_REVIEW = "UNDER_REVIEW"
    RESTRICTED = "RESTRICTED"
    SUSPENDED = "SUSPENDED"
    OFFBOARDED = "OFFBOARDED"
    REJECTED = "REJECTED"


class CustomerRiskRating(str, Enum):
    """Customer risk classification."""
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    VERY_HIGH = "VERY_HIGH"
    PROHIBITED = "PROHIBITED"


class DocumentType(str, Enum):
    """KYC document types."""
    PASSPORT = "PASSPORT"
    NATIONAL_ID = "NATIONAL_ID"
    DRIVERS_LICENSE = "DRIVERS_LICENSE"
    RESIDENCE_PERMIT = "RESIDENCE_PERMIT"
    UTILITY_BILL = "UTILITY_BILL"
    BANK_STATEMENT = "BANK_STATEMENT"
    CERTIFICATE_OF_INCORPORATION = "CERTIFICATE_OF_INCORPORATION"
    ARTICLES_OF_ASSOCIATION = "ARTICLES_OF_ASSOCIATION"
    SHAREHOLDER_REGISTER = "SHAREHOLDER_REGISTER"
    BOARD_RESOLUTION = "BOARD_RESOLUTION"
    FINANCIAL_STATEMENTS = "FINANCIAL_STATEMENTS"
    TAX_RETURN = "TAX_RETURN"
    BENEFICIAL_OWNERSHIP = "BENEFICIAL_OWNERSHIP"
    SOURCE_OF_FUNDS = "SOURCE_OF_FUNDS"
    SOURCE_OF_WEALTH = "SOURCE_OF_WEALTH"
    SANCTIONS_CERTIFICATE = "SANCTIONS_CERTIFICATE"
    OTHER = "OTHER"


class ReviewType(str, Enum):
    """Types of customer reviews."""
    INITIAL_KYC = "INITIAL_KYC"
    PERIODIC_REVIEW = "PERIODIC_REVIEW"
    TRIGGER_REVIEW = "TRIGGER_REVIEW"
    ENHANCED_DUE_DILIGENCE = "ENHANCED_DUE_DILIGENCE"
    REMEDIATION = "REMEDIATION"
    EXIT_REVIEW = "EXIT_REVIEW"


class Customer(Base, TimestampMixin, TenantMixin):
    """Customer entity for AML/KYC."""
    __tablename__ = "customers"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Customer identification
    customer_type: Mapped[CustomerType] = mapped_column(String(50), nullable=False, index=True)
    external_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True, unique=True)

    # Status
    status: Mapped[CustomerStatus] = mapped_column(String(50), default=CustomerStatus.PROSPECT, index=True)
    risk_rating: Mapped[CustomerRiskRating] = mapped_column(String(50), default=CustomerRiskRating.MEDIUM, index=True)
    risk_score: Mapped[float] = mapped_column(Float, default=50.0)

    # Individual fields
    first_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    middle_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    last_name: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date_of_birth: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    nationality: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    country_of_residence: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)

    # Organization fields
    legal_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True, index=True)
    trading_name: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    registration_number: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    tax_id: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    incorporation_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    incorporation_country: Mapped[Optional[str]] = mapped_column(String(3), nullable=True, index=True)
    industry_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    industry_description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Contact info
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    address_line1: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    address_line2: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    city: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    state: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    postal_code: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    country: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)

    # Risk factors
    is_pep: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    pep_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    pep_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_sanctioned: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    sanction_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    has_adverse_media: Mapped[bool] = mapped_column(Boolean, default=False)
    adverse_media_details: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    high_risk_country: Mapped[bool] = mapped_column(Boolean, default=False)
    high_risk_industry: Mapped[bool] = mapped_column(Boolean, default=False)

    # Source of funds/wealth
    source_of_funds: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_of_wealth: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_activity: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    expected_volume: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Beneficial ownership (for organizations)
    beneficial_owners: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Review schedule
    last_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    next_review_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    review_frequency_months: Mapped[int] = mapped_column(Integer, default=12)

    # Onboarding
    onboarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    onboarded_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    offboarded_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    offboarded_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Additional data
    aliases: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    tags: Mapped[List[str]] = mapped_column(ARRAY(String), default=list)
    custom_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationships
    documents = relationship("CustomerDocument", back_populates="customer", cascade="all, delete-orphan")
    reviews = relationship("CustomerReview", back_populates="customer", cascade="all, delete-orphan")
    screening_results = relationship("ScreeningResult", back_populates="customer", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="customer", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="customer", cascade="all, delete-orphan")

    @property
    def full_name(self) -> str:
        if self.customer_type == CustomerType.INDIVIDUAL:
            parts = [self.first_name, self.middle_name, self.last_name]
            return " ".join(p for p in parts if p)
        return self.legal_name or self.trading_name or ""


class CustomerDocument(Base, TimestampMixin, TenantMixin):
    """KYC documents attached to customers."""
    __tablename__ = "customer_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True)

    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False)
    file_name: Mapped[str] = mapped_column(String(500), nullable=False)
    file_path: Mapped[str] = mapped_column(String(1000), nullable=False)
    file_size: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Document details
    document_number: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issuing_authority: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    issuing_country: Mapped[Optional[str]] = mapped_column(String(3), nullable=True)
    issue_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Verification
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    verified_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    verified_by: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    verification_method: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    verification_notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # OCR/extracted data
    extracted_data: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Status
    is_expired: Mapped[bool] = mapped_column(Boolean, default=False)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=False)

    # Relationships
    customer = relationship("Customer", back_populates="documents")


class CustomerReview(Base, TimestampMixin, TenantMixin):
    """Customer KYC reviews and due diligence."""
    __tablename__ = "customer_reviews"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    customer_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("customers.id", ondelete="CASCADE"), index=True)

    review_type: Mapped[ReviewType] = mapped_column(String(50), nullable=False)
    status: Mapped[str] = mapped_column(String(50), default="IN_PROGRESS")

    # Review dates
    initiated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    due_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Reviewer
    reviewer_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    approver_id: Mapped[Optional[UUID]] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    # Before/after risk
    previous_risk_rating: Mapped[Optional[CustomerRiskRating]] = mapped_column(String(50), nullable=True)
    new_risk_rating: Mapped[Optional[CustomerRiskRating]] = mapped_column(String(50), nullable=True)
    risk_score_change: Mapped[Optional[float]] = mapped_column(Float, nullable=True)

    # Review findings
    findings: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    recommendations: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    decision: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)  # APPROVE, REJECT, ESCALATE
    decision_rationale: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Checklist
    checklist_completed: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    # Trigger (for trigger reviews)
    trigger_reason: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_source: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="reviews")
