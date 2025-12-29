"""
Russian Compliance API Endpoints
Company profiles, ISPDN systems, documents, tasks for 152-ФЗ, 187-ФЗ, etc.
"""

import logging
from datetime import date, datetime, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status

logger = logging.getLogger(__name__)
from pydantic import BaseModel, Field
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.v1.deps import get_current_user, get_db
from app.services.ru_task_templates import FZ152_TASK_TEMPLATES, get_task_templates_for_company, TASK_CATEGORIES
from app.models.compliance.russian import (
    DocumentStatus,
    ISPDNCategory,
    KIICategory,
    ProtectionLevel,
    ResponsibleRole,
    RuCompanyProfile,
    RuComplianceDocument,
    RuComplianceTask,
    RuDocumentTemplate,
    RuFrameworkType,
    RuISPDN,
    RuRequirement,
    RuResponsiblePerson,
    TaskPriority,
    TaskStatus,
    ThreatType,
)
from app.models.user import User
from app.services.russian_compliance import (
    DocumentTemplateService,
    ProtectionLevelCalculator,
    get_company_by_inn_demo,
)
from app.services.template_registry import TemplateRegistry, CompanyLifecycleStage

router = APIRouter(tags=["Russian Compliance"])


# ============================================================================
# SCHEMAS
# ============================================================================


class CompanyProfileCreate(BaseModel):
    """Create company profile by INN."""

    inn: str = Field(..., min_length=10, max_length=12, description="ИНН организации")


class CompanyProfileResponse(BaseModel):
    """Company profile response."""

    id: UUID
    inn: str
    kpp: str | None
    ogrn: str | None
    okpo: str | None
    full_name: str
    short_name: str | None
    legal_form: str | None
    legal_address: str | None
    actual_address: str | None
    okved_main: str | None
    okved_main_name: str | None
    director_name: str | None
    director_position: str | None
    is_pdn_operator: bool
    roskomnadzor_reg_number: str | None
    is_kii_subject: bool
    kii_category: str | None
    is_financial_org: bool
    phone: str | None
    email: str | None
    website: str | None

    class Config:
        from_attributes = True


class CompanyProfileUpdate(BaseModel):
    """Update company profile."""

    phone: str | None = None
    email: str | None = None
    website: str | None = None
    is_pdn_operator: bool | None = None
    roskomnadzor_reg_number: str | None = None
    is_kii_subject: bool | None = None
    kii_category: str | None = None
    is_financial_org: bool | None = None
    employee_count: int | None = None
    industry: str | None = None


class ResponsiblePersonCreate(BaseModel):
    """Create responsible person."""

    role: ResponsibleRole
    full_name: str
    email: str
    position: str | None = None
    department: str | None = None
    phone: str | None = None
    mobile: str | None = None


class ResponsiblePersonResponse(BaseModel):
    """Responsible person response."""

    id: UUID
    role: ResponsibleRole
    role_name_ru: str
    full_name: str
    position: str | None
    department: str | None
    email: str
    phone: str | None
    is_active: bool
    training_completed: bool
    training_date: date | None

    class Config:
        from_attributes = True


class ISPDNCreate(BaseModel):
    """Create ISPDN system."""

    name: str
    description: str | None = None
    pdn_category: ISPDNCategory
    subject_count: str  # <1000, <100000, >100000
    threat_type: ThreatType
    processing_purposes: list[str] = []
    subject_categories: list[str] = []
    pdn_types: list[str] = []


class ISPDNResponse(BaseModel):
    """ISPDN response."""

    id: UUID
    name: str
    short_name: str | None
    description: str | None
    pdn_category: ISPDNCategory
    subject_count: str
    threat_type: ThreatType
    protection_level: ProtectionLevel
    processes_special_pdn: bool
    processes_biometric: bool
    is_certified: bool
    status: str

    class Config:
        from_attributes = True


class ProtectionLevelRequest(BaseModel):
    """Request for protection level calculation."""

    pdn_category: ISPDNCategory
    subject_count: int
    threat_type: ThreatType
    is_employee_only: bool = False


class ProtectionLevelResponse(BaseModel):
    """Protection level calculation response."""

    protection_level: ProtectionLevel
    protection_level_name: str
    required_measures: dict[str, list[str]]


class DocumentTemplateResponse(BaseModel):
    """Document template response."""

    id: UUID
    template_code: str
    title: str
    title_en: str | None
    document_type: str
    framework: RuFrameworkType
    requirement_ref: str | None
    description: str | None
    is_mandatory: bool
    display_order: int

    class Config:
        from_attributes = True


class ComplianceDocumentCreate(BaseModel):
    """Create compliance document from template."""

    template_id: UUID
    ispdn_id: UUID | None = None


class ComplianceDocumentResponse(BaseModel):
    """Compliance document response."""

    id: UUID
    document_code: str
    title: str
    document_type: str
    framework: RuFrameworkType
    status: DocumentStatus
    completion_percent: int
    version: str
    document_number: str | None
    document_date: date | None
    due_date: date | None
    priority: TaskPriority

    class Config:
        from_attributes = True


