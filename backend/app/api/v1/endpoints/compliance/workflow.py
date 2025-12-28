"""
Complete Compliance Workflow API
Handles the entire lifecycle from registration to full compliance:
1. Company Registration -> EGRUL lookup
2. Responsible Persons -> Appointment orders
3. ISPDN Registration -> Classification, threat model
4. Document Generation -> All required documents
5. Document Approval -> Workflow with signatures
6. Employee Consents -> Collection and tracking
7. Training -> Schedule and track completion
8. Roskomnadzor -> Notification submission
9. Audits -> Schedule and conduct
10. Monitoring -> Continuous compliance
"""

from datetime import datetime, timedelta
from enum import Enum
from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

router = APIRouter()


# ============ ENUMS ============
class WorkflowStage(str, Enum):
    REGISTRATION = "registration"
    RESPONSIBLE_PERSONS = "responsible_persons"
    ISPDN_CLASSIFICATION = "ispdn_classification"
    DOCUMENT_GENERATION = "document_generation"
    DOCUMENT_APPROVAL = "document_approval"
    EMPLOYEE_CONSENTS = "employee_consents"
    TRAINING = "training"
    ROSKOMNADZOR = "roskomnadzor"
    AUDIT = "audit"
    MONITORING = "monitoring"


class ApprovalStatus(str, Enum):
    PENDING = "pending"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    REVISION_REQUIRED = "revision_required"


class ConsentStatus(str, Enum):
    NOT_SENT = "not_sent"
    SENT = "sent"
    SIGNED = "signed"
    REFUSED = "refused"
    EXPIRED = "expired"


