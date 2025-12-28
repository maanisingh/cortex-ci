"""
Russian Compliance Onboarding API
Complete lifecycle from company registration to full compliance
"""

from datetime import date, timedelta
from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user, get_db
from app.models.compliance.russian import (
    DocumentStatus,
    ISPDNCategory,
    ProtectionLevel,
    ResponsibleRole,
    RuCompanyProfile,
    RuComplianceDocument,
    RuComplianceTask,
    RuDocumentTemplate,
    RuISPDN,
    RuResponsiblePerson,
    TaskPriority,
    TaskStatus,
    ThreatType,
    RuFrameworkType,
)
from app.models.user import User
from app.services.russian_compliance import (
    ProtectionLevelCalculator,
    get_company_by_inn_demo,
)
from app.services.ru_templates_152fz import get_all_fz152_templates, get_mandatory_templates

router = APIRouter(prefix="/onboarding", tags=["Russian Compliance Onboarding"])


# ============================================================================
# SCHEMAS
# ============================================================================


class OnboardingStep1(BaseModel):
    """Step 1: Company Registration."""

    inn: str = Field(..., min_length=10, max_length=12)


class OnboardingStep2(BaseModel):
    """Step 2: Responsible Persons."""

    persons: list[dict[str, Any]]


class ResponsiblePersonInput(BaseModel):
    """Input for responsible person."""

    role: ResponsibleRole
    full_name: str
    email: str
    position: str | None = None
    phone: str | None = None


class OnboardingStep3(BaseModel):
    """Step 3: ISPDN Systems."""

    systems: list[dict[str, Any]]


class ISPDNInput(BaseModel):
    """Input for ISPDN system."""

    name: str
    description: str | None = None
    pdn_category: ISPDNCategory
    subject_count: str  # <1000, <100000, >100000
    threat_type: ThreatType
    processing_purposes: list[str] = []
    subject_categories: list[str] = []
    pdn_types: list[str] = []


class OnboardingStep4(BaseModel):
    """Step 4: Document Package Selection."""

    framework: str = "152-ФЗ"
    generate_all_mandatory: bool = True
    selected_templates: list[str] = []


class OnboardingStep5(BaseModel):
    """Step 5: Task Assignment."""

    assign_tasks: bool = True
    deadline_days: int = 30


class OnboardingStatus(BaseModel):
    """Onboarding status response."""

    company_id: str | None
    current_step: int
    steps_completed: list[int]
    company_name: str | None
    inn: str | None
    responsible_count: int
    ispdn_count: int
    document_count: int
    task_count: int
    compliance_score: float


class FullOnboardingRequest(BaseModel):
    """Complete onboarding in one request."""

    # Step 1: Company
    inn: str

    # Step 2: Responsible Persons
    pdn_responsible: ResponsiblePersonInput | None = None
    security_admin: ResponsiblePersonInput | None = None

    # Step 3: ISPDN Systems
    ispdn_systems: list[ISPDNInput] = []

    # Step 4: Documents
    generate_fz152_package: bool = True

    # Step 5: Tasks
    assign_tasks: bool = True
    task_deadline_days: int = 30


class OnboardingResult(BaseModel):
    """Result of onboarding process."""

    success: bool
    company_id: str
    company_name: str
    responsible_persons_created: int
    ispdn_systems_created: int
    documents_generated: int
    tasks_created: int
    protection_levels: dict[str, str]
    next_steps: list[str]


# ============================================================================
# ROLE NAMES
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


# ============================================================================
# ONBOARDING ENDPOINTS
# ============================================================================


