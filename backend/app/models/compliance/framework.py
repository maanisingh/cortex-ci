"""
Regulatory Framework Models
Supports: NIST 800-53, NIST CSF, ISO 27001, SOC 2, PCI-DSS, HIPAA, GDPR, CIS Controls, MITRE ATT&CK
"""

from datetime import date
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class FrameworkType(str, Enum):
    """Supported regulatory frameworks."""

    # International Standards
    NIST_800_53 = "NIST_800_53"
    NIST_CSF = "NIST_CSF"
    ISO_27001 = "ISO_27001"
    ISO_27002 = "ISO_27002"
    SOC_2 = "SOC_2"
    PCI_DSS = "PCI_DSS"
    HIPAA = "HIPAA"
    GDPR = "GDPR"
    SOX = "SOX"
    GLBA = "GLBA"
    CCPA = "CCPA"
    CIS_CONTROLS = "CIS_CONTROLS"
    MITRE_ATTACK = "MITRE_ATTACK"
    COBIT = "COBIT"
    FEDRAMP = "FEDRAMP"
    CMMC = "CMMC"
    NERC_CIP = "NERC_CIP"
    SWIFT_CSP = "SWIFT_CSP"
    # Russian Regulatory Frameworks
    FZ_152 = "FZ_152"  # Personal Data Protection
    FZ_187 = "FZ_187"  # Critical Information Infrastructure
    FZ_115 = "FZ_115"  # Anti-Money Laundering
    FZ_273 = "FZ_273"  # Anti-Corruption
    CBR_382P = "CBR_382P"  # Central Bank of Russia - Payment Security
    CBR_683P = "CBR_683P"  # Central Bank of Russia - Information Security
    CBR_716P = "CBR_716P"  # Central Bank of Russia - Operational Risk
    GOST_57580 = "GOST_57580"  # Financial Sector Security Standard
    GOST_34_10 = "GOST_34_10"  # Cryptographic Standards
    FSTEC_17 = "FSTEC_17"  # Government Information Systems Protection
    FSTEC_21 = "FSTEC_21"  # Personal Data Protection Measures
    FSTEC_31 = "FSTEC_31"  # Critical Infrastructure Protection
    ROSKOMNADZOR = "ROSKOMNADZOR"  # Data Protection Authority Requirements
    # Custom
    CUSTOM = "CUSTOM"


class ControlCategory(str, Enum):
    """Control categories across frameworks."""

    ACCESS_CONTROL = "ACCESS_CONTROL"
    ASSET_MANAGEMENT = "ASSET_MANAGEMENT"
    AUDIT_LOGGING = "AUDIT_LOGGING"
    AWARENESS_TRAINING = "AWARENESS_TRAINING"
    BUSINESS_CONTINUITY = "BUSINESS_CONTINUITY"
    CHANGE_MANAGEMENT = "CHANGE_MANAGEMENT"
    COMMUNICATIONS = "COMMUNICATIONS"
    COMPLIANCE = "COMPLIANCE"
    CONFIGURATION_MANAGEMENT = "CONFIGURATION_MANAGEMENT"
    CRYPTOGRAPHY = "CRYPTOGRAPHY"
    DATA_PROTECTION = "DATA_PROTECTION"
    GOVERNANCE = "GOVERNANCE"
    IDENTIFICATION_AUTHENTICATION = "IDENTIFICATION_AUTHENTICATION"
    INCIDENT_RESPONSE = "INCIDENT_RESPONSE"
    MAINTENANCE = "MAINTENANCE"
    MEDIA_PROTECTION = "MEDIA_PROTECTION"
    PERSONNEL_SECURITY = "PERSONNEL_SECURITY"
    PHYSICAL_SECURITY = "PHYSICAL_SECURITY"
    PLANNING = "PLANNING"
    PRIVACY = "PRIVACY"
    PROGRAM_MANAGEMENT = "PROGRAM_MANAGEMENT"
    RISK_ASSESSMENT = "RISK_ASSESSMENT"
    SECURITY_ASSESSMENT = "SECURITY_ASSESSMENT"
    SUPPLY_CHAIN = "SUPPLY_CHAIN"
    SYSTEM_SERVICES = "SYSTEM_SERVICES"
    VULNERABILITY_MANAGEMENT = "VULNERABILITY_MANAGEMENT"


class MappingRelationship(str, Enum):
    """How controls relate across frameworks."""

    EQUIVALENT = "EQUIVALENT"
    PARTIAL = "PARTIAL"
    RELATED = "RELATED"
    SUPERSET = "SUPERSET"
    SUBSET = "SUBSET"


class AssessmentStatus(str, Enum):
    """Assessment lifecycle status."""

    NOT_STARTED = "NOT_STARTED"
    IN_PROGRESS = "IN_PROGRESS"
    UNDER_REVIEW = "UNDER_REVIEW"
    COMPLETED = "COMPLETED"
    ARCHIVED = "ARCHIVED"


