"""Phase 3: Russian Compliance Tables (152-FZ, 187-FZ, GOST)

Revision ID: 003_russian
Revises: 002_phase2
Create Date: 2025-12-28

Adds tables for:
- ru_company_profiles - Company profiles with INN/EGRUL data
- ru_responsible_persons - Responsible persons per Russian law
- ru_ispdn_systems - Personal Data Information Systems
- ru_document_templates - Document template library
- ru_compliance_documents - Generated compliance documents
- ru_compliance_tasks - Compliance tasks
- ru_requirements - Requirements library
- ru_email_templates - Russian email templates
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = "003_russian"
down_revision: Union[str, None] = "002_phase2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ========================================================================
    # RU_COMPANY_PROFILES - Master company data
    # ========================================================================
    op.create_table(
        "ru_company_profiles",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        # Primary identifiers
        sa.Column("inn", sa.String(12), nullable=False, unique=True, index=True),
        sa.Column("kpp", sa.String(9), nullable=True),
        sa.Column("ogrn", sa.String(15), nullable=True),
        sa.Column("okpo", sa.String(14), nullable=True),
        # Company details
        sa.Column("full_name", sa.String(1000), nullable=False),
        sa.Column("short_name", sa.String(500), nullable=True),
        sa.Column("legal_form", sa.String(100), nullable=True),
        # Address
        sa.Column("legal_address", sa.Text, nullable=True),
        sa.Column("actual_address", sa.Text, nullable=True),
        sa.Column("postal_code", sa.String(10), nullable=True),
        sa.Column("region_code", sa.String(2), nullable=True),
        # Activity codes
        sa.Column("okved_main", sa.String(20), nullable=True),
        sa.Column("okved_main_name", sa.String(500), nullable=True),
        sa.Column("okved_additional", postgresql.ARRAY(sa.String), server_default="{}"),
        # Director
        sa.Column("director_name", sa.String(500), nullable=True),
        sa.Column("director_position", sa.String(200), nullable=True),
        sa.Column("director_inn", sa.String(12), nullable=True),
        # Registration
        sa.Column("registration_date", sa.Date, nullable=True),
        sa.Column("last_egrul_update", sa.DateTime(timezone=True), nullable=True),
        # Contact
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("email", sa.String(255), nullable=True),
        sa.Column("website", sa.String(500), nullable=True),
        # Compliance flags
        sa.Column("is_pdn_operator", sa.Boolean, server_default="true"),
        sa.Column("roskomnadzor_reg_number", sa.String(50), nullable=True),
        sa.Column("roskomnadzor_reg_date", sa.Date, nullable=True),
        sa.Column("is_kii_subject", sa.Boolean, server_default="false"),
        sa.Column("kii_category", sa.String(20), nullable=True),
        sa.Column("fstec_reg_number", sa.String(50), nullable=True),
        sa.Column("is_financial_org", sa.Boolean, server_default="false"),
        sa.Column("cb_license_number", sa.String(50), nullable=True),
        # Business info
        sa.Column("industry", sa.String(200), nullable=True),
        sa.Column("employee_count", sa.Integer, nullable=True),
        sa.Column("annual_revenue", sa.Integer, nullable=True),
        # Raw EGRUL data
        sa.Column("egrul_data", postgresql.JSONB, nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ru_company_profiles_tenant", "ru_company_profiles", ["tenant_id"])
    op.create_index("ix_ru_company_profiles_inn", "ru_company_profiles", ["inn"])

    # ========================================================================
    # RU_RESPONSIBLE_PERSONS - Appointed responsible persons
    # ========================================================================
    op.create_table(
        "ru_responsible_persons",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), nullable=False),
        # Role
        sa.Column("role", sa.String(50), nullable=False, index=True),
        sa.Column("role_name_ru", sa.String(200), nullable=False),
        # Person details
        sa.Column("full_name", sa.String(500), nullable=False),
        sa.Column("position", sa.String(200), nullable=True),
        sa.Column("department", sa.String(200), nullable=True),
        # Contact
        sa.Column("email", sa.String(255), nullable=False),
        sa.Column("phone", sa.String(50), nullable=True),
        sa.Column("mobile", sa.String(50), nullable=True),
        # Appointment
        sa.Column("order_number", sa.String(100), nullable=True),
        sa.Column("order_date", sa.Date, nullable=True),
        sa.Column("effective_from", sa.Date, nullable=True),
        sa.Column("effective_to", sa.Date, nullable=True),
        # Training
        sa.Column("training_completed", sa.Boolean, server_default="false"),
        sa.Column("training_date", sa.Date, nullable=True),
        sa.Column("training_certificate", sa.String(200), nullable=True),
        sa.Column("next_training_date", sa.Date, nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, server_default="true"),
        sa.Column("is_primary", sa.Boolean, server_default="true"),
        # GosSOPKA
        sa.Column("gossopka_login", sa.String(100), nullable=True),
        sa.Column("gossopka_certificate", sa.String(200), nullable=True),
        # Platform user link
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ru_responsible_persons_company", "ru_responsible_persons", ["company_id"])

    # ========================================================================
    # RU_ISPDN_SYSTEMS - Personal Data Information Systems
    # ========================================================================
    op.create_table(
        "ru_ispdn_systems",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), nullable=False),
        # System info
        sa.Column("name", sa.String(500), nullable=False),
        sa.Column("short_name", sa.String(100), nullable=True),
        sa.Column("description", sa.Text, nullable=True),
        # Classification
        sa.Column("pdn_category", sa.String(50), nullable=False),
        sa.Column("subject_count", sa.String(50), nullable=False),
        sa.Column("threat_type", sa.String(10), nullable=False),
        sa.Column("protection_level", sa.String(10), nullable=False),
        # Data flags
        sa.Column("processes_special_pdn", sa.Boolean, server_default="false"),
        sa.Column("processes_biometric", sa.Boolean, server_default="false"),
        sa.Column("processes_minor_pdn", sa.Boolean, server_default="false"),
        # Processing details
        sa.Column("processing_purposes", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("legal_basis", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("subject_categories", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("pdn_types", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("processing_methods", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("storage_location", sa.String(500), nullable=True),
        # Cross-border
        sa.Column("is_cross_border", sa.Boolean, server_default="false"),
        sa.Column("cross_border_countries", postgresql.ARRAY(sa.String), server_default="{}"),
        # Third parties
        sa.Column("third_party_access", sa.Boolean, server_default="false"),
        sa.Column("processors", postgresql.ARRAY(sa.String), server_default="{}"),
        # Technical
        sa.Column("servers", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("networks", sa.String(200), nullable=True),
        sa.Column("is_connected_to_internet", sa.Boolean, server_default="true"),
        # Security
        sa.Column("security_measures", postgresql.JSONB, nullable=True),
        sa.Column("crypto_used", sa.Boolean, server_default="false"),
        sa.Column("crypto_class", sa.String(20), nullable=True),
        # Certification
        sa.Column("is_certified", sa.Boolean, server_default="false"),
        sa.Column("certification_date", sa.Date, nullable=True),
        sa.Column("certification_number", sa.String(100), nullable=True),
        sa.Column("certification_expires", sa.Date, nullable=True),
        # Classification act
        sa.Column("classification_act_number", sa.String(100), nullable=True),
        sa.Column("classification_act_date", sa.Date, nullable=True),
        # Threat model
        sa.Column("threat_model_version", sa.String(50), nullable=True),
        sa.Column("threat_model_date", sa.Date, nullable=True),
        # Audit
        sa.Column("last_audit_date", sa.Date, nullable=True),
        sa.Column("next_audit_date", sa.Date, nullable=True),
        # Status
        sa.Column("status", sa.String(50), server_default="'ACTIVE'"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ru_ispdn_company", "ru_ispdn_systems", ["company_id"])

    # ========================================================================
    # RU_DOCUMENT_TEMPLATES - System-wide templates
    # ========================================================================
    op.create_table(
        "ru_document_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        # Template identification
        sa.Column("template_code", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("title_en", sa.String(1000), nullable=True),
        sa.Column("document_type", sa.String(50), nullable=False),
        # Framework
        sa.Column("framework", sa.String(50), nullable=False, index=True),
        sa.Column("requirement_ref", sa.String(100), nullable=True),
        # Content
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("template_content", sa.Text, nullable=False),
        sa.Column("template_html", sa.Text, nullable=True),
        # Form
        sa.Column("form_schema", postgresql.JSONB, nullable=True),
        sa.Column("form_fields", postgresql.JSONB, server_default="[]"),
        sa.Column("autofill_mappings", postgresql.JSONB, nullable=True),
        # Dependencies
        sa.Column("requires_ispdn", sa.Boolean, server_default="false"),
        sa.Column("requires_templates", postgresql.ARRAY(sa.String), server_default="{}"),
        # Categorization
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("tags", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("applicable_uz", postgresql.ARRAY(sa.String), server_default="{}"),
        # Metadata
        sa.Column("version", sa.String(20), server_default="'1.0'"),
        sa.Column("is_mandatory", sa.Boolean, server_default="true"),
        sa.Column("display_order", sa.Integer, server_default="0"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ========================================================================
    # RU_COMPLIANCE_DOCUMENTS - Per-company documents
    # ========================================================================
    op.create_table(
        "ru_compliance_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("template_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_document_templates.id"), nullable=True),
        sa.Column("ispdn_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_ispdn_systems.id"), nullable=True),
        # Document identification
        sa.Column("document_code", sa.String(50), nullable=False, index=True),
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("document_type", sa.String(50), nullable=False),
        # Framework
        sa.Column("framework", sa.String(50), nullable=False, index=True),
        sa.Column("requirement_ref", sa.String(100), nullable=True),
        # Content
        sa.Column("content", sa.Text, nullable=True),
        sa.Column("content_html", sa.Text, nullable=True),
        sa.Column("content_data", postgresql.JSONB, nullable=True),
        # Status
        sa.Column("status", sa.String(50), server_default="'НЕ НАЧАТ'", index=True),
        sa.Column("completion_percent", sa.Integer, server_default="0"),
        # File
        sa.Column("file_path", sa.String(1000), nullable=True),
        sa.Column("file_format", sa.String(20), nullable=True),
        sa.Column("file_size", sa.Integer, nullable=True),
        # Version
        sa.Column("version", sa.String(20), server_default="'1.0'"),
        # Approval workflow
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("reviewer_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approver_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
        # Document details
        sa.Column("document_number", sa.String(100), nullable=True),
        sa.Column("document_date", sa.Date, nullable=True),
        sa.Column("effective_date", sa.Date, nullable=True),
        sa.Column("expires_date", sa.Date, nullable=True),
        # Review
        sa.Column("next_review_date", sa.Date, nullable=True),
        sa.Column("review_frequency_days", sa.Integer, server_default="365"),
        # Assignment
        sa.Column("priority", sa.String(20), server_default="'СРЕДНИЙ'"),
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("department", sa.String(200), nullable=True),
        sa.Column("due_date", sa.Date, nullable=True),
        # Notifications
        sa.Column("reminder_sent", sa.Boolean, server_default="false"),
        sa.Column("last_reminder_date", sa.Date, nullable=True),
        # Dependencies
        sa.Column("depends_on", postgresql.ARRAY(sa.String), server_default="{}"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ru_compliance_docs_company", "ru_compliance_documents", ["company_id"])

    # ========================================================================
    # RU_COMPLIANCE_TASKS - Compliance tasks
    # ========================================================================
    op.create_table(
        "ru_compliance_tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("tenant_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tenants.id", ondelete="CASCADE"), nullable=False),
        sa.Column("company_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_company_profiles.id", ondelete="CASCADE"), nullable=False),
        sa.Column("document_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("ru_compliance_documents.id", ondelete="SET NULL"), nullable=True),
        # Task details
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("description", sa.Text, nullable=True),
        sa.Column("task_type", sa.String(50), nullable=False),
        # Framework
        sa.Column("framework", sa.String(50), nullable=False, index=True),
        sa.Column("requirement_ref", sa.String(100), nullable=True),
        # Assignment
        sa.Column("assigned_to", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id"), nullable=True),
        sa.Column("assigned_department", sa.String(200), nullable=True),
        sa.Column("assigned_role", sa.String(50), nullable=True),
        # Status
        sa.Column("status", sa.String(50), server_default="'НЕ_НАЧАТ'", index=True),
        sa.Column("priority", sa.String(20), server_default="'СРЕДНИЙ'"),
        # Dates
        sa.Column("due_date", sa.Date, nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        # Recurrence
        sa.Column("is_recurring", sa.Boolean, server_default="false"),
        sa.Column("recurrence_days", sa.Integer, nullable=True),
        sa.Column("next_due_date", sa.Date, nullable=True),
        # Notifications
        sa.Column("notification_sent", sa.Boolean, server_default="false"),
        sa.Column("reminder_sent", sa.Boolean, server_default="false"),
        sa.Column("overdue_notified", sa.Boolean, server_default="false"),
        # Completion
        sa.Column("completion_notes", sa.Text, nullable=True),
        sa.Column("evidence_path", sa.String(1000), nullable=True),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )
    op.create_index("ix_ru_tasks_company", "ru_compliance_tasks", ["company_id"])

    # ========================================================================
    # RU_REQUIREMENTS - Requirements library
    # ========================================================================
    op.create_table(
        "ru_requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        # Requirement identification
        sa.Column("requirement_code", sa.String(100), nullable=False, unique=True, index=True),
        sa.Column("framework", sa.String(50), nullable=False, index=True),
        # Reference
        sa.Column("article_number", sa.String(50), nullable=True),
        sa.Column("paragraph_number", sa.String(50), nullable=True),
        sa.Column("full_reference", sa.String(500), nullable=False),
        # Content
        sa.Column("title", sa.String(1000), nullable=False),
        sa.Column("description", sa.Text, nullable=False),
        sa.Column("guidance", sa.Text, nullable=True),
        # Applicability
        sa.Column("applicable_uz", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("applicable_kii", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("applicable_industries", postgresql.ARRAY(sa.String), server_default="{}"),
        # Evidence
        sa.Column("required_evidence", postgresql.ARRAY(sa.String), server_default="{}"),
        sa.Column("required_documents", postgresql.ARRAY(sa.String), server_default="{}"),
        # Mapping
        sa.Column("mapped_controls", postgresql.ARRAY(sa.String), server_default="{}"),
        # Metadata
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("subcategory", sa.String(100), nullable=True),
        sa.Column("is_mandatory", sa.Boolean, server_default="true"),
        sa.Column("is_active", sa.Boolean, server_default="true"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )

    # ========================================================================
    # RU_EMAIL_TEMPLATES - Russian email templates
    # ========================================================================
    op.create_table(
        "ru_email_templates",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        # Template identification
        sa.Column("template_code", sa.String(50), nullable=False, unique=True, index=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("description", sa.String(500), nullable=True),
        # Content
        sa.Column("subject", sa.String(500), nullable=False),
        sa.Column("body_text", sa.Text, nullable=False),
        sa.Column("body_html", sa.Text, nullable=True),
        # Variables
        sa.Column("variables", postgresql.ARRAY(sa.String), server_default="{}"),
        # Categorization
        sa.Column("category", sa.String(50), nullable=False),
        sa.Column("framework", sa.String(50), nullable=True),
        # Status
        sa.Column("is_active", sa.Boolean, server_default="true"),
        # Timestamps
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()")),
    )


def downgrade() -> None:
    op.drop_table("ru_email_templates")
    op.drop_table("ru_requirements")
    op.drop_table("ru_compliance_tasks")
    op.drop_table("ru_compliance_documents")
    op.drop_table("ru_document_templates")
    op.drop_table("ru_ispdn_systems")
    op.drop_table("ru_responsible_persons")
    op.drop_table("ru_company_profiles")