class LifecycleStageTemplate(BaseModel):
    """Template info for lifecycle stage."""

    id: str
    name: str
    category: str
    priority: str = "recommended"  # required, recommended, optional
    description: str | None = None


class LifecycleStageResponse(BaseModel):
    """Response for lifecycle stage templates."""

    stage: str
    stage_name: str
    templates: list[LifecycleStageTemplate]


class ComplianceTaskResponse(BaseModel):
    """Compliance task response."""

    id: UUID
    title: str
    description: str | None
    task_type: str
    framework: RuFrameworkType
    status: TaskStatus
    priority: TaskPriority
    due_date: date | None
    assigned_to: UUID | None
    assigned_department: str | None
    assigned_role: str | None
    is_recurring: bool
    recurrence_days: int | None
    next_due_date: date | None
    started_at: datetime | None
    completed_at: datetime | None
    completion_notes: str | None
    created_at: datetime | None

    class Config:
        from_attributes = True


class TaskCreate(BaseModel):
    """Create a new compliance task."""

    title: str
    description: str | None = None
    task_type: str = "compliance"
    framework: RuFrameworkType = RuFrameworkType.FZ_152
    priority: TaskPriority = TaskPriority.MEDIUM
    due_date: date | None = None
    assigned_to: UUID | None = None
    assigned_department: str | None = None
    assigned_role: str | None = None
    is_recurring: bool = False
    recurrence_days: int | None = None
    document_id: UUID | None = None


class TaskUpdate(BaseModel):
    """Update an existing compliance task."""

    title: str | None = None
    description: str | None = None
    task_type: str | None = None
    framework: RuFrameworkType | None = None
    status: TaskStatus | None = None
    priority: TaskPriority | None = None
    due_date: date | None = None
    assigned_to: UUID | None = None
    assigned_department: str | None = None
    assigned_role: str | None = None
    is_recurring: bool | None = None
    recurrence_days: int | None = None
    completion_notes: str | None = None


class DashboardStats(BaseModel):
    """Russian compliance dashboard statistics."""

    total_documents: int
    completed_documents: int
    in_progress_documents: int
    overdue_documents: int
    total_tasks: int
    completed_tasks: int
    overdue_tasks: int
    ispdn_systems: int
    responsible_persons: int
    compliance_score: float


class INNLookupResponse(BaseModel):
    """INN lookup response."""

    found: bool
    data: dict[str, Any] | None


# ============================================================================
# COMPANY PROFILE ENDPOINTS
# ============================================================================


@router.post("/companies/lookup", response_model=INNLookupResponse)
async def lookup_company_by_inn(
    inn: str = Query(..., min_length=10, max_length=12),
    current_user: User = Depends(get_current_user),
):
    """
    Lookup company data by INN from public sources (EGRUL).
    Returns company details without creating a profile.
    """
    data = await get_company_by_inn_demo(inn)
    return INNLookupResponse(found=data is not None, data=data)