class AssessmentResult(str, Enum):
    """Control assessment results."""

    NOT_ASSESSED = "NOT_ASSESSED"
    FULLY_IMPLEMENTED = "FULLY_IMPLEMENTED"
    PARTIALLY_IMPLEMENTED = "PARTIALLY_IMPLEMENTED"
    NOT_IMPLEMENTED = "NOT_IMPLEMENTED"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    PLANNED = "PLANNED"


class Framework(Base, TimestampMixin, TenantMixin):
    """Regulatory framework definition."""

    __tablename__ = "frameworks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    type: Mapped[FrameworkType] = mapped_column(String(50), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    version: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Source information
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    publisher: Mapped[str | None] = mapped_column(String(255), nullable=True)
    publication_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Framework metadata
    total_controls: Mapped[int] = mapped_column(Integer, default=0)
    categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_custom: Mapped[bool] = mapped_column(Boolean, default=False)

    # OSCAL support
    oscal_catalog_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oscal_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    controls = relationship("Control", back_populates="framework", cascade="all, delete-orphan")
    assessments = relationship(
        "Assessment", back_populates="framework", cascade="all, delete-orphan"
    )


class Control(Base, TimestampMixin, TenantMixin):
    """Individual control within a framework."""

    __tablename__ = "controls"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    framework_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("frameworks.id", ondelete="CASCADE"), index=True
    )

    # Control identification
    control_id: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)

    # Hierarchy
    parent_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("controls.id"), nullable=True
    )
    family: Mapped[str | None] = mapped_column(String(100), nullable=True, index=True)
    category: Mapped[ControlCategory | None] = mapped_column(String(50), nullable=True)

    # Control details
    guidance: Mapped[str | None] = mapped_column(Text, nullable=True)
    supplemental_guidance: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification
    baseline_impact: Mapped[str | None] = mapped_column(
        String(50), nullable=True
    )  # LOW, MODERATE, HIGH
    priority: Mapped[int | None] = mapped_column(Integer, nullable=True)  # P1, P2, P3

    # Implementation
    implementation_status: Mapped[AssessmentResult] = mapped_column(
        String(50), default=AssessmentResult.NOT_ASSESSED
    )
    implementation_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Parameters (for NIST controls with parameters)
    parameters: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Related artifacts
    test_procedures: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    references: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # MITRE ATT&CK specific
    tactics: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    techniques: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)
    mitigations: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # OSCAL data
    oscal_control_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    oscal_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    framework = relationship("Framework", back_populates="controls")
    parent = relationship("Control", remote_side=[id], backref="children")
    evidence_links = relationship(
        "EvidenceLink", back_populates="control", cascade="all, delete-orphan"
    )

    # Mappings
    source_mappings = relationship(
        "ControlMapping",
        foreign_keys="ControlMapping.source_control_id",
        back_populates="source_control",
    )
    target_mappings = relationship(
        "ControlMapping",
        foreign_keys="ControlMapping.target_control_id",
        back_populates="target_control",
    )


class ControlMapping(Base, TimestampMixin, TenantMixin):
    """Cross-framework control mappings."""

    __tablename__ = "control_mappings"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    source_control_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), index=True
    )
    target_control_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("controls.id", ondelete="CASCADE"), index=True
    )

    relationship_type: Mapped[MappingRelationship] = mapped_column(String(50), nullable=False)
    confidence: Mapped[float] = mapped_column(Float, default=1.0)

    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    source: Mapped[str | None] = mapped_column(String(100), nullable=True)  # UCF, NIST, manual

    # Relationships
    source_control = relationship(
        "Control", foreign_keys=[source_control_id], back_populates="source_mappings"
    )
    target_control = relationship(
        "Control", foreign_keys=[target_control_id], back_populates="target_mappings"
    )


class Assessment(Base, TimestampMixin, TenantMixin):
    """Control assessment/audit record."""

    __tablename__ = "control_assessments"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    framework_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("frameworks.id", ondelete="CASCADE"), index=True
    )

    # Assessment info
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    assessment_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # self, external, certification

    # Timeline
    start_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    completion_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[AssessmentStatus] = mapped_column(
        String(50), default=AssessmentStatus.NOT_STARTED
    )

    # Assessor
    assessor_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assessor_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    assessor_organization: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Scope
    scope_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    in_scope_controls: Mapped[list[str] | None] = mapped_column(ARRAY(String), nullable=True)

    # Results summary
    controls_assessed: Mapped[int] = mapped_column(Integer, default=0)
    controls_compliant: Mapped[int] = mapped_column(Integer, default=0)
    controls_partial: Mapped[int] = mapped_column(Integer, default=0)
    controls_non_compliant: Mapped[int] = mapped_column(Integer, default=0)
    controls_not_applicable: Mapped[int] = mapped_column(Integer, default=0)

    overall_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Assessment data
    results: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    framework = relationship("Framework", back_populates="assessments")
