"""AI-powered document generation endpoints."""

from typing import Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from app.api.v1.deps import DB, CurrentTenant, CurrentUser, RequireWriter
from app.services.ai_document_service import ai_document_service

router = APIRouter()


class DocumentGenerationRequest(BaseModel):
    """Request to generate a compliance document using AI."""

    document_type: str = Field(
        ...,
        description="Type of document: policy, consent, ispdn, notification, dpo_order, kii_act, security_policy",
    )
    company_name: str = Field(..., min_length=1, description="Company name in Russian")
    company_inn: str = Field(..., min_length=10, max_length=12, description="Company INN")
    framework: str = Field(
        default="152-FZ",
        description="Compliance framework: 152-FZ, 187-FZ, GOST-57580, FSTEC",
    )
    additional_context: dict[str, Any] = Field(
        default_factory=dict,
        description="Additional context for document generation (e.g., director name, DPO name)",
    )


class DocumentGenerationResponse(BaseModel):
    """Response with generated document content."""

    content: str
    document_type: str
    framework: str
    company_name: str
    generated_by: str


class AIDocumentStatus(BaseModel):
    """AI document service status."""

    ai_provider: str
    is_configured: bool
    huggingface_model: str | None
    ollama_url: str | None


@router.post("/generate", response_model=DocumentGenerationResponse)
async def generate_document(
    request: DocumentGenerationRequest,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
) -> DocumentGenerationResponse:
    """
    Generate a compliance document using AI.

    Supported document types:
    - policy: Personal Data Processing Policy (Политика обработки ПДн)
    - consent: Consent Form (Согласие на обработку ПДн)
    - ispdn: ISPDN Description (Описание ИСПДн)
    - notification: Roskomnadzor Notification (Уведомление в РКН)
    - dpo_order: DPO Appointment Order (Приказ о назначении ответственного)
    - kii_act: KII Categorization Act (Акт категорирования КИИ)
    - security_policy: Information Security Policy (Политика ИБ)

    Supported frameworks:
    - 152-FZ: Personal Data Protection
    - 187-FZ: Critical Information Infrastructure
    - GOST-57580: Financial Security
    - FSTEC: Data Protection Requirements
    """
    try:
        result = await ai_document_service.generate_document(
            document_type=request.document_type,
            company_name=request.company_name,
            company_inn=request.company_inn,
            framework=request.framework,
            additional_context=request.additional_context,
        )

        return DocumentGenerationResponse(
            content=result["content"],
            document_type=result["document_type"],
            framework=result["framework"],
            company_name=result["company_name"],
            generated_by=result["generated_by"],
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Document generation failed: {e}")


@router.get("/status", response_model=AIDocumentStatus)
async def get_ai_status(
    current_user: CurrentUser,
) -> AIDocumentStatus:
    """Get the status of the AI document generation service."""
    return AIDocumentStatus(
        ai_provider=ai_document_service.ai_provider,
        is_configured=bool(ai_document_service.hf_token or ai_document_service.ollama_url),
        huggingface_model=ai_document_service.hf_model if ai_document_service.hf_token else None,
        ollama_url=ai_document_service.ollama_url if ai_document_service.ai_provider == "ollama" else None,
    )


@router.get("/document-types")
async def list_document_types(
    current_user: CurrentUser,
) -> dict[str, Any]:
    """List available document types for AI generation."""
    return {
        "document_types": [
            {
                "id": "policy",
                "name": "Политика обработки ПДн",
                "name_en": "Personal Data Processing Policy",
                "framework": "152-FZ",
                "description": "Main policy document for personal data processing",
            },
            {
                "id": "consent",
                "name": "Согласие на обработку ПДн",
                "name_en": "Consent Form",
                "framework": "152-FZ",
                "description": "Template for subject consent",
            },
            {
                "id": "ispdn",
                "name": "Описание ИСПДн",
                "name_en": "ISPDN Description",
                "framework": "152-FZ",
                "description": "Information system description",
            },
            {
                "id": "notification",
                "name": "Уведомление в РКН",
                "name_en": "Roskomnadzor Notification",
                "framework": "152-FZ",
                "description": "Notification to data protection authority",
            },
            {
                "id": "dpo_order",
                "name": "Приказ о назначении ответственного",
                "name_en": "DPO Appointment Order",
                "framework": "152-FZ",
                "description": "Order appointing data protection officer",
            },
            {
                "id": "kii_act",
                "name": "Акт категорирования КИИ",
                "name_en": "KII Categorization Act",
                "framework": "187-FZ",
                "description": "Critical infrastructure categorization",
            },
            {
                "id": "security_policy",
                "name": "Политика ИБ",
                "name_en": "Information Security Policy",
                "framework": "GOST-57580",
                "description": "Bank information security policy",
            },
        ],
        "frameworks": [
            {"id": "152-FZ", "name": "152-ФЗ О персональных данных"},
            {"id": "187-FZ", "name": "187-ФЗ О безопасности КИИ"},
            {"id": "GOST-57580", "name": "ГОСТ Р 57580 Финансовая безопасность"},
            {"id": "FSTEC", "name": "Приказы ФСТЭК"},
        ],
    }