@router.get("/status", response_model=OnboardingStatus)
async def get_onboarding_status(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get current onboarding status for tenant."""
    # Check if company exists
    company_result = await db.execute(
        select(RuCompanyProfile).where(
            RuCompanyProfile.tenant_id == current_user.tenant_id
        ).limit(1)
    )
    company = company_result.scalar_one_or_none()

    if not company:
        return OnboardingStatus(
            company_id=None,
            current_step=1,
            steps_completed=[],
            company_name=None,
            inn=None,
            responsible_count=0,
            ispdn_count=0,
            document_count=0,
            task_count=0,
            compliance_score=0,
        )

    # Count related entities
    responsible_count = await db.execute(
        select(RuResponsiblePerson).where(
            RuResponsiblePerson.company_id == company.id
        )
    )
    responsible_list = list(responsible_count.scalars().all())

    ispdn_count = await db.execute(
        select(RuISPDN).where(RuISPDN.company_id == company.id)
    )
    ispdn_list = list(ispdn_count.scalars().all())

    document_count = await db.execute(
        select(RuComplianceDocument).where(
            RuComplianceDocument.company_id == company.id
        )
    )
    document_list = list(document_count.scalars().all())

    task_count = await db.execute(
        select(RuComplianceTask).where(RuComplianceTask.company_id == company.id)
    )
    task_list = list(task_count.scalars().all())

    # Determine completed steps
    steps_completed = [1]  # Company exists
    if len(responsible_list) > 0:
        steps_completed.append(2)
    if len(ispdn_list) > 0:
        steps_completed.append(3)
    if len(document_list) > 0:
        steps_completed.append(4)
    if len(task_list) > 0:
        steps_completed.append(5)

    # Calculate current step
    current_step = max(steps_completed) + 1 if len(steps_completed) < 5 else 5

    # Calculate compliance score
    completed_docs = [d for d in document_list if d.status == DocumentStatus.APPROVED]
    total_docs = len(document_list) or 1
    compliance_score = (len(completed_docs) / total_docs) * 100

    return OnboardingStatus(
        company_id=str(company.id),
        current_step=current_step,
        steps_completed=steps_completed,
        company_name=company.full_name,
        inn=company.inn,
        responsible_count=len(responsible_list),
        ispdn_count=len(ispdn_list),
        document_count=len(document_list),
        task_count=len(task_list),
        compliance_score=round(compliance_score, 1),
    )


@router.post("/complete", response_model=OnboardingResult)
async def complete_onboarding(
    data: FullOnboardingRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Complete full onboarding in one request.
    Creates company, responsible persons, ISPDN systems, documents, and tasks.
    """
    # Step 1: Create Company
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
            detail=f"Company with INN {data.inn} not found",
        )

    company = RuCompanyProfile(
        tenant_id=current_user.tenant_id,
        inn=egrul_data.get("inn", data.inn),
        kpp=egrul_data.get("kpp"),
        ogrn=egrul_data.get("ogrn"),
        full_name=egrul_data.get("full_name", f"Company {data.inn}"),
        short_name=egrul_data.get("short_name"),
        legal_form=egrul_data.get("legal_form"),
        legal_address=egrul_data.get("legal_address"),
        director_name=egrul_data.get("director_name"),
        director_position=egrul_data.get("director_position"),
        egrul_data=egrul_data,
        is_pdn_operator=True,
    )
    db.add(company)
    await db.flush()

    # Step 2: Create Responsible Persons
    responsible_count = 0

    if data.pdn_responsible:
        person = RuResponsiblePerson(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            role=data.pdn_responsible.role,
            role_name_ru=ROLE_NAMES_RU.get(data.pdn_responsible.role, str(data.pdn_responsible.role)),
            full_name=data.pdn_responsible.full_name,
            email=data.pdn_responsible.email,
            position=data.pdn_responsible.position,
            phone=data.pdn_responsible.phone,
        )
        db.add(person)
        responsible_count += 1

    if data.security_admin:
        person = RuResponsiblePerson(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            role=data.security_admin.role,
            role_name_ru=ROLE_NAMES_RU.get(data.security_admin.role, str(data.security_admin.role)),
            full_name=data.security_admin.full_name,
            email=data.security_admin.email,
            position=data.security_admin.position,
            phone=data.security_admin.phone,
        )
        db.add(person)
        responsible_count += 1

    # Step 3: Create ISPDN Systems
    protection_levels = {}
    for ispdn_input in data.ispdn_systems:
        # Calculate protection level
        subject_count_int = (
            100000 if ispdn_input.subject_count == ">100000"
            else 10000 if ispdn_input.subject_count == "<100000"
            else 500
        )
        protection_level = ProtectionLevelCalculator.calculate(
            category=ispdn_input.pdn_category,
            subject_count=subject_count_int,
            threat_type=ispdn_input.threat_type,
        )

        ispdn = RuISPDN(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            name=ispdn_input.name,
            description=ispdn_input.description,
            pdn_category=ispdn_input.pdn_category,
            subject_count=ispdn_input.subject_count,
            threat_type=ispdn_input.threat_type,
            protection_level=protection_level,
            processing_purposes=ispdn_input.processing_purposes,
            subject_categories=ispdn_input.subject_categories,
            pdn_types=ispdn_input.pdn_types,
            processes_special_pdn=ispdn_input.pdn_category == ISPDNCategory.SPECIAL,
            processes_biometric=ispdn_input.pdn_category == ISPDNCategory.BIOMETRIC,
        )
        db.add(ispdn)
        protection_levels[ispdn_input.name] = protection_level.value

    # Step 4: Generate Documents
    documents_count = 0
    if data.generate_fz152_package:
        templates = get_mandatory_templates()
        for template_data in templates:
            # Populate template with company data
            content = template_data["template_content"]
            content = content.replace("{{company_name}}", company.full_name or "")
            content = content.replace("{{company_short_name}}", company.short_name or company.full_name or "")
            content = content.replace("{{inn}}", company.inn or "")
            content = content.replace("{{kpp}}", company.kpp or "")
            content = content.replace("{{ogrn}}", company.ogrn or "")
            content = content.replace("{{legal_address}}", company.legal_address or "")
            content = content.replace("{{actual_address}}", company.legal_address or "")
            content = content.replace("{{director_name}}", company.director_name or "")
            content = content.replace("{{director_position}}", company.director_position or "Генеральный директор")
            content = content.replace("{{current_year}}", str(date.today().year))
            content = content.replace("{{current_date}}", date.today().strftime("%d.%m.%Y"))
            content = content.replace("{{phone}}", company.phone or "")
            content = content.replace("{{email}}", company.email or "")
            content = content.replace("{{website}}", company.website or "")

            document = RuComplianceDocument(
                tenant_id=current_user.tenant_id,
                company_id=company.id,
                document_code=f"{template_data['template_code']}-{company.inn}",
                title=template_data["title"],
                document_type=template_data["document_type"],
                framework=RuFrameworkType.FZ_152,
                requirement_ref=template_data.get("requirement_ref"),
                content=content,
                status=DocumentStatus.DRAFT,
                priority=TaskPriority.HIGH if template_data.get("is_mandatory") else TaskPriority.MEDIUM,
                due_date=date.today() + timedelta(days=data.task_deadline_days),
            )
            db.add(document)
            documents_count += 1

    # Step 5: Create Tasks
    tasks_count = 0
    if data.assign_tasks and documents_count > 0:
        # Create main onboarding task
        main_task = RuComplianceTask(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            title="Завершить подготовку пакета документов 152-ФЗ",
            description=f"Подготовить и утвердить {documents_count} документов для соответствия 152-ФЗ",
            task_type="DOCUMENT",
            framework=RuFrameworkType.FZ_152,
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.HIGH,
            due_date=date.today() + timedelta(days=data.task_deadline_days),
        )
        db.add(main_task)
        tasks_count += 1

        # Create task for Roskomnadzor notification
        notification_task = RuComplianceTask(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            title="Подать уведомление в Роскомнадзор",
            description="Подготовить и подать уведомление об обработке персональных данных в территориальное управление Роскомнадзора",
            task_type="NOTIFICATION",
            framework=RuFrameworkType.FZ_152,
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.HIGH,
            due_date=date.today() + timedelta(days=data.task_deadline_days + 15),
        )
        db.add(notification_task)
        tasks_count += 1

        # Create task for employee training
        training_task = RuComplianceTask(
            tenant_id=current_user.tenant_id,
            company_id=company.id,
            title="Провести обучение сотрудников",
            description="Провести обучение сотрудников, имеющих доступ к персональным данным, требованиям 152-ФЗ",
            task_type="TRAINING",
            framework=RuFrameworkType.FZ_152,
            status=TaskStatus.NOT_STARTED,
            priority=TaskPriority.MEDIUM,
            due_date=date.today() + timedelta(days=data.task_deadline_days + 30),
        )
        db.add(training_task)
        tasks_count += 1

    await db.commit()

    # Generate next steps
    next_steps = []
    if documents_count > 0:
        next_steps.append("Заполнить и подписать сгенерированные документы")
    if not data.pdn_responsible:
        next_steps.append("Назначить ответственного за организацию обработки ПДн")
    if len(data.ispdn_systems) == 0:
        next_steps.append("Зарегистрировать информационные системы персональных данных (ИСПДн)")
    next_steps.append("Подать уведомление в Роскомнадзор")
    next_steps.append("Провести обучение сотрудников")
    next_steps.append("Внедрить технические меры защиты")

    return OnboardingResult(
        success=True,
        company_id=str(company.id),
        company_name=company.full_name,
        responsible_persons_created=responsible_count,
        ispdn_systems_created=len(data.ispdn_systems),
        documents_generated=documents_count,
        tasks_created=tasks_count,
        protection_levels=protection_levels,
        next_steps=next_steps,
    )


