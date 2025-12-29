"""AI-powered document generation service for Russian compliance."""

from typing import Optional
import httpx
from app.core.config import settings


class AIDocumentService:
    """Service for AI-assisted compliance document generation."""

    def __init__(self):
        self.hf_token = getattr(settings, "HUGGINGFACE_TOKEN", None)
        # Use our fine-tuned Cortex Compliance AI model
        self.hf_model = getattr(settings, "HUGGINGFACE_MODEL", "maaninder/cortex-compliance-ai")
        self.ollama_url = getattr(settings, "OLLAMA_URL", "http://localhost:11434")
        self.ai_provider = getattr(settings, "AI_PROVIDER", "huggingface")

    async def generate_document(
        self,
        document_type: str,
        company_name: str,
        company_inn: str,
        framework: str = "152-FZ",
        additional_context: dict | None = None,
    ) -> dict:
        """Generate a compliance document using AI.

        Args:
            document_type: Type of document (policy, consent, ispdn, notification, etc.)
            company_name: Company name in Russian
            company_inn: Company INN number
            framework: Compliance framework (152-FZ, 187-FZ, GOST-57580, FSTEC)
            additional_context: Additional data for document generation

        Returns:
            dict with generated content and metadata
        """
        prompt = self._build_prompt(
            document_type=document_type,
            company_name=company_name,
            company_inn=company_inn,
            framework=framework,
            additional_context=additional_context or {},
        )

        if self.ai_provider == "ollama":
            content = await self._call_ollama(prompt)
        elif self.ai_provider == "huggingface":
            content = await self._call_huggingface(prompt)
        else:
            content = self._generate_fallback(document_type, company_name, company_inn)

        return {
            "content": content,
            "document_type": document_type,
            "framework": framework,
            "company_name": company_name,
            "generated_by": self.ai_provider,
        }

    def _build_prompt(
        self,
        document_type: str,
        company_name: str,
        company_inn: str,
        framework: str,
        additional_context: dict,
    ) -> str:
        """Build the prompt for document generation."""
        document_type_names = {
            "policy": "Personal Data Processing Policy (Политика обработки персональных данных)",
            "consent": "Consent Form for Personal Data Processing (Согласие на обработку ПДн)",
            "ispdn": "ISPDN Description (Описание ИСПДн)",
            "notification": "Roskomnadzor Notification (Уведомление в Роскомнадзор)",
            "dpo_order": "DPO Appointment Order (Приказ о назначении ответственного)",
            "kii_act": "KII Categorization Act (Акт категорирования КИИ)",
            "security_policy": "Information Security Policy (Политика ИБ)",
        }

        doc_name = document_type_names.get(document_type, document_type)
        context_str = "\n".join(f"- {k}: {v}" for k, v in additional_context.items())

        return f"""### Instruction:
Generate a {doc_name} for company {company_name} (INN: {company_inn}).
Framework: {framework}
{f"Additional context:{chr(10)}{context_str}" if context_str else ""}

The document must be in formal Russian legal language and comply with {framework} requirements.

### Response:
"""

    async def _call_huggingface(self, prompt: str) -> str:
        """Call Hugging Face Inference API."""
        if not self.hf_token:
            return self._generate_fallback_message()

        headers = {"Authorization": f"Bearer {self.hf_token}"}
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": 1000,
                "temperature": 0.7,
                "do_sample": True,
                "return_full_text": False,
            },
        }

        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"https://api-inference.huggingface.co/models/{self.hf_model}",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()

                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", "")
                return str(result)
        except Exception as e:
            return f"[AI Generation Error: {e}]\n\n{self._generate_fallback_message()}"

    async def _call_ollama(self, prompt: str) -> str:
        """Call local Ollama instance."""
        payload = {
            "model": "mistral",
            "prompt": prompt,
            "stream": False,
            "options": {"temperature": 0.7, "num_predict": 1000},
        }

        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.ollama_url}/api/generate",
                    json=payload,
                )
                response.raise_for_status()
                result = response.json()
                return result.get("response", "")
        except Exception as e:
            return f"[Ollama Error: {e}]\n\n{self._generate_fallback_message()}"

    def _generate_fallback(
        self, document_type: str, company_name: str, company_inn: str
    ) -> str:
        """Generate a basic template when AI is not available."""
        templates = {
            "policy": f"""ПОЛИТИКА ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ
{company_name.upper()}

1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Настоящая Политика обработки персональных данных определяет позицию {company_name} (ИНН: {company_inn}) в области обработки и защиты персональных данных.

1.2. Политика разработана в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных».

2. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ

2.1. Оператор обрабатывает персональные данные в следующих целях:
- осуществление трудовых отношений с работниками;
- выполнение договорных обязательств перед контрагентами;
- обеспечение безопасности.

3. ПРАВОВЫЕ ОСНОВАНИЯ ОБРАБОТКИ

3.1. Обработка персональных данных осуществляется на основании:
- Трудового кодекса Российской Федерации;
- Гражданского кодекса Российской Федерации;
- согласия субъекта персональных данных.

Генеральный директор {company_name}
_________________ / _______________ /

Дата: «___» ____________ 20__ г.""",
            "consent": f"""СОГЛАСИЕ
на обработку персональных данных

Я, _________________________________________________ (ФИО полностью),
паспорт серия _______ № ____________, выдан ________________________________,

настоящим даю согласие {company_name} (ИНН: {company_inn}) на обработку моих персональных данных.

Настоящее согласие действует в течение всего срока обработки персональных данных.

«___» ____________ 20__ г.

___________________ / _____________________ /
     (подпись)            (расшифровка)""",
        }

        return templates.get(document_type, self._generate_fallback_message())

    def _generate_fallback_message(self) -> str:
        """Return message when AI is not configured."""
        return """[AI не настроен]

Для использования AI-генерации документов необходимо:
1. Настроить HUGGINGFACE_TOKEN в переменных окружения
2. Или установить Ollama и настроить OLLAMA_URL

Пока используется базовый шаблон документа."""


# Singleton instance
ai_document_service = AIDocumentService()