class TrainingStatus(str, Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


class RKNSubmissionStatus(str, Enum):
    DRAFT = "draft"
    READY = "ready"
    SUBMITTED = "submitted"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    AMENDMENT_REQUIRED = "amendment_required"


# ============ SCHEMAS ============

# Workflow Progress
class WorkflowProgressResponse(BaseModel):
    company_id: str
    company_name: str
    current_stage: WorkflowStage
    overall_progress: float  # 0-100
    stages: list[dict[str, Any]]
    next_actions: list[dict[str, str]]
    blocking_issues: list[str]
    estimated_completion: str | None


# Document Approval
class ApprovalRequest(BaseModel):
    document_id: str
    approver_id: str
    action: ApprovalStatus
    comment: str = ""
    signature_data: str | None = None  # Base64 encoded signature


class ApprovalWorkflow(BaseModel):
    document_id: str
    document_title: str
    current_status: ApprovalStatus
    current_approver: str | None
    approval_chain: list[dict[str, Any]]
    history: list[dict[str, Any]]
    due_date: str | None


# Employee Consents
class EmployeeConsentRequest(BaseModel):
    employee_name: str
    employee_email: str
    employee_position: str
    consent_types: list[str]  # ["pd_processing", "pd_transfer", "biometric"]
    delivery_method: str = "email"  # email, paper, electronic


class ConsentRecord(BaseModel):
    id: str
    employee_name: str
    employee_email: str
    consent_type: str
    status: ConsentStatus
    sent_at: str | None
    signed_at: str | None
    expires_at: str | None
    document_url: str | None


# Training
class TrainingProgramRequest(BaseModel):
    title: str
    description: str
    training_type: str  # online, offline, mixed
    duration_hours: int
    target_roles: list[str]
    is_mandatory: bool = True
    deadline_days: int = 30


class TrainingRecord(BaseModel):
    id: str
    employee_id: str
    employee_name: str
    program_id: str
    program_title: str
    status: TrainingStatus
    started_at: str | None
    completed_at: str | None
    score: int | None
    certificate_url: str | None


# Roskomnadzor
class RKNNotificationData(BaseModel):
    company_name: str
    inn: str
    ogrn: str
    legal_address: str
    actual_address: str
    responsible_name: str
    responsible_position: str
    responsible_phone: str
    responsible_email: str
    processing_purposes: list[str]
    data_categories: list[str]
    subject_categories: list[str]
    legal_bases: list[str]
    data_actions: list[str]
    storage_location: str
    cross_border_transfer: bool = False
    transfer_countries: list[str] = []


class RKNNotificationResponse(BaseModel):
    id: str
    status: RKNSubmissionStatus
    registration_number: str | None
    submitted_at: str | None
    accepted_at: str | None
    rejection_reason: str | None
    document_url: str


# Audit
class AuditScheduleRequest(BaseModel):
    audit_type: str  # internal, external, certification
    framework: str  # fz152, fz187, gost57580
    scheduled_date: str
    auditor_name: str | None
    auditor_company: str | None
    scope: list[str]


class AuditRecord(BaseModel):
    id: str
    audit_type: str
    framework: str
    status: str
    scheduled_date: str
    started_at: str | None
    completed_at: str | None
    findings_count: int
    score: float | None
    report_url: str | None


# Calendar
class CalendarEvent(BaseModel):
    id: str
    title: str
    event_type: str  # deadline, audit, training, review, submission
    date: str
    priority: str
    related_document: str | None
    assigned_to: str | None
    status: str


# ============ WORKFLOW PROGRESS ============

@router.get("/workflow/progress/{company_id}", response_model=WorkflowProgressResponse)
async def get_workflow_progress(company_id: str):
    """Get comprehensive workflow progress for a company."""
    # Mock implementation - in production would query database
    stages = [
        {
            "stage": WorkflowStage.REGISTRATION,
            "title": "Регистрация организации",
            "status": "completed",
            "progress": 100,
            "completed_at": "2024-01-15T10:00:00Z",
        },
        {
            "stage": WorkflowStage.RESPONSIBLE_PERSONS,
            "title": "Назначение ответственных лиц",
            "status": "completed",
            "progress": 100,
            "completed_at": "2024-01-16T14:00:00Z",
        },
        {
            "stage": WorkflowStage.ISPDN_CLASSIFICATION,
            "title": "Классификация ИСПДн",
            "status": "completed",
            "progress": 100,
            "completed_at": "2024-01-17T11:00:00Z",
        },
        {
            "stage": WorkflowStage.DOCUMENT_GENERATION,
            "title": "Генерация документов",
            "status": "completed",
            "progress": 100,
            "completed_at": "2024-01-18T09:00:00Z",
        },
        {
            "stage": WorkflowStage.DOCUMENT_APPROVAL,
            "title": "Утверждение документов",
            "status": "in_progress",
            "progress": 75,
            "pending_count": 5,
            "approved_count": 15,
        },
        {
            "stage": WorkflowStage.EMPLOYEE_CONSENTS,
            "title": "Сбор согласий работников",
            "status": "in_progress",
            "progress": 60,
            "total": 150,
            "collected": 90,
        },
        {
            "stage": WorkflowStage.TRAINING,
            "title": "Обучение персонала",
            "status": "in_progress",
            "progress": 45,
            "total": 150,
            "completed": 68,
        },
        {
            "stage": WorkflowStage.ROSKOMNADZOR,
            "title": "Уведомление в Роскомнадзор",
            "status": "pending",
            "progress": 0,
            "blocked_by": "Ожидает утверждения документов",
        },
        {
            "stage": WorkflowStage.AUDIT,
            "title": "Внутренний аудит",
            "status": "pending",
            "progress": 0,
            "scheduled_for": "2024-03-01T00:00:00Z",
        },
        {
            "stage": WorkflowStage.MONITORING,
            "title": "Постоянный мониторинг",
            "status": "pending",
            "progress": 0,
        },
    ]

    # Calculate overall progress
    total_progress = sum(s["progress"] for s in stages) / len(stages)

    # Determine current stage
    current_stage = WorkflowStage.DOCUMENT_APPROVAL
    for stage in stages:
        if stage["status"] == "in_progress":
            current_stage = stage["stage"]
            break

    next_actions = [
        {"action": "Утвердить 5 документов", "priority": "high", "url": "/documents?status=pending"},
        {"action": "Собрать 60 согласий", "priority": "high", "url": "/consents"},
        {"action": "Завершить обучение 82 сотрудников", "priority": "medium", "url": "/training"},
        {"action": "Подготовить уведомление в РКН", "priority": "low", "url": "/roskomnadzor"},
    ]

    blocking_issues = [
        "5 документов ожидают утверждения руководителя",
        "Не все сотрудники прошли обучение",
    ]

    return WorkflowProgressResponse(
        company_id=company_id,
        company_name="ООО «Демо Компания»",
        current_stage=current_stage,
        overall_progress=total_progress,
        stages=stages,
        next_actions=next_actions,
        blocking_issues=blocking_issues,
        estimated_completion="2024-03-15",
    )


# ============ DOCUMENT APPROVAL ============

@router.get("/approval/queue", response_model=list[ApprovalWorkflow])
async def get_approval_queue(
    status: ApprovalStatus | None = None,
    approver_id: str | None = None,
):
    """Get documents pending approval."""
    documents = [
        ApprovalWorkflow(
            document_id="doc-1",
            document_title="Политика обработки персональных данных",
            current_status=ApprovalStatus.PENDING,
            current_approver="Генеральный директор",
            approval_chain=[
                {"role": "Ответственный за ПДн", "status": "approved", "date": "2024-01-16"},
                {"role": "Юрист", "status": "approved", "date": "2024-01-17"},
                {"role": "Генеральный директор", "status": "pending", "date": None},
            ],
            history=[
                {"action": "created", "user": "Система", "date": "2024-01-15T10:00:00Z"},
                {"action": "approved", "user": "Петров П.П.", "date": "2024-01-16T14:00:00Z"},
                {"action": "approved", "user": "Сидоров С.С.", "date": "2024-01-17T11:00:00Z"},
            ],
            due_date="2024-01-25",
        ),
        ApprovalWorkflow(
            document_id="doc-2",
            document_title="Приказ о назначении ответственного за ПДн",
            current_status=ApprovalStatus.PENDING,
            current_approver="Генеральный директор",
            approval_chain=[
                {"role": "Генеральный директор", "status": "pending", "date": None},
            ],
            history=[
                {"action": "created", "user": "Система", "date": "2024-01-15T10:00:00Z"},
            ],
            due_date="2024-01-20",
        ),
    ]
    return documents


@router.post("/approval/action")
async def process_approval(request: ApprovalRequest):
    """Process document approval action (approve/reject/request revision)."""
    return {
        "success": True,
        "document_id": request.document_id,
        "new_status": request.action,
        "message": f"Документ {request.action.value}",
        "next_approver": None if request.action == ApprovalStatus.APPROVED else "Автор документа",
    }


@router.post("/approval/bulk")
async def bulk_approve(document_ids: list[str], approver_id: str, action: ApprovalStatus):
    """Bulk approve/reject multiple documents."""
    return {
        "success": True,
        "processed": len(document_ids),
        "new_status": action,
    }


# ============ EMPLOYEE CONSENTS ============

@router.get("/consents/stats/{company_id}")
async def get_consent_stats(company_id: str):
    """Get consent collection statistics."""
    return {
        "company_id": company_id,
        "total_employees": 150,
        "consents_required": 150,
        "consents_collected": 90,
        "consents_pending": 45,
        "consents_refused": 5,
        "consents_expired": 10,
        "collection_rate": 60.0,
        "by_type": {
            "pd_processing": {"collected": 95, "pending": 40, "refused": 5, "expired": 10},
            "pd_transfer": {"collected": 85, "pending": 50, "refused": 5, "expired": 10},
            "photo_video": {"collected": 70, "pending": 60, "refused": 10, "expired": 10},
        },
    }


@router.get("/consents/list", response_model=list[ConsentRecord])
async def get_consents(
    company_id: str,
    status: ConsentStatus | None = None,
    consent_type: str | None = None,
    skip: int = 0,
    limit: int = 50,
):
    """Get list of employee consents."""
    return [
        ConsentRecord(
            id="consent-1",
            employee_name="Иванов Иван Иванович",
            employee_email="ivanov@company.ru",
            consent_type="pd_processing",
            status=ConsentStatus.SIGNED,
            sent_at="2024-01-15T10:00:00Z",
            signed_at="2024-01-16T09:30:00Z",
            expires_at="2029-01-16T00:00:00Z",
            document_url="/documents/consent-1.pdf",
        ),
        ConsentRecord(
            id="consent-2",
            employee_name="Петров Пётр Петрович",
            employee_email="petrov@company.ru",
            consent_type="pd_processing",
            status=ConsentStatus.SENT,
            sent_at="2024-01-15T10:00:00Z",
            signed_at=None,
            expires_at=None,
            document_url=None,
        ),
    ]


@router.post("/consents/send")
async def send_consent_requests(requests: list[EmployeeConsentRequest]):
    """Send consent requests to employees."""
    return {
        "success": True,
        "sent": len(requests),
        "message": f"Отправлено {len(requests)} запросов на согласие",
    }


@router.post("/consents/bulk-send/{company_id}")
async def bulk_send_consents(company_id: str, consent_types: list[str], filter_by: str | None = None):
    """Send consent requests to all employees who haven't signed yet."""
    return {
        "success": True,
        "sent": 45,
        "message": "Отправлено 45 запросов на согласие",
    }


@router.post("/consents/record-signature/{consent_id}")
async def record_consent_signature(
    consent_id: str,
    signature_data: str,
    signed_via: str = "electronic",  # electronic, paper
):
    """Record consent signature (for paper consents or manual recording)."""
    return {
        "success": True,
        "consent_id": consent_id,
        "status": ConsentStatus.SIGNED,
        "signed_at": datetime.now().isoformat(),
    }


# ============ TRAINING ============

@router.get("/training/programs")
async def get_training_programs(framework: str | None = None):
    """Get available training programs."""
    return [
        {
            "id": "prog-1",
            "title": "Основы защиты персональных данных",
            "title_en": "Personal Data Protection Fundamentals",
            "description": "Базовый курс по 152-ФЗ для всех сотрудников",
            "framework": "fz152",
            "duration_hours": 4,
            "is_mandatory": True,
            "modules": [
                "Законодательство о ПДн",
                "Права субъектов ПДн",
                "Обязанности оператора",
                "Практические навыки",
            ],
        },
        {
            "id": "prog-2",
            "title": "Безопасность КИИ для администраторов",
            "title_en": "KII Security for Administrators",
            "description": "Углублённый курс по 187-ФЗ для ИТ-специалистов",
            "framework": "fz187",
            "duration_hours": 8,
            "is_mandatory": True,
            "modules": [
                "Требования 187-ФЗ",
                "Категорирование объектов КИИ",
                "Система безопасности",
                "Реагирование на инциденты",
            ],
        },
    ]


@router.get("/training/stats/{company_id}")
async def get_training_stats(company_id: str):
    """Get training completion statistics."""
    return {
        "company_id": company_id,
        "total_employees": 150,
        "training_required": 150,
        "training_completed": 68,
        "training_in_progress": 32,
        "training_not_started": 50,
        "completion_rate": 45.3,
        "by_program": {
            "prog-1": {"required": 150, "completed": 68, "in_progress": 32, "not_started": 50},
            "prog-2": {"required": 15, "completed": 10, "in_progress": 3, "not_started": 2},
        },
    }


@router.get("/training/records", response_model=list[TrainingRecord])
async def get_training_records(
    company_id: str,
    status: TrainingStatus | None = None,
    program_id: str | None = None,
    skip: int = 0,
    limit: int = 50,
):
    """Get training records for employees."""
    return [
        TrainingRecord(
            id="train-1",
            employee_id="emp-1",
            employee_name="Иванов Иван Иванович",
            program_id="prog-1",
            program_title="Основы защиты персональных данных",
            status=TrainingStatus.COMPLETED,
            started_at="2024-01-10T09:00:00Z",
            completed_at="2024-01-10T13:00:00Z",
            score=95,
            certificate_url="/certificates/train-1.pdf",
        ),
    ]


@router.post("/training/assign")
async def assign_training(
    company_id: str,
    program_id: str,
    employee_ids: list[str],
    deadline_date: str,
):
    """Assign training program to employees."""
    return {
        "success": True,
        "assigned": len(employee_ids),
        "program_id": program_id,
        "deadline": deadline_date,
    }


@router.post("/training/send-reminders/{company_id}")
async def send_training_reminders(company_id: str, program_id: str | None = None):
    """Send reminders to employees who haven't completed training."""
    return {
        "success": True,
        "reminders_sent": 50,
    }


# ============ ROSKOMNADZOR NOTIFICATION ============

@router.get("/roskomnadzor/status/{company_id}")
async def get_rkn_status(company_id: str):
    """Get Roskomnadzor notification status."""
    return {
        "company_id": company_id,
        "notification_required": True,
        "notification_status": RKNSubmissionStatus.DRAFT,
        "registration_number": None,
        "submitted_at": None,
        "last_updated": "2024-01-15T10:00:00Z",
        "blockers": [
            "Не утверждена Политика обработки ПДн",
            "Не назначен ответственный за ПДн",
        ],
        "checklist": {
            "policy_approved": False,
            "responsible_appointed": True,
            "ispdn_classified": True,
            "purposes_defined": True,
            "data_categories_defined": True,
        },
    }


@router.post("/roskomnadzor/prepare/{company_id}")
async def prepare_rkn_notification(company_id: str, data: RKNNotificationData):
    """Prepare Roskomnadzor notification form."""
    return {
        "success": True,
        "notification_id": "rkn-123",
        "status": RKNSubmissionStatus.READY,
        "preview_url": "/documents/rkn-notification-preview.pdf",
        "xml_url": "/documents/rkn-notification.xml",
    }


@router.get("/roskomnadzor/preview/{notification_id}")
async def preview_rkn_notification(notification_id: str):
    """Preview Roskomnadzor notification before submission."""
    return {
        "notification_id": notification_id,
        "preview_html": "<html>...</html>",  # Rendered notification form
        "validation_errors": [],
        "warnings": [],
    }


@router.post("/roskomnadzor/submit/{notification_id}")
async def submit_rkn_notification(notification_id: str, submission_method: str = "electronic"):
    """Submit notification to Roskomnadzor (generates final documents)."""
    # In production, this would generate the XML for electronic submission
    # or the printable PDF for paper submission
    return {
        "success": True,
        "notification_id": notification_id,
        "status": RKNSubmissionStatus.READY,  # Ready for manual submission
        "documents": {
            "xml": "/documents/rkn-notification.xml",
            "pdf": "/documents/rkn-notification.pdf",
            "cover_letter": "/documents/rkn-cover-letter.pdf",
        },
        "instructions": "Подайте уведомление через портал pd.rkn.gov.ru или направьте почтой",
        "portal_url": "https://pd.rkn.gov.ru/operators-registry/notification/",
    }


@router.post("/roskomnadzor/record-submission/{notification_id}")
async def record_rkn_submission(
    notification_id: str,
    registration_number: str,
    submission_date: str,
):
    """Record successful submission to Roskomnadzor."""
    return {
        "success": True,
        "notification_id": notification_id,
        "registration_number": registration_number,
        "status": RKNSubmissionStatus.SUBMITTED,
    }


# ============ AUDIT MANAGEMENT ============

@router.get("/audits/schedule/{company_id}")
async def get_audit_schedule(company_id: str, year: int | None = None):
    """Get audit schedule for a company."""
    return {
        "company_id": company_id,
        "year": year or datetime.now().year,
        "audits": [
            {
                "id": "audit-1",
                "title": "Внутренний аудит 152-ФЗ Q1",
                "audit_type": "internal",
                "framework": "fz152",
                "scheduled_date": "2024-03-15",
                "status": "scheduled",
            },
            {
                "id": "audit-2",
                "title": "Оценка соответствия ГОСТ 57580",
                "audit_type": "external",
                "framework": "gost57580",
                "scheduled_date": "2024-06-01",
                "status": "scheduled",
                "auditor_company": "ООО «Аудит ИБ»",
            },
        ],
    }


@router.post("/audits/schedule")
async def schedule_audit(request: AuditScheduleRequest):
    """Schedule a new audit."""
    return {
        "success": True,
        "audit_id": "audit-new",
        "scheduled_date": request.scheduled_date,
    }


@router.get("/audits/{audit_id}", response_model=AuditRecord)
async def get_audit(audit_id: str):
    """Get audit details."""
    return AuditRecord(
        id=audit_id,
        audit_type="internal",
        framework="fz152",
        status="completed",
        scheduled_date="2024-01-15",
        started_at="2024-01-15T09:00:00Z",
        completed_at="2024-01-15T17:00:00Z",
        findings_count=5,
        score=0.82,
        report_url="/documents/audit-report-1.pdf",
    )


@router.post("/audits/{audit_id}/findings")
async def add_audit_finding(
    audit_id: str,
    finding_type: str,  # nonconformity, observation, opportunity
    requirement_ref: str,
    description: str,
    severity: str,  # critical, major, minor
    recommendation: str,
):
    """Add finding to an audit."""
    return {
        "success": True,
        "finding_id": "finding-new",
        "audit_id": audit_id,
    }


# ============ COMPLIANCE CALENDAR ============

@router.get("/calendar/{company_id}")
async def get_compliance_calendar(
    company_id: str,
    start_date: str | None = None,
    end_date: str | None = None,
):
    """Get compliance calendar events."""
    events = [
        CalendarEvent(
            id="evt-1",
            title="Срок утверждения Политики ПДн",
            event_type="deadline",
            date="2024-01-25",
            priority="high",
            related_document="doc-1",
            assigned_to="Генеральный директор",
            status="pending",
        ),
        CalendarEvent(
            id="evt-2",
            title="Внутренний аудит 152-ФЗ",
            event_type="audit",
            date="2024-03-15",
            priority="high",
            related_document=None,
            assigned_to="Служба ИБ",
            status="scheduled",
        ),
        CalendarEvent(
            id="evt-3",
            title="Пересмотр модели угроз",
            event_type="review",
            date="2024-06-01",
            priority="medium",
            related_document="doc-threat-model",
            assigned_to="Администратор безопасности",
            status="scheduled",
        ),
        CalendarEvent(
            id="evt-4",
            title="Обучение сотрудников (дедлайн)",
            event_type="training",
            date="2024-02-15",
            priority="high",
            related_document=None,
            assigned_to="Отдел кадров",
            status="in_progress",
        ),
    ]
    return events


@router.get("/calendar/upcoming/{company_id}")
async def get_upcoming_deadlines(company_id: str, days: int = 30):
    """Get upcoming deadlines within specified days."""
    return {
        "company_id": company_id,
        "period_days": days,
        "deadlines": [
            {
                "date": "2024-01-25",
                "items": [
                    {"title": "Утверждение Политики ПДн", "priority": "high", "type": "deadline"},
                ],
            },
            {
                "date": "2024-02-01",
                "items": [
                    {"title": "Срок подачи уведомления в РКН", "priority": "critical", "type": "deadline"},
                ],
            },
        ],
        "summary": {
            "critical": 1,
            "high": 3,
            "medium": 5,
            "low": 2,
        },
    }


# ============ COMPLETE COMPLIANCE CHECK ============

@router.get("/check/{company_id}")
async def check_compliance(company_id: str, framework: str | None = None):
    """Run comprehensive compliance check."""
    checks = [
        {
            "category": "Организационные меры",
            "items": [
                {"check": "Назначен ответственный за ПДн", "status": "pass", "evidence": "Приказ № 1"},
                {"check": "Утверждена Политика обработки ПДн", "status": "fail", "issue": "Ожидает подписи"},
                {"check": "Определены цели обработки", "status": "pass", "evidence": "Политика п.4"},
            ],
        },
        {
            "category": "ИСПДн",
            "items": [
                {"check": "Проведена классификация ИСПДн", "status": "pass", "evidence": "Акт классификации"},
                {"check": "Определён уровень защищённости", "status": "pass", "evidence": "УЗ-3"},
                {"check": "Разработана модель угроз", "status": "warning", "issue": "Требует актуализации"},
            ],
        },
        {
            "category": "Технические меры",
            "items": [
                {"check": "Антивирусная защита", "status": "pass", "evidence": "Kaspersky Endpoint"},
                {"check": "Межсетевое экранирование", "status": "pass", "evidence": "Cisco ASA"},
                {"check": "Шифрование каналов связи", "status": "pass", "evidence": "TLS 1.3"},
            ],
        },
        {
            "category": "Работа с персоналом",
            "items": [
                {"check": "Обучение сотрудников", "status": "warning", "issue": "45% не обучены"},
                {"check": "Согласия на обработку ПДн", "status": "warning", "issue": "60% собрано"},
                {"check": "Обязательства о неразглашении", "status": "pass", "evidence": "100% подписали"},
            ],
        },
    ]

    # Calculate scores
    total = sum(len(c["items"]) for c in checks)
    passed = sum(1 for c in checks for i in c["items"] if i["status"] == "pass")
    warnings = sum(1 for c in checks for i in c["items"] if i["status"] == "warning")
    failed = sum(1 for c in checks for i in c["items"] if i["status"] == "fail")

    return {
        "company_id": company_id,
        "framework": framework or "all",
        "check_date": datetime.now().isoformat(),
        "score": round((passed + warnings * 0.5) / total * 100, 1),
        "summary": {
            "total": total,
            "passed": passed,
            "warnings": warnings,
            "failed": failed,
        },
        "checks": checks,
        "recommendations": [
            {"priority": "high", "action": "Утвердить Политику обработки ПДн"},
            {"priority": "high", "action": "Завершить обучение оставшихся 55% сотрудников"},
            {"priority": "medium", "action": "Собрать согласия на обработку ПДн (40% осталось)"},
            {"priority": "low", "action": "Актуализировать модель угроз"},
        ],
    }
