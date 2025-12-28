"""
Russian Compliance Requirements Models
Models for 152-ФЗ, 187-ФЗ, ГОСТ Р 57580, ЦБ РФ, ФСТЭК, ФСБ requirements
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


# ============================================================================
# ENUMS
# ============================================================================


class RuFrameworkType(str, Enum):
    """Russian regulatory frameworks."""

    FZ_152 = "152-ФЗ"  # Personal Data
    FZ_187 = "187-ФЗ"  # Critical Infrastructure (КИИ)
    FZ_149 = "149-ФЗ"  # Information
    FZ_242 = "242-ФЗ"  # Data Localization
    GOST_57580 = "ГОСТ Р 57580"  # Banking Security
    CB_683P = "683-П"  # Central Bank
    CB_719P = "719-П"
    CB_747P = "747-П"
    FSTEC_21 = "ФСТЭК №21"  # ISPDN Protection
    FSTEC_17 = "ФСТЭК №17"  # Government Systems
    FSTEC_239 = "ФСТЭК №239"  # КИИ Security
    FSTEC_235 = "ФСТЭК №235"  # КИИ Categorization
    FSB_378 = "ФСБ №378"  # Crypto Protection
    FSB_GOSSOPKA = "ГосСОПКА"  # Incident Response


class ProtectionLevel(str, Enum):
    """FSTEC Protection Levels (УЗ)."""

    UZ_1 = "УЗ-1"  # Maximum protection
    UZ_2 = "УЗ-2"
    UZ_3 = "УЗ-3"
    UZ_4 = "УЗ-4"  # Minimum protection


class ISPDNCategory(str, Enum):
    """ISPDN personal data categories."""

    SPECIAL = "СПЕЦИАЛЬНЫЕ"  # Race, politics, health, etc.
    BIOMETRIC = "БИОМЕТРИЧЕСКИЕ"
    PUBLIC = "ОБЩЕДОСТУПНЫЕ"
    OTHER = "ИНЫЕ"


class ThreatType(str, Enum):
    """Threat types for 152-ФЗ."""

    TYPE_1 = "1"  # Undocumented capabilities in system software
    TYPE_2 = "2"  # Undocumented capabilities in application software
    TYPE_3 = "3"  # No undocumented capabilities


class KIICategory(str, Enum):
    """КИИ significance categories per 187-ФЗ."""

    CATEGORY_1 = "1"  # Most critical
    CATEGORY_2 = "2"
    CATEGORY_3 = "3"
    NOT_SIGNIFICANT = "НЕ ЗНАЧИМЫЙ"


class DocumentStatus(str, Enum):
    """Russian compliance document status."""

    NOT_STARTED = "НЕ НАЧАТ"
    DRAFT = "ЧЕРНОВИК"
    IN_REVIEW = "НА ПРОВЕРКЕ"
    PENDING_APPROVAL = "НА УТВЕРЖДЕНИИ"
    APPROVED = "УТВЕРЖДЁН"
    NEEDS_UPDATE = "ТРЕБУЕТ ОБНОВЛЕНИЯ"
    ARCHIVED = "В АРХИВЕ"


class DocumentType(str, Enum):
    """Russian document types."""

    POLICY = "ПОЛИТИКА"
    ORDER = "ПРИКАЗ"
    INSTRUCTION = "ИНСТРУКЦИЯ"
    REGULATION = "ПОЛОЖЕНИЕ"
    JOURNAL = "ЖУРНАЛ"
    ACT = "АКТ"
    CONSENT = "СОГЛАСИЕ"
    MODEL = "МОДЕЛЬ"
    LIST = "ПЕРЕЧЕНЬ"
    CONTRACT = "ДОГОВОР"
    NOTIFICATION = "УВЕДОМЛЕНИЕ"
    REPORT = "ОТЧЁТ"
    CHECKLIST = "ЧЕКЛИСТ"


class ResponsibleRole(str, Enum):
    """Responsible person roles per Russian law."""

    PDN_OPERATOR = "ОПЕРАТОР_ПДН"  # Personal Data Operator
    PDN_RESPONSIBLE = "ОТВЕТСТВЕННЫЙ_ПДН"  # Responsible for PD Organization
    SECURITY_ADMIN = "АДМИНИСТРАТОР_ИБ"  # Security Administrator
    IT_ADMIN = "АДМИНИСТРАТОР_ИТ"  # IT Administrator
    KII_RESPONSIBLE = "ОТВЕТСТВЕННЫЙ_КИИ"  # КИИ Responsible
    GOSSOPKA_CONTACT = "КОНТАКТ_ГОССОПКА"  # GosSOPKA Contact
    DPO = "ДПО"  # Data Protection Officer
    CISO = "CISO"
    CEO = "РУКОВОДИТЕЛЬ"


class TaskPriority(str, Enum):
    """Task priority levels."""

    CRITICAL = "КРИТИЧЕСКИЙ"
    HIGH = "ВЫСОКИЙ"
    MEDIUM = "СРЕДНИЙ"
    LOW = "НИЗКИЙ"


class TaskStatus(str, Enum):
    """Task status."""

    NOT_STARTED = "НЕ_НАЧАТ"
    IN_PROGRESS = "В_РАБОТЕ"
    PENDING_REVIEW = "НА_ПРОВЕРКЕ"
    COMPLETED = "ЗАВЕРШЁН"
    OVERDUE = "ПРОСРОЧЕН"
    BLOCKED = "ЗАБЛОКИРОВАН"


# ============================================================================
# COMPANY PROFILE
# ============================================================================


class RuCompanyProfile(Base, TimestampMixin, TenantMixin):
    """
    Russian company profile with official details.
    Auto-filled from EGRUL by INN.
    """

    __tablename__ = "ru_company_profiles"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Primary identifiers (auto-filled from EGRUL)
    inn: Mapped[str] = mapped_column(String(12), nullable=False, unique=True, index=True)
    kpp: Mapped[str | None] = mapped_column(String(9), nullable=True)
    ogrn: Mapped[str | None] = mapped_column(String(15), nullable=True)
    okpo: Mapped[str | None] = mapped_column(String(14), nullable=True)

    # Company details (auto-filled from EGRUL)
    full_name: Mapped[str] = mapped_column(String(1000), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    legal_form: Mapped[str | None] = mapped_column(String(100), nullable=True)  # ООО, АО, etc.

    # Address
    legal_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    actual_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    postal_code: Mapped[str | None] = mapped_column(String(10), nullable=True)
    region_code: Mapped[str | None] = mapped_column(String(2), nullable=True)

    # Activity codes (auto-filled)
    okved_main: Mapped[str | None] = mapped_column(String(20), nullable=True)
    okved_main_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    okved_additional: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Director (auto-filled)
    director_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    director_position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    director_inn: Mapped[str | None] = mapped_column(String(12), nullable=True)

    # Registration dates
    registration_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    last_egrul_update: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Contact info (manual entry)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Compliance-specific
    is_pdn_operator: Mapped[bool] = mapped_column(Boolean, default=True)
    roskomnadzor_reg_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    roskomnadzor_reg_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    is_kii_subject: Mapped[bool] = mapped_column(Boolean, default=False)
    kii_category: Mapped[str | None] = mapped_column(String(20), nullable=True)
    fstec_reg_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    is_financial_org: Mapped[bool] = mapped_column(Boolean, default=False)
    cb_license_number: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Industry classification
    industry: Mapped[str | None] = mapped_column(String(200), nullable=True)
    employee_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    annual_revenue: Mapped[int | None] = mapped_column(Integer, nullable=True)  # In rubles

    # Metadata
    egrul_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Full EGRUL response

    # Relationships
    responsible_persons = relationship(
        "RuResponsiblePerson", back_populates="company", cascade="all, delete-orphan"
    )
    ispdn_systems = relationship(
        "RuISPDN", back_populates="company", cascade="all, delete-orphan"
    )
    documents = relationship(
        "RuComplianceDocument", back_populates="company", cascade="all, delete-orphan"
    )
    tasks = relationship(
        "RuComplianceTask", back_populates="company", cascade="all, delete-orphan"
    )


# ============================================================================
# RESPONSIBLE PERSONS
# ============================================================================


class RuResponsiblePerson(Base, TimestampMixin, TenantMixin):
    """
    Responsible persons for compliance per Russian law.
    Required roles: PDN responsible, security admin, etc.
    """

    __tablename__ = "ru_responsible_persons"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), index=True
    )

    # Role
    role: Mapped[ResponsibleRole] = mapped_column(String(50), nullable=False, index=True)
    role_name_ru: Mapped[str] = mapped_column(String(200), nullable=False)  # Display name

    # Person details
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)
    position: Mapped[str | None] = mapped_column(String(200), nullable=True)
    department: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Contact
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    phone: Mapped[str | None] = mapped_column(String(50), nullable=True)
    mobile: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Appointment
    order_number: Mapped[str | None] = mapped_column(String(100), nullable=True)  # Приказ о назначении
    order_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_from: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_to: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Training
    training_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    training_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    training_certificate: Mapped[str | None] = mapped_column(String(200), nullable=True)
    next_training_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_primary: Mapped[bool] = mapped_column(Boolean, default=True)  # Primary contact for role

    # GosSOPKA specific
    gossopka_login: Mapped[str | None] = mapped_column(String(100), nullable=True)
    gossopka_certificate: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Link to platform user
    user_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    company = relationship("RuCompanyProfile", back_populates="responsible_persons")


# ============================================================================
# ISPDN - Personal Data Information Systems
# ============================================================================


class RuISPDN(Base, TimestampMixin, TenantMixin):
    """
    ISPDN (Information System for Personal Data) per 152-ФЗ.
    Each system requires classification and protection measures.
    """

    __tablename__ = "ru_ispdn_systems"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), index=True
    )

    # System identification
    name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Classification (per FSTEC Order 21)
    pdn_category: Mapped[ISPDNCategory] = mapped_column(String(50), nullable=False)
    subject_count: Mapped[str] = mapped_column(String(50), nullable=False)  # <1000, <100000, >100000
    threat_type: Mapped[ThreatType] = mapped_column(String(10), nullable=False)
    protection_level: Mapped[ProtectionLevel] = mapped_column(String(10), nullable=False)

    # Data categories
    processes_special_pdn: Mapped[bool] = mapped_column(Boolean, default=False)
    processes_biometric: Mapped[bool] = mapped_column(Boolean, default=False)
    processes_minor_pdn: Mapped[bool] = mapped_column(Boolean, default=False)

    # Processing purposes
    processing_purposes: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    legal_basis: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Data subjects
    subject_categories: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Employees, clients, etc.
    pdn_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # FIO, passport, phone, etc.

    # Processing details
    processing_methods: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Automated, mixed
    storage_location: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_cross_border: Mapped[bool] = mapped_column(Boolean, default=False)
    cross_border_countries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Third parties
    third_party_access: Mapped[bool] = mapped_column(Boolean, default=False)
    processors: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # List of processors

    # Technical details
    servers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    networks: Mapped[str | None] = mapped_column(String(200), nullable=True)
    is_connected_to_internet: Mapped[bool] = mapped_column(Boolean, default=True)

    # Security measures
    security_measures: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Checklist per УЗ
    crypto_used: Mapped[bool] = mapped_column(Boolean, default=False)
    crypto_class: Mapped[str | None] = mapped_column(String(20), nullable=True)  # КС1, КС2, КС3, КВ, КА

    # Certification
    is_certified: Mapped[bool] = mapped_column(Boolean, default=False)
    certification_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    certification_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    certification_expires: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Classification act
    classification_act_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    classification_act_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Threat model
    threat_model_version: Mapped[str | None] = mapped_column(String(50), nullable=True)
    threat_model_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Audit
    last_audit_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    next_audit_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default="ACTIVE")  # ACTIVE, DECOMMISSIONED, PLANNED

    # Relationships
    company = relationship("RuCompanyProfile", back_populates="ispdn_systems")


# ============================================================================
# COMPLIANCE DOCUMENTS
# ============================================================================


class RuComplianceDocument(Base, TimestampMixin, TenantMixin):
    """
    Compliance documents for Russian frameworks.
    Pre-filled templates that can be edited and completed.
    """

    __tablename__ = "ru_compliance_documents"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), index=True
    )
    template_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_document_templates.id"), nullable=True
    )
    ispdn_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_ispdn_systems.id"), nullable=True
    )

    # Document identification
    document_code: Mapped[str] = mapped_column(String(50), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False)

    # Framework
    framework: Mapped[RuFrameworkType] = mapped_column(String(50), nullable=False, index=True)
    requirement_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)  # e.g., "п.2 ч.1 ст.18.1"

    # Content
    content: Mapped[str | None] = mapped_column(Text, nullable=True)  # Filled content
    content_html: Mapped[str | None] = mapped_column(Text, nullable=True)  # HTML for editor
    content_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Form field values

    # Status
    status: Mapped[DocumentStatus] = mapped_column(String(50), default=DocumentStatus.NOT_STARTED, index=True)
    completion_percent: Mapped[int] = mapped_column(Integer, default=0)

    # File storage
    file_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    file_format: Mapped[str | None] = mapped_column(String(20), nullable=True)  # PDF, DOCX
    file_size: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # Versioning
    version: Mapped[str] = mapped_column(String(20), default="1.0")

    # Approval workflow
    owner_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    reviewer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approver_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Document details (for official documents)
    document_number: Mapped[str | None] = mapped_column(String(100), nullable=True)
    document_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    effective_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    expires_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Review
    next_review_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    review_frequency_days: Mapped[int] = mapped_column(Integer, default=365)

    # Priority and assignment
    priority: Mapped[TaskPriority] = mapped_column(String(20), default=TaskPriority.MEDIUM)
    assigned_to: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Notifications
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    last_reminder_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Dependencies
    depends_on: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Other document codes

    # Relationships
    company = relationship("RuCompanyProfile", back_populates="documents")
    template = relationship("RuDocumentTemplate")


# ============================================================================
# DOCUMENT TEMPLATES
# ============================================================================


class RuDocumentTemplate(Base, TimestampMixin):
    """
    Pre-built Russian compliance document templates.
    System-wide templates that can be instantiated per company.
    """

    __tablename__ = "ru_document_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Template identification
    template_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    title_en: Mapped[str | None] = mapped_column(String(1000), nullable=True)  # English title
    document_type: Mapped[DocumentType] = mapped_column(String(50), nullable=False)

    # Framework
    framework: Mapped[RuFrameworkType] = mapped_column(String(50), nullable=False, index=True)
    requirement_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Template content
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    template_content: Mapped[str] = mapped_column(Text, nullable=False)  # Template with placeholders
    template_html: Mapped[str | None] = mapped_column(Text, nullable=True)  # HTML template

    # Form definition
    form_schema: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # JSON schema for form
    form_fields: Mapped[list[dict]] = mapped_column(JSONB, default=list)  # Field definitions

    # Auto-fill mappings
    autofill_mappings: Mapped[dict | None] = mapped_column(JSONB, nullable=True)  # Field -> company data

    # Dependencies
    requires_ispdn: Mapped[bool] = mapped_column(Boolean, default=False)  # Needs ISPDN selection
    requires_templates: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Required before this

    # Categorization
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    tags: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Protection level applicability
    applicable_uz: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # УЗ-1, УЗ-2, etc.

    # Metadata
    version: Mapped[str] = mapped_column(String(20), default="1.0")
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)
    display_order: Mapped[int] = mapped_column(Integer, default=0)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ============================================================================
# COMPLIANCE TASKS
# ============================================================================


class RuComplianceTask(Base, TimestampMixin, TenantMixin):
    """
    Compliance tasks assigned to users/departments.
    Tasks for document completion, evidence collection, reviews, etc.
    """

    __tablename__ = "ru_compliance_tasks"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    company_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), index=True
    )
    document_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("ru_compliance_documents.id", ondelete="SET NULL"), nullable=True
    )

    # Task details
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    task_type: Mapped[str] = mapped_column(String(50), nullable=False)  # DOCUMENT, REVIEW, EVIDENCE, TRAINING

    # Framework
    framework: Mapped[RuFrameworkType] = mapped_column(String(50), nullable=False, index=True)
    requirement_ref: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Assignment
    assigned_to: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    assigned_department: Mapped[str | None] = mapped_column(String(200), nullable=True)
    assigned_role: Mapped[ResponsibleRole | None] = mapped_column(String(50), nullable=True)

    # Status
    status: Mapped[TaskStatus] = mapped_column(String(50), default=TaskStatus.NOT_STARTED, index=True)
    priority: Mapped[TaskPriority] = mapped_column(String(20), default=TaskPriority.MEDIUM)

    # Dates
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    started_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Recurrence
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_days: Mapped[int | None] = mapped_column(Integer, nullable=True)
    next_due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Notifications
    notification_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    reminder_sent: Mapped[bool] = mapped_column(Boolean, default=False)
    overdue_notified: Mapped[bool] = mapped_column(Boolean, default=False)

    # Completion
    completion_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    evidence_path: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Relationships
    company = relationship("RuCompanyProfile", back_populates="tasks")


# ============================================================================
# REQUIREMENTS LIBRARY
# ============================================================================


class RuRequirement(Base, TimestampMixin):
    """
    Russian compliance requirements library.
    Pre-built requirements from all frameworks.
    """

    __tablename__ = "ru_requirements"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Requirement identification
    requirement_code: Mapped[str] = mapped_column(String(100), nullable=False, unique=True, index=True)
    framework: Mapped[RuFrameworkType] = mapped_column(String(50), nullable=False, index=True)

    # Reference
    article_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    paragraph_number: Mapped[str | None] = mapped_column(String(50), nullable=True)
    full_reference: Mapped[str] = mapped_column(String(500), nullable=False)  # e.g., "ст. 18.1 ч. 2 п. 1"

    # Content
    title: Mapped[str] = mapped_column(String(1000), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    guidance: Mapped[str | None] = mapped_column(Text, nullable=True)  # How to comply

    # Applicability
    applicable_uz: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applicable_kii: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    applicable_industries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Evidence
    required_evidence: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    required_documents: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Template codes

    # Mapping
    mapped_controls: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # ISO, SOC2 mappings

    # Metadata
    category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    subcategory: Mapped[str | None] = mapped_column(String(100), nullable=True)
    is_mandatory: Mapped[bool] = mapped_column(Boolean, default=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


# ============================================================================
# EMAIL TEMPLATES (RUSSIAN)
# ============================================================================


class RuEmailTemplate(Base, TimestampMixin):
    """
    Russian email templates for notifications.
    Pre-built templates for task assignment, reminders, etc.
    """

    __tablename__ = "ru_email_templates"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Template identification
    template_code: Mapped[str] = mapped_column(String(50), nullable=False, unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    # Email content
    subject: Mapped[str] = mapped_column(String(500), nullable=False)
    body_text: Mapped[str] = mapped_column(Text, nullable=False)
    body_html: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Variables
    variables: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)  # Available placeholders

    # Categorization
    category: Mapped[str] = mapped_column(String(50), nullable=False)  # ASSIGNMENT, REMINDER, OVERDUE, etc.
    framework: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