@router.post("/generate-documents/{company_id}")
async def generate_document_package(
    company_id: UUID,
    framework: str = "152-ФЗ",
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Generate full document package for a framework."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    templates = get_mandatory_templates()
    documents_created = []

    for template_data in templates:
        # Check if document already exists
        existing = await db.execute(
            select(RuComplianceDocument).where(
                RuComplianceDocument.company_id == company_id,
                RuComplianceDocument.document_code == f"{template_data['template_code']}-{company.inn}",
            )
        )
        if existing.scalar_one_or_none():
            continue

        # Populate template
        content = template_data["template_content"]
        content = content.replace("{{company_name}}", company.full_name or "")
        content = content.replace("{{company_short_name}}", company.short_name or company.full_name or "")
        content = content.replace("{{inn}}", company.inn or "")
        content = content.replace("{{kpp}}", company.kpp or "")
        content = content.replace("{{ogrn}}", company.ogrn or "")
        content = content.replace("{{legal_address}}", company.legal_address or "")
        content = content.replace("{{director_name}}", company.director_name or "")
        content = content.replace("{{director_position}}", company.director_position or "Генеральный директор")
        content = content.replace("{{current_year}}", str(date.today().year))
        content = content.replace("{{phone}}", company.phone or "")
        content = content.replace("{{email}}", company.email or "")

        document = RuComplianceDocument(
            tenant_id=current_user.tenant_id,
            company_id=company_id,
            document_code=f"{template_data['template_code']}-{company.inn}",
            title=template_data["title"],
            document_type=template_data["document_type"],
            framework=RuFrameworkType.FZ_152,
            requirement_ref=template_data.get("requirement_ref"),
            content=content,
            status=DocumentStatus.DRAFT,
            priority=TaskPriority.HIGH if template_data.get("is_mandatory") else TaskPriority.MEDIUM,
            due_date=date.today() + timedelta(days=30),
        )
        db.add(document)
        documents_created.append(template_data["title"])

    await db.commit()

    return {
        "success": True,
        "documents_created": len(documents_created),
        "document_titles": documents_created,
    }


@router.get("/required-roles")
async def get_required_roles(
    current_user: User = Depends(get_current_user),
):
    """Get list of required responsible person roles."""
    roles = [
        {
            "role": ResponsibleRole.PDN_RESPONSIBLE,
            "name_ru": ROLE_NAMES_RU[ResponsibleRole.PDN_RESPONSIBLE],
            "description": "Обязателен для всех операторов ПДн (ст. 22.1 152-ФЗ)",
            "is_mandatory": True,
            "framework": "152-ФЗ",
        },
        {
            "role": ResponsibleRole.SECURITY_ADMIN,
            "name_ru": ROLE_NAMES_RU[ResponsibleRole.SECURITY_ADMIN],
            "description": "Администратор безопасности ИСПДн",
            "is_mandatory": True,
            "framework": "152-ФЗ",
        },
        {
            "role": ResponsibleRole.CEO,
            "name_ru": ROLE_NAMES_RU[ResponsibleRole.CEO],
            "description": "Руководитель организации - оператора ПДн",
            "is_mandatory": True,
            "framework": "152-ФЗ",
        },
        {
            "role": ResponsibleRole.KII_RESPONSIBLE,
            "name_ru": ROLE_NAMES_RU[ResponsibleRole.KII_RESPONSIBLE],
            "description": "Обязателен для субъектов КИИ (187-ФЗ)",
            "is_mandatory": False,
            "framework": "187-ФЗ",
        },
        {
            "role": ResponsibleRole.GOSSOPKA_CONTACT,
            "name_ru": ROLE_NAMES_RU[ResponsibleRole.GOSSOPKA_CONTACT],
            "description": "Контактное лицо для взаимодействия с ГосСОПКА",
            "is_mandatory": False,
            "framework": "187-ФЗ",
        },
    ]
    return roles


@router.get("/document-packages")
async def get_available_document_packages(
    current_user: User = Depends(get_current_user),
):
    """Get available document packages."""
    templates = get_all_fz152_templates()

    # Group by category
    categories = {}
    for t in templates:
        cat = t.get("category", "other")
        if cat not in categories:
            categories[cat] = []
        categories[cat].append({
            "code": t["template_code"],
            "title": t["title"],
            "title_en": t.get("title_en"),
            "document_type": t["document_type"],
            "is_mandatory": t.get("is_mandatory", False),
            "requirement_ref": t.get("requirement_ref"),
        })

    return {
        "framework": "152-ФЗ",
        "total_documents": len(templates),
        "mandatory_documents": len([t for t in templates if t.get("is_mandatory")]),
        "categories": categories,
    }


@router.get("/compliance-checklist/{company_id}")
async def get_compliance_checklist(
    company_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Get compliance checklist for a company."""
    company = await db.get(RuCompanyProfile, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")

    # Get counts
    responsible_result = await db.execute(
        select(RuResponsiblePerson).where(
            RuResponsiblePerson.company_id == company_id,
            RuResponsiblePerson.is_active == True,
        )
    )
    responsible_list = list(responsible_result.scalars().all())

    ispdn_result = await db.execute(
        select(RuISPDN).where(RuISPDN.company_id == company_id)
    )
    ispdn_list = list(ispdn_result.scalars().all())

    doc_result = await db.execute(
        select(RuComplianceDocument).where(
            RuComplianceDocument.company_id == company_id
        )
    )
    doc_list = list(doc_result.scalars().all())

    # Build checklist
    checklist = [
        {
            "id": "company_registered",
            "title": "Организация зарегистрирована",
            "description": "Данные организации загружены из ЕГРЮЛ",
            "completed": True,
            "framework": "152-ФЗ",
        },
        {
            "id": "pdn_responsible",
            "title": "Назначен ответственный за обработку ПДн",
            "description": "Статья 22.1 152-ФЗ",
            "completed": any(p.role == ResponsibleRole.PDN_RESPONSIBLE for p in responsible_list),
            "framework": "152-ФЗ",
        },
        {
            "id": "security_admin",
            "title": "Назначен администратор безопасности",
            "description": "Приказ ФСТЭК № 21",
            "completed": any(p.role == ResponsibleRole.SECURITY_ADMIN for p in responsible_list),
            "framework": "152-ФЗ",
        },
        {
            "id": "ispdn_registered",
            "title": "Зарегистрированы ИСПДн",
            "description": "Постановление Правительства № 1119",
            "completed": len(ispdn_list) > 0,
            "framework": "152-ФЗ",
        },
        {
            "id": "ispdn_classified",
            "title": "Проведена классификация ИСПДн",
            "description": "Определены уровни защищенности",
            "completed": all(i.protection_level is not None for i in ispdn_list) if ispdn_list else False,
            "framework": "152-ФЗ",
        },
        {
            "id": "policy_approved",
            "title": "Утверждена Политика обработки ПДн",
            "description": "Статья 18.1 152-ФЗ",
            "completed": any(
                d.document_code.startswith("FZ152-POL-001") and d.status == DocumentStatus.APPROVED
                for d in doc_list
            ),
            "framework": "152-ФЗ",
        },
        {
            "id": "documents_prepared",
            "title": "Подготовлен пакет документов",
            "description": "Все обязательные документы",
            "completed": len([d for d in doc_list if d.status == DocumentStatus.APPROVED]) >= 10,
            "framework": "152-ФЗ",
        },
        {
            "id": "roskomnadzor_notified",
            "title": "Подано уведомление в Роскомнадзор",
            "description": "Статья 22 152-ФЗ",
            "completed": company.roskomnadzor_reg_number is not None,
            "framework": "152-ФЗ",
        },
        {
            "id": "employees_trained",
            "title": "Проведено обучение сотрудников",
            "description": "Статья 18.1 152-ФЗ",
            "completed": all(p.training_completed for p in responsible_list) if responsible_list else False,
            "framework": "152-ФЗ",
        },
        {
            "id": "technical_measures",
            "title": "Внедрены технические меры защиты",
            "description": "Приказ ФСТЭК № 21",
            "completed": False,  # Would check for evidence
            "framework": "152-ФЗ",
        },
    ]

    completed_count = sum(1 for item in checklist if item["completed"])
    total_count = len(checklist)

    return {
        "company_id": str(company_id),
        "company_name": company.full_name,
        "checklist": checklist,
        "completed_count": completed_count,
        "total_count": total_count,
        "compliance_percentage": round((completed_count / total_count) * 100, 1),
    }