@router.post("/companies", response_model=CompanyProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_company_profile(
    data: CompanyProfileCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Create company profile by INN.
    Auto-fills data from EGRUL.
    """
    # Check if company already exists
    existing = await db.execute(
        select(RuCompanyProfile).where(
            RuCompanyProfile.inn == data.inn,
            RuCompanyProfile.tenant_id == current_user.tenant_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Company with INN {data.inn} already exists",
        )

    # Lookup company data
    egrul_data = await get_company_by_inn_demo(data.inn)
    if not egrul_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Company with INN {data.inn} not found in EGRUL",
        )

    # Create company profile
    company = RuCompanyProfile(
        tenant_id=current_user.tenant_id,
        inn=egrul_data.get("inn", data.inn),
        kpp=egrul_data.get("kpp"),
        ogrn=egrul_data.get("ogrn"),
        okpo=egrul_data.get("okpo"),
        full_name=egrul_data.get("full_name", f"Company {data.inn}"),
        short_name=egrul_data.get("short_name"),
        legal_form=egrul_data.get("legal_form"),
        legal_address=egrul_data.get("legal_address"),
        okved_main=egrul_data.get("okved_main"),
        okved_main_name=egrul_data.get("okved_main_name"),
        director_name=egrul_data.get("director_name"),
        director_position=egrul_data.get("director_position"),
        egrul_data=egrul_data,
        is_pdn_operator=True,  # Default: most companies process PD
        is_kii_subject=egrul_data.get("is_kii_subject", False),
        is_financial_org=egrul_data.get("is_financial_org", False),
    )

    db.add(company)
    await db.commit()
    await db.refresh(company)

    return company


@router.get("/companies", response_model=list[CompanyProfileResponse])
async def list_company_profiles(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List all company profiles for tenant."""
    result = await db.execute(
        select(RuCompanyProfile).where(
            RuCompanyProfile.tenant_id == current_user.tenant_id
        )
    )
    return list(result.scalars().all())


@router.get("/companies/{company_id}", response_model=CompanyProfileResponse)
async def get_company_profile(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get company profile by ID."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/companies/{company_id}", response_model=CompanyProfileResponse)
async def update_company_profile(
    company_id: UUID,
    data: CompanyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update company profile."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(company, field, value)

    await db.commit()
    await db.refresh(company)
    return company


# ============================================================================
# RESPONSIBLE PERSONS ENDPOINTS
# ============================================================================


ROLE_NAMES_RU = {
    ResponsibleRole.PDN_OPERATOR: "Оператор персональных данных",
    ResponsibleRole.PDN_RESPONSIBLE: "Ответственный за организацию обработки ПДн",
    ResponsibleRole.SECURITY_ADMIN: "Администратор информационной безопасности",
    ResponsibleRole.IT_ADMIN: "Администратор информационных технологий",
    ResponsibleRole.KII_RESPONSIBLE: "Ответственный за безопасность КИИ",
    ResponsibleRole.GOSSOPKA_CONTACT: "Контактное лицо ГосСОПКА",
    ResponsibleRole.DPO: "Уполномоченный по защите данных (DPO)",
    ResponsibleRole.CISO: "Директор по информационной безопасности (CISO)",
    ResponsibleRole.CEO: "Руководитель организации",
}


@router.post(
    "/companies/{company_id}/responsible",
    response_model=ResponsiblePersonResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_responsible_person(
    company_id: UUID,
    data: ResponsiblePersonCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Add responsible person to company."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    person = RuResponsiblePerson(
        tenant_id=current_user.tenant_id,
        company_id=company_id,
        role=data.role,
        role_name_ru=ROLE_NAMES_RU.get(data.role, data.role.value),
        full_name=data.full_name,
        email=data.email,
        position=data.position,
        department=data.department,
        phone=data.phone,
        mobile=data.mobile,
    )

    db.add(person)
    await db.commit()
    await db.refresh(person)
    return person


@router.get("/companies/{company_id}/responsible", response_model=list[ResponsiblePersonResponse])
async def list_responsible_persons(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List responsible persons for company."""
    result = await db.execute(
        select(RuResponsiblePerson).where(
            RuResponsiblePerson.company_id == company_id,
            RuResponsiblePerson.tenant_id == current_user.tenant_id,
            RuResponsiblePerson.is_active == True,
        )
    )
    return list(result.scalars().all())


# ============================================================================
# ISPDN ENDPOINTS
# ============================================================================


@router.post(
    "/companies/{company_id}/ispdn",
    response_model=ISPDNResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_ispdn(
    company_id: UUID,
    data: ISPDNCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create ISPDN system for company."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    # Calculate protection level
    subject_count_int = 100000 if data.subject_count == ">100000" else 1000
    protection_level = ProtectionLevelCalculator.calculate(
        category=data.pdn_category,
        subject_count=subject_count_int,
        threat_type=data.threat_type,
    )

    ispdn = RuISPDN(
        tenant_id=current_user.tenant_id,
        company_id=company_id,
        name=data.name,
        description=data.description,
        pdn_category=data.pdn_category,
        subject_count=data.subject_count,
        threat_type=data.threat_type,
        protection_level=protection_level,
        processing_purposes=data.processing_purposes,
        subject_categories=data.subject_categories,
        pdn_types=data.pdn_types,
        processes_special_pdn=data.pdn_category == ISPDNCategory.SPECIAL,
        processes_biometric=data.pdn_category == ISPDNCategory.BIOMETRIC,
    )

    db.add(ispdn)
    await db.commit()
    await db.refresh(ispdn)
    return ispdn


@router.get("/companies/{company_id}/ispdn", response_model=list[ISPDNResponse])
async def list_ispdn_systems(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List ISPDN systems for company."""
    result = await db.execute(
        select(RuISPDN).where(
            RuISPDN.company_id == company_id,
            RuISPDN.tenant_id == current_user.tenant_id,
        )
    )
    return list(result.scalars().all())


@router.post("/calculate-protection-level", response_model=ProtectionLevelResponse)
async def calculate_protection_level(
    data: ProtectionLevelRequest,
    current_user: User = Depends(get_current_user),
):
    """
    Calculate required protection level (УЗ) per FSTEC Order 21.
    """
    level = ProtectionLevelCalculator.calculate(
        category=data.pdn_category,
        subject_count=data.subject_count,
        threat_type=data.threat_type,
        is_employee_only=data.is_employee_only,
    )

    measures = ProtectionLevelCalculator.get_required_measures(level)

    level_names = {
        ProtectionLevel.UZ_1: "УЗ-1 (Максимальный уровень защиты)",
        ProtectionLevel.UZ_2: "УЗ-2 (Высокий уровень защиты)",
        ProtectionLevel.UZ_3: "УЗ-3 (Средний уровень защиты)",
        ProtectionLevel.UZ_4: "УЗ-4 (Базовый уровень защиты)",
    }

    return ProtectionLevelResponse(
        protection_level=level,
        protection_level_name=level_names.get(level, level.value),
        required_measures=measures,
    )


# ============================================================================
# DOCUMENT TEMPLATE ENDPOINTS
# ============================================================================


@router.get("/templates", response_model=list[DocumentTemplateResponse])
async def list_document_templates(
    framework: RuFrameworkType | None = None,
    protection_level: ProtectionLevel | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List available document templates."""
    query = select(RuDocumentTemplate).where(RuDocumentTemplate.is_active == True)

    if framework:
        query = query.where(RuDocumentTemplate.framework == framework)

    query = query.order_by(RuDocumentTemplate.display_order)

    result = await db.execute(query)
    return list(result.scalars().all())


# Lifecycle stage names in Russian
LIFECYCLE_STAGE_NAMES = {
    "idea": "Идея",
    "registration": "Регистрация",
    "launch": "Запуск",
    "growth": "Рост",
    "maturity": "Зрелость",
    "expansion": "Экспансия",
    "restructuring": "Реструктуризация",
    "exit": "Выход",
}

# Priority mapping for lifecycle templates
LIFECYCLE_PRIORITY_MAP = {
    "idea": {"founders_agreement": "required", "nda": "required", "preliminary_agreement": "recommended"},
    "registration": {
        "charter_ooo": "required", "formation_decision_sole": "required",
        "formation_decision_multiple": "required", "tax_registration": "recommended",
        "usn_application": "recommended", "account_opening": "required",
    },
    "launch": {
        "employment_contract": "required", "internal_labor_rules": "required",
        "accounting_policy": "required", "privacy_policy": "required",
        "online_terms": "recommended", "director_appointment_order": "required",
    },
    "growth": {
        "supply": "required", "service": "required", "lease": "recommended",
        "loan": "optional", "contractor_agreement": "recommended", "leasing": "optional",
    },
    "maturity": {
        "dividend_resolution": "required", "shareholder_meeting_minutes": "required",
        "quality_manual": "recommended", "sla_agreement": "recommended", "distribution": "optional",
    },
    "expansion": {
        "franchise": "recommended", "joint_venture": "recommended",
        "licensing": "recommended", "bank_guarantee": "optional",
    },
    "restructuring": {
        "restructuring_plan": "required", "creditor_agreement": "required",
        "debt_restructuring": "required", "capital_increase_decision": "recommended",
    },
    "exit": {
        "voluntary_liquidation": "required", "liquidation_decision": "required",
        "asset_sale": "recommended", "settlement": "optional",
    },
}


@router.get("/lifecycle-templates", response_model=list[LifecycleStageResponse])
async def list_lifecycle_templates(
    current_user: User = Depends(get_current_user),
):
    """Get all templates grouped by company lifecycle stage."""
    result = []

    for stage in CompanyLifecycleStage:
        stage_templates = TemplateRegistry.get_templates_for_stage(stage)
        priority_map = LIFECYCLE_PRIORITY_MAP.get(stage.value, {})

        templates = [
            LifecycleStageTemplate(
                id=t["type"],
                name=t["name"],
                category=t.get("category", "general"),
                priority=priority_map.get(t["type"], "recommended"),
                description=None,
            )
            for t in stage_templates
        ]

        result.append(LifecycleStageResponse(
            stage=stage.value,
            stage_name=LIFECYCLE_STAGE_NAMES.get(stage.value, stage.value),
            templates=templates,
        ))

    return result


@router.get("/lifecycle-templates/{stage}", response_model=LifecycleStageResponse)
async def get_lifecycle_stage_templates(
    stage: str,
    current_user: User = Depends(get_current_user),
):
    """Get templates for a specific lifecycle stage."""
    try:
        lifecycle_stage = CompanyLifecycleStage(stage)
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Invalid lifecycle stage: {stage}")

    stage_templates = TemplateRegistry.get_templates_for_stage(lifecycle_stage)
    priority_map = LIFECYCLE_PRIORITY_MAP.get(stage, {})

    templates = [
        LifecycleStageTemplate(
            id=t["type"],
            name=t["name"],
            category=t.get("category", "general"),
            priority=priority_map.get(t["type"], "recommended"),
            description=None,
        )
        for t in stage_templates
    ]

    return LifecycleStageResponse(
        stage=stage,
        stage_name=LIFECYCLE_STAGE_NAMES.get(stage, stage),
        templates=templates,
    )


@router.get("/templates/{template_id}", response_model=DocumentTemplateResponse)
async def get_document_template(
    template_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get document template by ID."""
    template = await db.get(RuDocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.get("/templates/{template_id}/preview")
async def preview_template(
    template_id: UUID,
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Preview template populated with company data."""
    template = await db.get(RuDocumentTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")

    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    service = DocumentTemplateService(db)
    content = await service.populate_template(template, company)

    return {"content": content, "template": template.title}


# ============================================================================
# COMPLIANCE DOCUMENTS ENDPOINTS
# ============================================================================


@router.post(
    "/companies/{company_id}/documents",
    response_model=ComplianceDocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_compliance_document(
    company_id: UUID,
    data: ComplianceDocumentCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create compliance document from template."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    service = DocumentTemplateService(db)
    document = await service.create_document_from_template(
        template_id=data.template_id,
        company_id=company_id,
        tenant_id=current_user.tenant_id,
    )

    await db.commit()
    await db.refresh(document)
    return document


@router.get("/companies/{company_id}/documents", response_model=list[ComplianceDocumentResponse])
async def list_compliance_documents(
    company_id: UUID,
    framework: RuFrameworkType | None = None,
    status: DocumentStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List compliance documents for company."""
    query = select(RuComplianceDocument).where(
        RuComplianceDocument.company_id == company_id,
        RuComplianceDocument.tenant_id == current_user.tenant_id,
    )

    if framework:
        query = query.where(RuComplianceDocument.framework == framework)
    if status:
        query = query.where(RuComplianceDocument.status == status)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/companies/{company_id}/documents/{document_id}")
async def get_compliance_document(
    company_id: UUID,
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance document with full content."""
    document = await db.get(RuComplianceDocument, document_id)
    if not document or document.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")

    return {
        "id": document.id,
        "document_code": document.document_code,
        "title": document.title,
        "document_type": document.document_type,
        "framework": document.framework,
        "status": document.status,
        "content": document.content,
        "content_html": document.content_html,
        "version": document.version,
        "completion_percent": document.completion_percent,
    }


@router.patch("/companies/{company_id}/documents/{document_id}")
async def update_compliance_document(
    company_id: UUID,
    document_id: UUID,
    content: str | None = None,
    status: DocumentStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update compliance document content or status."""
    document = await db.get(RuComplianceDocument, document_id)
    if not document or document.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")

    if content is not None:
        document.content = content
    if status is not None:
        document.status = status

    await db.commit()
    await db.refresh(document)
    return {"status": "updated", "id": document.id}


@router.get("/companies/{company_id}/documents/{document_id}/export/{format}")
async def export_compliance_document(
    company_id: UUID,
    document_id: UUID,
    format: str,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Export compliance document to DOCX or PDF format.

    Args:
        format: Export format ('docx' or 'pdf')
    """
    from fastapi.responses import StreamingResponse
    from app.services.document_export import document_export_service
    import io

    document = await db.get(RuComplianceDocument, document_id)
    if not document or document.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Document not found")

    company = await db.get(RuCompanyProfile, company_id)
    if not company:
        raise HTTPException(status_code=404, detail="Company not found")

    content = document.content or ""
    title = document.title

    if format.lower() == "docx":
        if not document_export_service.docx_available:
            raise HTTPException(status_code=501, detail="DOCX export not available")
        file_bytes = await document_export_service.export_to_docx(
            content=content,
            title=title,
            company_name=company.full_name,
        )
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        filename = f"{document.document_code}.docx"
    elif format.lower() == "pdf":
        if not document_export_service.pdf_available:
            raise HTTPException(status_code=501, detail="PDF export not available")
        file_bytes = await document_export_service.export_to_pdf(
            content=content,
            title=title,
            company_name=company.full_name,
        )
        media_type = "application/pdf"
        filename = f"{document.document_code}.pdf"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format. Use 'docx' or 'pdf'")

    return StreamingResponse(
        io.BytesIO(file_bytes),
        media_type=media_type,
        headers={"Content-Disposition": f"attachment; filename={filename}"}
    )


# ============================================================================
# TASKS ENDPOINTS
# ============================================================================


@router.get("/companies/{company_id}/tasks", response_model=list[ComplianceTaskResponse])
async def list_compliance_tasks(
    company_id: UUID,
    status: TaskStatus | None = None,
    framework: RuFrameworkType | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List compliance tasks for company."""
    query = select(RuComplianceTask).where(
        RuComplianceTask.company_id == company_id,
        RuComplianceTask.tenant_id == current_user.tenant_id,
    )

    if status:
        query = query.where(RuComplianceTask.status == status)
    if framework:
        query = query.where(RuComplianceTask.framework == framework)

    result = await db.execute(query)
    return list(result.scalars().all())


@router.get("/my-tasks", response_model=list[ComplianceTaskResponse])
async def list_my_tasks(
    status: TaskStatus | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """List tasks assigned to current user."""
    query = select(RuComplianceTask).where(
        RuComplianceTask.assigned_to == current_user.id,
        RuComplianceTask.tenant_id == current_user.tenant_id,
    )

    if status:
        query = query.where(RuComplianceTask.status == status)

    query = query.order_by(RuComplianceTask.due_date)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/companies/{company_id}/tasks", response_model=ComplianceTaskResponse)
async def create_task(
    company_id: UUID,
    task_data: TaskCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Create a new compliance task."""
    # Verify company exists and belongs to tenant
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    task = RuComplianceTask(
        tenant_id=current_user.tenant_id,
        company_id=company_id,
        title=task_data.title,
        description=task_data.description,
        task_type=task_data.task_type,
        framework=task_data.framework,
        priority=task_data.priority,
        status=TaskStatus.NOT_STARTED,
        due_date=task_data.due_date,
        assigned_to=task_data.assigned_to,
        assigned_department=task_data.assigned_department,
        assigned_role=task_data.assigned_role,
        is_recurring=task_data.is_recurring,
        recurrence_days=task_data.recurrence_days,
        document_id=task_data.document_id,
    )

    db.add(task)
    await db.commit()
    await db.refresh(task)

    logger.info(f"Created task {task.id} for company {company_id}")
    return task


@router.get("/companies/{company_id}/tasks/{task_id}", response_model=ComplianceTaskResponse)
async def get_task(
    company_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get a specific compliance task."""
    task = await db.get(RuComplianceTask, task_id)
    if not task or task.tenant_id != current_user.tenant_id or task.company_id != company_id:
        raise HTTPException(status_code=404, detail="Task not found")
    return task


@router.patch("/companies/{company_id}/tasks/{task_id}", response_model=ComplianceTaskResponse)
async def update_task(
    company_id: UUID,
    task_id: UUID,
    task_data: TaskUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Update a compliance task."""
    task = await db.get(RuComplianceTask, task_id)
    if not task or task.tenant_id != current_user.tenant_id or task.company_id != company_id:
        raise HTTPException(status_code=404, detail="Task not found")

    update_data = task_data.model_dump(exclude_unset=True)

    # Handle status transitions
    if "status" in update_data:
        new_status = update_data["status"]
        if new_status == TaskStatus.IN_PROGRESS and not task.started_at:
            task.started_at = datetime.utcnow()
        elif new_status == TaskStatus.COMPLETED:
            task.completed_at = datetime.utcnow()
            # Handle recurring task - create next occurrence
            if task.is_recurring and task.recurrence_days:
                next_due = (task.due_date or date.today()) + timedelta(days=task.recurrence_days)
                task.next_due_date = next_due

    for field, value in update_data.items():
        setattr(task, field, value)

    await db.commit()
    await db.refresh(task)

    logger.info(f"Updated task {task_id}")
    return task


@router.delete("/companies/{company_id}/tasks/{task_id}")
async def delete_task(
    company_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Delete a compliance task."""
    task = await db.get(RuComplianceTask, task_id)
    if not task or task.tenant_id != current_user.tenant_id or task.company_id != company_id:
        raise HTTPException(status_code=404, detail="Task not found")

    await db.delete(task)
    await db.commit()

    logger.info(f"Deleted task {task_id}")
    return {"status": "deleted", "task_id": str(task_id)}


@router.post("/companies/{company_id}/tasks/{task_id}/complete", response_model=ComplianceTaskResponse)
async def complete_task(
    company_id: UUID,
    task_id: UUID,
    completion_notes: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Mark a task as completed."""
    task = await db.get(RuComplianceTask, task_id)
    if not task or task.tenant_id != current_user.tenant_id or task.company_id != company_id:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.utcnow()
    if completion_notes:
        task.completion_notes = completion_notes

    # Handle recurring task - create next occurrence
    if task.is_recurring and task.recurrence_days and task.due_date:
        next_task = RuComplianceTask(
            tenant_id=task.tenant_id,
            company_id=task.company_id,
            title=task.title,
            description=task.description,
            task_type=task.task_type,
            framework=task.framework,
            priority=task.priority,
            status=TaskStatus.NOT_STARTED,
            due_date=task.due_date + timedelta(days=task.recurrence_days),
            assigned_to=task.assigned_to,
            assigned_department=task.assigned_department,
            assigned_role=task.assigned_role,
            is_recurring=True,
            recurrence_days=task.recurrence_days,
            document_id=task.document_id,
        )
        db.add(next_task)
        task.next_due_date = next_task.due_date

    await db.commit()
    await db.refresh(task)

    logger.info(f"Completed task {task_id}")
    return task


@router.post("/companies/{company_id}/tasks/bulk-create", response_model=list[ComplianceTaskResponse])
async def bulk_create_tasks(
    company_id: UUID,
    tasks: list[TaskCreate],
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Bulk create compliance tasks (e.g., from template)."""
    # Verify company exists and belongs to tenant
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    created_tasks = []
    for task_data in tasks:
        task = RuComplianceTask(
            tenant_id=current_user.tenant_id,
            company_id=company_id,
            title=task_data.title,
            description=task_data.description,
            task_type=task_data.task_type,
            framework=task_data.framework,
            priority=task_data.priority,
            status=TaskStatus.NOT_STARTED,
            due_date=task_data.due_date,
            assigned_to=task_data.assigned_to,
            assigned_department=task_data.assigned_department,
            assigned_role=task_data.assigned_role,
            is_recurring=task_data.is_recurring,
            recurrence_days=task_data.recurrence_days,
            document_id=task_data.document_id,
        )
        db.add(task)
        created_tasks.append(task)

    await db.commit()
    for task in created_tasks:
        await db.refresh(task)

    logger.info(f"Bulk created {len(created_tasks)} tasks for company {company_id}")
    return created_tasks


@router.get("/task-templates")
async def get_task_templates(
    current_user: User = Depends(get_current_user),
):
    """Get available task templates for 152-ФЗ."""
    return {
        "templates": FZ152_TASK_TEMPLATES,
        "categories": TASK_CATEGORIES,
        "total": len(FZ152_TASK_TEMPLATES),
    }


@router.post("/companies/{company_id}/tasks/generate-from-template", response_model=list[ComplianceTaskResponse])
async def generate_tasks_from_template(
    company_id: UUID,
    start_date: date | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate all 152-ФЗ compliance tasks for a company from templates."""
    # Verify company exists and belongs to tenant
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    # Generate tasks from templates
    task_templates = get_task_templates_for_company(start_date or date.today())

    created_tasks = []
    for template in task_templates:
        # Map priority string to enum
        priority_map = {
            "CRITICAL": TaskPriority.CRITICAL,
            "HIGH": TaskPriority.HIGH,
            "MEDIUM": TaskPriority.MEDIUM,
            "LOW": TaskPriority.LOW,
        }

        task = RuComplianceTask(
            tenant_id=current_user.tenant_id,
            company_id=company_id,
            title=template["title"],
            description=template["description"],
            task_type=template["task_type"],
            framework=RuFrameworkType.FZ_152,
            priority=priority_map.get(template["priority"], TaskPriority.MEDIUM),
            status=TaskStatus.NOT_STARTED,
            due_date=template["due_date"],
            is_recurring=template["is_recurring"],
            recurrence_days=template.get("recurrence_days"),
        )
        db.add(task)
        created_tasks.append(task)

    await db.commit()
    for task in created_tasks:
        await db.refresh(task)

    logger.info(f"Generated {len(created_tasks)} tasks from template for company {company_id}")
    return created_tasks


# ============================================================================
# DASHBOARD ENDPOINTS
# ============================================================================


@router.get("/companies/{company_id}/dashboard", response_model=DashboardStats)
async def get_compliance_dashboard(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance dashboard statistics for company."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    # Count documents by status
    doc_query = select(
        func.count(RuComplianceDocument.id).label("total"),
        func.count(RuComplianceDocument.id).filter(
            RuComplianceDocument.status == DocumentStatus.APPROVED
        ).label("completed"),
        func.count(RuComplianceDocument.id).filter(
            RuComplianceDocument.status.in_([DocumentStatus.DRAFT, DocumentStatus.IN_REVIEW])
        ).label("in_progress"),
        func.count(RuComplianceDocument.id).filter(
            RuComplianceDocument.due_date < date.today(),
            RuComplianceDocument.status != DocumentStatus.APPROVED,
        ).label("overdue"),
    ).where(
        RuComplianceDocument.company_id == company_id,
        RuComplianceDocument.tenant_id == current_user.tenant_id,
    )

    doc_result = await db.execute(doc_query)
    doc_stats = doc_result.one()

    # Count tasks
    task_query = select(
        func.count(RuComplianceTask.id).label("total"),
        func.count(RuComplianceTask.id).filter(
            RuComplianceTask.status == TaskStatus.COMPLETED
        ).label("completed"),
        func.count(RuComplianceTask.id).filter(
            RuComplianceTask.status == TaskStatus.OVERDUE
        ).label("overdue"),
    ).where(
        RuComplianceTask.company_id == company_id,
        RuComplianceTask.tenant_id == current_user.tenant_id,
    )

    task_result = await db.execute(task_query)
    task_stats = task_result.one()

    # Count ISPDN systems
    ispdn_count = await db.execute(
        select(func.count(RuISPDN.id)).where(
            RuISPDN.company_id == company_id,
            RuISPDN.tenant_id == current_user.tenant_id,
        )
    )

    # Count responsible persons
    person_count = await db.execute(
        select(func.count(RuResponsiblePerson.id)).where(
            RuResponsiblePerson.company_id == company_id,
            RuResponsiblePerson.tenant_id == current_user.tenant_id,
            RuResponsiblePerson.is_active == True,
        )
    )

    # Calculate compliance score
    total_docs = doc_stats.total or 1
    completed_docs = doc_stats.completed or 0
    compliance_score = (completed_docs / total_docs) * 100

    return DashboardStats(
        total_documents=doc_stats.total or 0,
        completed_documents=doc_stats.completed or 0,
        in_progress_documents=doc_stats.in_progress or 0,
        overdue_documents=doc_stats.overdue or 0,
        total_tasks=task_stats.total or 0,
        completed_tasks=task_stats.completed or 0,
        overdue_tasks=task_stats.overdue or 0,
        ispdn_systems=ispdn_count.scalar() or 0,
        responsible_persons=person_count.scalar() or 0,
        compliance_score=round(compliance_score, 1),
    )


# ============================================================================
# FRAMEWORKS INFO
# ============================================================================


@router.get("/frameworks")
async def list_frameworks(
    current_user: User = Depends(get_current_user),
):
    """List available Russian regulatory frameworks."""
    frameworks = [
        {
            "code": RuFrameworkType.FZ_152,
            "name": "152-ФЗ",
            "full_name": 'Федеральный закон "О персональных данных"',
            "description": "Основной закон о защите персональных данных в России",
            "regulator": "Роскомнадзор",
            "mandatory": True,
        },
        {
            "code": RuFrameworkType.FZ_187,
            "name": "187-ФЗ",
            "full_name": 'Федеральный закон "О безопасности критической информационной инфраструктуры"',
            "description": "Закон о защите объектов критической информационной инфраструктуры",
            "regulator": "ФСТЭК России / ФСБ России",
            "mandatory": False,
        },
        {
            "code": RuFrameworkType.GOST_57580,
            "name": "ГОСТ Р 57580",
            "full_name": "ГОСТ Р 57580.1-2017 Безопасность финансовых (банковских) операций",
            "description": "Стандарт безопасности для финансовых организаций",
            "regulator": "ЦБ РФ",
            "mandatory": False,
        },
        {
            "code": RuFrameworkType.FSTEC_21,
            "name": "Приказ ФСТЭК №21",
            "full_name": "Приказ ФСТЭК России от 18.02.2013 № 21",
            "description": "Меры защиты персональных данных при их обработке в ИСПДн",
            "regulator": "ФСТЭК России",
            "mandatory": True,
        },
        {
            "code": RuFrameworkType.CB_683P,
            "name": "683-П",
            "full_name": "Положение ЦБ РФ от 17.04.2019 № 683-П",
            "description": "Требования к защите информации в банках",
            "regulator": "ЦБ РФ",
            "mandatory": False,
        },
    ]
    return frameworks


# ============================================================================
# SME TEMPLATES ENDPOINTS (285+ business document templates)
# ============================================================================


class SMETemplateResponse(BaseModel):
    """SME template info."""

    id: str
    name: str
    category: str
    description: str | None = None
    tags: list[str] = []
    regulatory_refs: list[str] = []


class SMECategoryResponse(BaseModel):
    """SME template category info."""

    id: str
    name: str
    name_en: str | None = None
    template_count: int


class DocumentGenerateRequest(BaseModel):
    """Request to generate a document."""

    template_id: str
    company_data: dict = {}


class DocumentGenerateResponse(BaseModel):
    """Generated document response."""

    content: str
    template_id: str
    template_name: str


@router.get("/sme-templates", response_model=list[SMETemplateResponse])
async def list_sme_templates(
    category: str | None = Query(None, description="Filter by category"),
    search: str | None = Query(None, description="Search query"),
    current_user: User = Depends(get_current_user),
):
    """List all SME templates (285+ templates)."""
    from app.services.template_registry import TemplateRegistry, TemplateCategory

    # Get all templates or filter by category
    if category:
        try:
            cat = TemplateCategory(category)
            templates = TemplateRegistry.list_templates(cat)
        except ValueError:
            templates = TemplateRegistry.list_templates()
    else:
        templates = TemplateRegistry.list_templates()

    # Apply search filter
    if search:
        search_lower = search.lower()
        templates = [
            t for t in templates
            if search_lower in t.get("name", "").lower() or search_lower in t.get("type", "").lower()
        ]

    return [
        SMETemplateResponse(
            id=t.get("type", t.get("id", "")),
            name=t.get("name", ""),
            category=t.get("category", "general"),
            description=None,
            tags=[],
            regulatory_refs=[],
        )
        for t in templates
    ]


@router.get("/sme-templates/categories", response_model=list[SMECategoryResponse])
async def list_sme_categories(
    current_user: User = Depends(get_current_user),
):
    """List all SME template categories."""
    from app.services.template_registry import TemplateRegistry

    categories = TemplateRegistry.get_categories()

    return [
        SMECategoryResponse(
            id=cat["id"],
            name=cat["name"],
            name_en=None,
            template_count=cat["template_count"],
        )
        for cat in categories
    ]


@router.get("/sme-templates/statistics")
async def get_sme_statistics(
    current_user: User = Depends(get_current_user),
):
    """Get SME template statistics."""
    from app.services.template_registry import TemplateRegistry

    return TemplateRegistry.get_statistics()


@router.post("/sme-templates/generate", response_model=DocumentGenerateResponse)
async def generate_sme_document(
    request: DocumentGenerateRequest,
    current_user: User = Depends(get_current_user),
):
    """Generate a document from an SME template."""
    from app.services.template_registry import TemplateRegistry

    try:
        content = TemplateRegistry.generate_document(
            template_type=request.template_id,
            data=request.company_data,
        )

        # Get template name
        all_templates = TemplateRegistry.list_templates()
        template_name = next(
            (t["name"] for t in all_templates if t.get("type") == request.template_id),
            request.template_id,
        )

        return DocumentGenerateResponse(
            content=content,
            template_id=request.template_id,
            template_name=template_name,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
