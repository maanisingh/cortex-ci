"""
Russian Compliance Services
EGRUL integration, document template population, protection level calculation
"""

import logging
from datetime import date, datetime
from typing import Any
from uuid import UUID

import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.compliance.russian import (
    ISPDNCategory,
    ProtectionLevel,
    RuCompanyProfile,
    RuComplianceDocument,
    RuDocumentTemplate,
    RuFrameworkType,
    ThreatType,
)

logger = logging.getLogger(__name__)


# ============================================================================
# EGRUL SERVICE - Company Data by INN
# ============================================================================


class EGRULService:
    """
    Service for fetching company data from public Russian sources.
    Uses free APIs that don't require registration.
    """

    # Public EGRUL data sources (free, no signup required)
    DADATA_SUGGESTIONS_URL = "https://suggestions.dadata.ru/suggestions/api/4_1/rs/findById/party"
    FNS_EGRUL_URL = "https://egrul.nalog.ru/search-result"
    RUSPROFILE_URL = "https://www.rusprofile.ru/api/search"

    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0)

    async def lookup_by_inn(self, inn: str) -> dict[str, Any] | None:
        """
        Lookup company data by INN from public sources.
        Returns normalized company data.
        """
        # Validate INN format
        if not self._validate_inn(inn):
            logger.warning(f"Invalid INN format: {inn}")
            return None

        # Try multiple sources in order of reliability
        data = await self._lookup_rusprofile(inn)
        if data:
            return self._normalize_company_data(data, "rusprofile")

        data = await self._lookup_fns(inn)
        if data:
            return self._normalize_company_data(data, "fns")

        logger.warning(f"Company not found for INN: {inn}")
        return None

    def _validate_inn(self, inn: str) -> bool:
        """Validate Russian INN format (10 or 12 digits)."""
        if not inn or not inn.isdigit():
            return False
        return len(inn) in (10, 12)

    async def _lookup_rusprofile(self, inn: str) -> dict | None:
        """Lookup from rusprofile.ru (free public API)."""
        try:
            # This is a simplified example - real implementation would parse HTML or use their API
            response = await self.client.get(
                f"https://www.rusprofile.ru/search?query={inn}",
                headers={"User-Agent": "Mozilla/5.0 (compatible; GRC Platform)"},
            )
            if response.status_code == 200:
                # Parse the response - in real implementation, use BeautifulSoup or similar
                return {"source": "rusprofile", "inn": inn, "raw": response.text[:1000]}
        except Exception as e:
            logger.debug(f"Rusprofile lookup failed: {e}")
        return None

    async def _lookup_fns(self, inn: str) -> dict | None:
        """Lookup from FNS EGRUL (official tax service)."""
        try:
            # FNS EGRUL lookup - uses their search API
            search_response = await self.client.post(
                "https://egrul.nalog.ru/",
                data={"query": inn},
                headers={"User-Agent": "Mozilla/5.0 (compatible; GRC Platform)"},
            )
            if search_response.status_code == 200:
                return {"source": "fns", "inn": inn, "raw": search_response.text[:1000]}
        except Exception as e:
            logger.debug(f"FNS lookup failed: {e}")
        return None

    def _normalize_company_data(self, raw_data: dict, source: str) -> dict[str, Any]:
        """
        Normalize company data from various sources to a standard format.
        In production, this would parse the actual response.
        """
        # This is a demo implementation that returns sample data
        # Real implementation would parse HTML/JSON from the source
        inn = raw_data.get("inn", "")

        return {
            "inn": inn,
            "kpp": "",  # Would be parsed from source
            "ogrn": "",
            "okpo": "",
            "full_name": f"Company with INN {inn}",  # Would be parsed
            "short_name": "",
            "legal_form": "OOO",
            "legal_address": "",
            "actual_address": "",
            "postal_code": "",
            "region_code": "",
            "okved_main": "",
            "okved_main_name": "",
            "okved_additional": [],
            "director_name": "",
            "director_position": "",
            "director_inn": "",
            "registration_date": None,
            "source": source,
            "raw_data": raw_data,
        }

    async def close(self):
        """Close the HTTP client."""
        await self.client.aclose()


# Sample data for demo purposes
SAMPLE_COMPANIES = {
    "7707083893": {  # Sberbank
        "inn": "7707083893",
        "kpp": "773601001",
        "ogrn": "1027700132195",
        "okpo": "00032537",
        "full_name": 'Публичное акционерное общество "Сбербанк России"',
        "short_name": "ПАО Сбербанк",
        "legal_form": "ПАО",
        "legal_address": "117312, г. Москва, ул. Вавилова, д. 19",
        "okved_main": "64.19",
        "okved_main_name": "Денежное посредничество прочее",
        "director_name": "Греф Герман Оскарович",
        "director_position": "Президент, Председатель Правления",
        "registration_date": "1991-06-20",
        "is_financial_org": True,
    },
    "7702070139": {  # Gazprom
        "inn": "7702070139",
        "kpp": "997250001",
        "ogrn": "1027700070518",
        "okpo": "00040778",
        "full_name": 'Публичное акционерное общество "Газпром"',
        "short_name": "ПАО «Газпром»",
        "legal_form": "ПАО",
        "legal_address": "117420, г. Москва, ул. Намёткина, д. 16",
        "okved_main": "06.20",
        "okved_main_name": "Добыча природного газа",
        "director_name": "Миллер Алексей Борисович",
        "director_position": "Председатель Правления",
        "registration_date": "1993-02-17",
        "is_kii_subject": True,
    },
    "7736050003": {  # Rosneft
        "inn": "7736050003",
        "kpp": "997250001",
        "ogrn": "1027700043502",
        "okpo": "07050068",
        "full_name": 'Публичное акционерное общество "НК «Роснефть»"',
        "short_name": 'ПАО "НК «Роснефть»"',
        "legal_form": "ПАО",
        "legal_address": "115035, г. Москва, Софийская набережная, д. 26/1",
        "okved_main": "06.10",
        "okved_main_name": "Добыча сырой нефти и нефтяного (попутного) газа",
        "director_name": "Сечин Игорь Иванович",
        "director_position": "Президент, Председатель Правления",
        "registration_date": "1995-04-07",
        "is_kii_subject": True,
    },
}


async def get_company_by_inn_demo(inn: str) -> dict[str, Any] | None:
    """
    Demo function to get company data by INN.
    Uses sample data for demonstration.
    """
    if inn in SAMPLE_COMPANIES:
        return SAMPLE_COMPANIES[inn]

    # For demo: generate sample data for any valid INN
    if len(inn) in (10, 12) and inn.isdigit():
        return {
            "inn": inn,
            "kpp": f"{inn[:4]}01001" if len(inn) == 10 else "",
            "ogrn": f"1{inn}00" if len(inn) == 10 else f"3{inn}",
            "full_name": f"Общество с ограниченной ответственностью «Компания {inn[-4:]}»",
            "short_name": f"ООО «Компания {inn[-4:]}»",
            "legal_form": "ООО",
            "legal_address": "Москва, ул. Примерная, д. 1",
            "okved_main": "62.01",
            "okved_main_name": "Разработка компьютерного программного обеспечения",
            "director_name": "Иванов Иван Иванович",
            "director_position": "Генеральный директор",
            "registration_date": "2020-01-15",
        }

    return None


# ============================================================================
# PROTECTION LEVEL CALCULATOR (УЗ)
# ============================================================================


class ProtectionLevelCalculator:
    """
    Calculate required protection level (УЗ) per FSTEC Order 21.
    Based on personal data category, subject count, and threat type.
    """

    # Protection level matrix per FSTEC Order 21
    # Format: (category, subject_count, threat_type) -> protection_level
    PROTECTION_MATRIX = {
        # Special category PD
        (ISPDNCategory.SPECIAL, ">100000", ThreatType.TYPE_1): ProtectionLevel.UZ_1,
        (ISPDNCategory.SPECIAL, ">100000", ThreatType.TYPE_2): ProtectionLevel.UZ_1,
        (ISPDNCategory.SPECIAL, ">100000", ThreatType.TYPE_3): ProtectionLevel.UZ_2,
        (ISPDNCategory.SPECIAL, "<100000", ThreatType.TYPE_1): ProtectionLevel.UZ_1,
        (ISPDNCategory.SPECIAL, "<100000", ThreatType.TYPE_2): ProtectionLevel.UZ_2,
        (ISPDNCategory.SPECIAL, "<100000", ThreatType.TYPE_3): ProtectionLevel.UZ_3,
        # Biometric PD
        (ISPDNCategory.BIOMETRIC, ">100000", ThreatType.TYPE_1): ProtectionLevel.UZ_1,
        (ISPDNCategory.BIOMETRIC, ">100000", ThreatType.TYPE_2): ProtectionLevel.UZ_2,
        (ISPDNCategory.BIOMETRIC, ">100000", ThreatType.TYPE_3): ProtectionLevel.UZ_3,
        (ISPDNCategory.BIOMETRIC, "<100000", ThreatType.TYPE_1): ProtectionLevel.UZ_1,
        (ISPDNCategory.BIOMETRIC, "<100000", ThreatType.TYPE_2): ProtectionLevel.UZ_2,
        (ISPDNCategory.BIOMETRIC, "<100000", ThreatType.TYPE_3): ProtectionLevel.UZ_3,
        # Public PD (generally УЗ-4)
        (ISPDNCategory.PUBLIC, ">100000", ThreatType.TYPE_1): ProtectionLevel.UZ_2,
        (ISPDNCategory.PUBLIC, ">100000", ThreatType.TYPE_2): ProtectionLevel.UZ_3,
        (ISPDNCategory.PUBLIC, ">100000", ThreatType.TYPE_3): ProtectionLevel.UZ_4,
        (ISPDNCategory.PUBLIC, "<100000", ThreatType.TYPE_1): ProtectionLevel.UZ_2,
        (ISPDNCategory.PUBLIC, "<100000", ThreatType.TYPE_2): ProtectionLevel.UZ_3,
        (ISPDNCategory.PUBLIC, "<100000", ThreatType.TYPE_3): ProtectionLevel.UZ_4,
        # Other PD
        (ISPDNCategory.OTHER, ">100000", ThreatType.TYPE_1): ProtectionLevel.UZ_1,
        (ISPDNCategory.OTHER, ">100000", ThreatType.TYPE_2): ProtectionLevel.UZ_2,
        (ISPDNCategory.OTHER, ">100000", ThreatType.TYPE_3): ProtectionLevel.UZ_3,
        (ISPDNCategory.OTHER, "<100000", ThreatType.TYPE_1): ProtectionLevel.UZ_2,
        (ISPDNCategory.OTHER, "<100000", ThreatType.TYPE_2): ProtectionLevel.UZ_3,
        (ISPDNCategory.OTHER, "<100000", ThreatType.TYPE_3): ProtectionLevel.UZ_4,
    }

    @classmethod
    def calculate(
        cls,
        category: ISPDNCategory,
        subject_count: int,
        threat_type: ThreatType,
        is_employee_only: bool = False,
    ) -> ProtectionLevel:
        """
        Calculate protection level based on ISPDN parameters.

        Args:
            category: Personal data category
            subject_count: Number of data subjects
            threat_type: Threat type (1, 2, or 3)
            is_employee_only: True if only processing employee data

        Returns:
            Required protection level (УЗ-1 to УЗ-4)
        """
        # Determine subject count category
        count_category = ">100000" if subject_count >= 100000 else "<100000"

        # Special rule: employee-only systems can have reduced level
        if is_employee_only and category == ISPDNCategory.OTHER:
            # Employee data with no special categories can be УЗ-4
            if threat_type == ThreatType.TYPE_3:
                return ProtectionLevel.UZ_4

        # Lookup in matrix
        key = (category, count_category, threat_type)
        level = cls.PROTECTION_MATRIX.get(key)

        if level:
            return level

        # Default to highest protection if not found
        logger.warning(f"Protection level not found for key: {key}, defaulting to УЗ-1")
        return ProtectionLevel.UZ_1

    @classmethod
    def get_required_measures(cls, level: ProtectionLevel) -> dict[str, list[str]]:
        """
        Get required security measures for a protection level.
        Returns categorized list of measures per FSTEC Order 21.
        """
        base_measures = {
            "identification_auth": [
                "ИАФ.1 - Идентификация и аутентификация пользователей",
                "ИАФ.2 - Идентификация и аутентификация устройств",
            ],
            "access_control": [
                "УПД.1 - Управление учётными записями",
                "УПД.2 - Реализация ролевого метода",
                "УПД.3 - Управление информационными потоками",
            ],
            "integrity": [
                "ОЦЛ.1 - Контроль целостности ПО",
                "ОЦЛ.2 - Контроль целостности данных",
            ],
            "logging": [
                "РСБ.1 - Регистрация событий безопасности",
                "РСБ.2 - Мониторинг событий безопасности",
            ],
            "antivirus": [
                "АВЗ.1 - Антивирусная защита",
                "АВЗ.2 - Обновление баз сигнатур",
            ],
            "intrusion_detection": [
                "СОВ.1 - Обнаружение вторжений",
            ],
            "security_analysis": [
                "АНЗ.1 - Выявление уязвимостей",
                "АНЗ.2 - Контроль установки ПО",
            ],
            "protection_media": [
                "ЗНИ.1 - Учёт машинных носителей",
                "ЗНИ.2 - Управление доступом к носителям",
            ],
            "protection_env": [
                "ЗСВ.1 - Защита среды виртуализации",
            ],
            "protection_tech": [
                "ЗТС.1 - Контроль и управление физическим доступом",
            ],
            "protection_is": [
                "ЗИС.1 - Разделение функций администрирования",
                "ЗИС.2 - Защита периметра",
            ],
            "incident_response": [
                "ИНЦ.1 - Выявление инцидентов",
                "ИНЦ.2 - Информирование об инцидентах",
            ],
            "security_management": [
                "УБИ.1 - Определение угроз",
                "УБИ.2 - Управление уязвимостями",
            ],
        }

        # Add more stringent measures for higher protection levels
        if level in (ProtectionLevel.UZ_1, ProtectionLevel.UZ_2):
            base_measures["identification_auth"].extend([
                "ИАФ.3 - Идентификация и аутентификация администраторов",
                "ИАФ.4 - Управление идентификаторами",
                "ИАФ.5 - Управление средствами аутентификации",
                "ИАФ.6 - Защита обратной связи при аутентификации",
            ])
            base_measures["access_control"].extend([
                "УПД.4 - Разделение полномочий пользователей",
                "УПД.5 - Назначение минимально необходимых прав",
            ])
            base_measures["crypto"] = [
                "ЗКР.1 - Использование криптографических средств",
                "ЗКР.2 - Управление криптографическими ключами",
            ]

        if level == ProtectionLevel.UZ_1:
            base_measures["intrusion_detection"].append(
                "СОВ.2 - Обновление базы решающих правил"
            )
            base_measures["trusted_boot"] = [
                "ОДТ.1 - Использование средств доверенной загрузки",
            ]

        return base_measures


# ============================================================================
# DOCUMENT TEMPLATE SERVICE
# ============================================================================


class DocumentTemplateService:
    """
    Service for managing and populating Russian compliance document templates.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_templates_for_framework(
        self,
        framework: RuFrameworkType,
        protection_level: ProtectionLevel | None = None,
    ) -> list[RuDocumentTemplate]:
        """Get all templates for a specific framework."""
        query = select(RuDocumentTemplate).where(
            RuDocumentTemplate.framework == framework,
            RuDocumentTemplate.is_active == True,
        )

        if protection_level:
            # Filter by applicable protection level
            query = query.where(
                RuDocumentTemplate.applicable_uz.contains([protection_level.value])
            )

        query = query.order_by(RuDocumentTemplate.display_order)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def populate_template(
        self,
        template: RuDocumentTemplate,
        company: RuCompanyProfile,
        additional_data: dict | None = None,
    ) -> str:
        """
        Populate a template with company data.
        Returns filled template content.
        """
        content = template.template_content

        # Build replacement data
        replacements = {
            "{{company_name}}": company.full_name or "",
            "{{company_short_name}}": company.short_name or company.full_name or "",
            "{{inn}}": company.inn or "",
            "{{kpp}}": company.kpp or "",
            "{{ogrn}}": company.ogrn or "",
            "{{legal_address}}": company.legal_address or "",
            "{{actual_address}}": company.actual_address or company.legal_address or "",
            "{{director_name}}": company.director_name or "",
            "{{director_position}}": company.director_position or "Генеральный директор",
            "{{current_date}}": date.today().strftime("%d.%m.%Y"),
            "{{current_year}}": str(date.today().year),
            "{{phone}}": company.phone or "",
            "{{email}}": company.email or "",
            "{{website}}": company.website or "",
        }

        # Add additional data
        if additional_data:
            for key, value in additional_data.items():
                replacements[f"{{{{{key}}}}}"] = str(value) if value else ""

        # Apply replacements
        for placeholder, value in replacements.items():
            content = content.replace(placeholder, value)

        return content

    async def create_document_from_template(
        self,
        template_id: UUID,
        company_id: UUID,
        tenant_id: UUID,
        additional_data: dict | None = None,
    ) -> RuComplianceDocument:
        """
        Create a new compliance document from a template.
        """
        # Get template
        template = await self.db.get(RuDocumentTemplate, template_id)
        if not template:
            raise ValueError(f"Template not found: {template_id}")

        # Get company
        company = await self.db.get(RuCompanyProfile, company_id)
        if not company:
            raise ValueError(f"Company not found: {company_id}")

        # Populate content
        content = await self.populate_template(template, company, additional_data)

        # Create document
        document = RuComplianceDocument(
            company_id=company_id,
            tenant_id=tenant_id,
            template_id=template_id,
            document_code=f"{template.template_code}-{company.inn}",
            title=template.title,
            document_type=template.document_type,
            framework=template.framework,
            requirement_ref=template.requirement_ref,
            content=content,
        )

        self.db.add(document)
        await self.db.flush()

        return document


# ============================================================================
# 152-ФЗ DOCUMENT TEMPLATES
# ============================================================================


FZ152_TEMPLATES = [
    {
        "template_code": "FZ152-POL-001",
        "title": "Политика в отношении обработки персональных данных",
        "title_en": "Personal Data Processing Policy",
        "document_type": "ПОЛИТИКА",
        "framework": "152-ФЗ",
        "requirement_ref": "ст. 18.1",
        "is_mandatory": True,
        "display_order": 1,
        "description": "Основной документ, определяющий правила обработки ПДн в организации",
        "template_content": """
ПОЛИТИКА
{{company_name}}
в отношении обработки персональных данных

1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Настоящая Политика в отношении обработки персональных данных (далее – Политика) разработана в соответствии с Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных».

1.2. Настоящая Политика определяет правила обработки персональных данных {{company_short_name}} (далее – Оператор), основные направления деятельности Оператора в области защиты персональных данных.

1.3. Оператор: {{company_name}}
ИНН: {{inn}}
ОГРН: {{ogrn}}
Адрес: {{legal_address}}

2. ПРИНЦИПЫ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ

2.1. Обработка персональных данных осуществляется на законной и справедливой основе.

2.2. Обработка персональных данных ограничивается достижением конкретных, заранее определенных и законных целей.

2.3. Не допускается объединение баз данных, содержащих персональные данные, обработка которых осуществляется в целях, несовместимых между собой.

2.4. Обработке подлежат только персональные данные, которые отвечают целям их обработки.

2.5. Содержание и объем обрабатываемых персональных данных соответствуют заявленным целям обработки.

2.6. При обработке персональных данных обеспечивается точность персональных данных, их достаточность и актуальность.

2.7. Хранение персональных данных осуществляется в форме, позволяющей определить субъекта персональных данных, не дольше, чем этого требуют цели обработки.

3. ЦЕЛИ ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ

3.1. Оператор осуществляет обработку персональных данных в следующих целях:
- [Цели обработки]

4. ПРАВОВЫЕ ОСНОВАНИЯ ОБРАБОТКИ

4.1. Обработка персональных данных осуществляется на основании:
- Согласия субъекта персональных данных
- Исполнения договора с субъектом персональных данных
- Исполнения обязанностей, возложенных на Оператора законодательством РФ

5. ПРАВА СУБЪЕКТОВ ПЕРСОНАЛЬНЫХ ДАННЫХ

5.1. Субъект персональных данных имеет право:
- На получение сведений об обработке персональных данных
- На доступ к своим персональным данным
- На уточнение, блокирование или уничтожение персональных данных
- На отзыв согласия на обработку персональных данных

6. ОБЯЗАННОСТИ ОПЕРАТОРА

6.1. Оператор обязуется:
- Обрабатывать персональные данные в соответствии с законодательством
- Обеспечивать защиту персональных данных от неправомерного доступа
- Предоставлять субъекту информацию об обработке его данных
- Уведомлять уполномоченный орган о начале обработки персональных данных

7. МЕРЫ ПО ОБЕСПЕЧЕНИЮ БЕЗОПАСНОСТИ

7.1. Оператор принимает необходимые правовые, организационные и технические меры для защиты персональных данных.

8. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

8.1. Настоящая Политика является общедоступным документом и подлежит размещению на официальном сайте Оператора.

8.2. Настоящая Политика вступает в силу с момента утверждения.


{{director_position}}
{{company_short_name}}                    _______________ / {{director_name}} /

«___» _____________ {{current_year}} г.
""",
    },
    {
        "template_code": "FZ152-ORD-001",
        "title": "Приказ о назначении ответственного за организацию обработки персональных данных",
        "title_en": "Order on Appointment of Personal Data Processing Officer",
        "document_type": "ПРИКАЗ",
        "framework": "152-ФЗ",
        "requirement_ref": "ст. 22.1",
        "is_mandatory": True,
        "display_order": 2,
        "description": "Приказ о назначении лица, ответственного за организацию обработки ПДн",
        "template_content": """
{{company_name}}

ПРИКАЗ № ___

г. Москва                                           «___» _____________ {{current_year}} г.

О назначении ответственного за организацию
обработки персональных данных

В соответствии с частью 1 статьи 22.1 Федерального закона от 27.07.2006 № 152-ФЗ «О персональных данных»,

ПРИКАЗЫВАЮ:

1. Назначить ответственным за организацию обработки персональных данных в {{company_short_name}} [ФИО, должность].

2. Ответственному за организацию обработки персональных данных:
   2.1. Обеспечить контроль соблюдения законодательства о персональных данных.
   2.2. Организовать разработку и актуализацию локальных актов по защите персональных данных.
   2.3. Обеспечить доведение до работников требований законодательства о персональных данных.
   2.4. Организовать обучение работников правилам работы с персональными данными.
   2.5. Осуществлять внутренний контроль соответствия обработки персональных данных требованиям законодательства.
   2.6. Обеспечить прием и обработку обращений субъектов персональных данных.

3. Контроль исполнения настоящего приказа оставляю за собой.


{{director_position}}
{{company_short_name}}                    _______________ / {{director_name}} /
""",
    },
    {
        "template_code": "FZ152-CON-001",
        "title": "Согласие на обработку персональных данных",
        "title_en": "Personal Data Processing Consent",
        "document_type": "СОГЛАСИЕ",
        "framework": "152-ФЗ",
        "requirement_ref": "ст. 9",
        "is_mandatory": True,
        "display_order": 3,
        "description": "Форма согласия субъекта на обработку персональных данных",
        "template_content": """
СОГЛАСИЕ
на обработку персональных данных

Я, ___________________________________________________ ,
         (фамилия, имя, отчество субъекта персональных данных)

паспорт серия _______ № _______________ выдан _________________________________
                                                    (кем, когда)

проживающий(ая) по адресу: ___________________________________________________

настоящим даю согласие {{company_name}}
(ИНН: {{inn}}, адрес: {{legal_address}})

на обработку моих персональных данных, а именно:
- фамилия, имя, отчество;
- дата рождения;
- паспортные данные;
- адрес регистрации и фактического проживания;
- номер телефона;
- адрес электронной почты;
- [иные категории персональных данных]

в целях:
- [цели обработки персональных данных]

Настоящее согласие действует с даты его подписания до момента достижения целей обработки или до отзыва согласия.

Согласие может быть отозвано путем направления письменного заявления по адресу: {{legal_address}}

Я уведомлен(а) о том, что имею право:
- требовать уточнения своих персональных данных;
- требовать блокирования или уничтожения персональных данных;
- получать информацию об обработке персональных данных;
- обжаловать действия или бездействие оператора в уполномоченный орган.


«___» _____________ 20__ г.              _______________ / ____________________ /
                                               (подпись)         (расшифровка)
""",
    },
    {
        "template_code": "FZ152-REG-001",
        "title": "Положение об обработке персональных данных",
        "title_en": "Regulation on Personal Data Processing",
        "document_type": "ПОЛОЖЕНИЕ",
        "framework": "152-ФЗ",
        "requirement_ref": "ст. 18.1",
        "is_mandatory": True,
        "display_order": 4,
        "description": "Внутреннее положение, регламентирующее порядок обработки ПДн",
        "template_content": """
УТВЕРЖДАЮ
{{director_position}}
{{company_short_name}}
_______________ / {{director_name}} /
«___» _____________ {{current_year}} г.


ПОЛОЖЕНИЕ
об обработке персональных данных
в {{company_short_name}}


1. ОБЩИЕ ПОЛОЖЕНИЯ

1.1. Настоящее Положение определяет порядок обработки персональных данных в {{company_name}} (далее – Оператор).

1.2. Положение разработано в соответствии с:
- Конституцией Российской Федерации
- Трудовым кодексом Российской Федерации
- Федеральным законом от 27.07.2006 № 152-ФЗ «О персональных данных»
- Постановлением Правительства РФ от 01.11.2012 № 1119
- Приказом ФСТЭК России от 18.02.2013 № 21

2. ОСНОВНЫЕ ПОНЯТИЯ

2.1. Персональные данные – любая информация, относящаяся к прямо или косвенно определенному физическому лицу (субъекту персональных данных).

2.2. Обработка персональных данных – любое действие с персональными данными.

2.3. Оператор – юридическое лицо, осуществляющее обработку персональных данных.

3. КАТЕГОРИИ ОБРАБАТЫВАЕМЫХ ПЕРСОНАЛЬНЫХ ДАННЫХ

3.1. Оператор обрабатывает следующие категории персональных данных:
- Персональные данные работников
- Персональные данные клиентов
- [Иные категории]

4. ПОРЯДОК ОБРАБОТКИ ПЕРСОНАЛЬНЫХ ДАННЫХ

4.1. Обработка персональных данных осуществляется:
- С использованием средств автоматизации
- Без использования средств автоматизации

4.2. Обработка осуществляется с соблюдением принципов:
- Законности
- Соответствия целям
- Соразмерности
- Точности
- Ограниченного срока хранения

5. ЗАЩИТА ПЕРСОНАЛЬНЫХ ДАННЫХ

5.1. Для защиты персональных данных применяются:
- Организационные меры
- Технические меры
- Правовые меры

6. ПРАВА И ОБЯЗАННОСТИ

6.1. Субъекты персональных данных имеют право на доступ к своим данным.

6.2. Работники Оператора обязаны соблюдать конфиденциальность персональных данных.

7. ОТВЕТСТВЕННОСТЬ

7.1. Работники, нарушившие требования настоящего Положения, несут ответственность в соответствии с законодательством РФ.

8. ЗАКЛЮЧИТЕЛЬНЫЕ ПОЛОЖЕНИЯ

8.1. Настоящее Положение вступает в силу с момента утверждения.

8.2. Изменения в настоящее Положение вносятся приказом Оператора.
""",
    },
    {
        "template_code": "FZ152-JRN-001",
        "title": "Журнал учёта обращений субъектов персональных данных",
        "title_en": "Register of Personal Data Subject Requests",
        "document_type": "ЖУРНАЛ",
        "framework": "152-ФЗ",
        "requirement_ref": "ст. 20",
        "is_mandatory": True,
        "display_order": 5,
        "description": "Журнал для регистрации обращений субъектов ПДн",
        "template_content": """
{{company_name}}


ЖУРНАЛ
учёта обращений субъектов персональных данных


Начат: «___» _____________ 20__ г.
Окончен: «___» _____________ 20__ г.

+-----+------------+-----------------------+----------------------+------------+-------------+------------------+------------+
| №   | Дата       | ФИО субъекта ПДн      | Содержание           | Срок       | Ответ-      | Результат        | Дата       |
| п/п | обращения  |                       | обращения            | рассмот-   | ственный    | рассмотрения     | ответа     |
|     |            |                       |                      | рения      |             |                  |            |
+-----+------------+-----------------------+----------------------+------------+-------------+------------------+------------+
| 1   |            |                       |                      |            |             |                  |            |
+-----+------------+-----------------------+----------------------+------------+-------------+------------------+------------+
| 2   |            |                       |                      |            |             |                  |            |
+-----+------------+-----------------------+----------------------+------------+-------------+------------------+------------+
| 3   |            |                       |                      |            |             |                  |            |
+-----+------------+-----------------------+----------------------+------------+-------------+------------------+------------+


Ответственный за ведение журнала: _______________ / ____________________ /
                                      (подпись)         (расшифровка)
""",
    },
]


# ============================================================================
# EMAIL TEMPLATES (RUSSIAN)
# ============================================================================


RU_EMAIL_TEMPLATES = [
    {
        "template_code": "RU-TASK-ASSIGN",
        "name": "Назначение задачи",
        "category": "ASSIGNMENT",
        "subject": "Вам назначена новая задача: {{task_title}}",
        "body_text": """
Уважаемый(ая) {{recipient_name}}!

Вам назначена новая задача в системе управления соответствием.

Задача: {{task_title}}
Рамочный документ: {{framework}}
Срок выполнения: {{due_date}}
Приоритет: {{priority}}

Описание:
{{task_description}}

Для выполнения задачи перейдите в систему:
{{task_url}}

С уважением,
Система управления соответствием
{{company_name}}
""",
        "variables": [
            "recipient_name",
            "task_title",
            "framework",
            "due_date",
            "priority",
            "task_description",
            "task_url",
            "company_name",
        ],
    },
    {
        "template_code": "RU-TASK-REMINDER",
        "name": "Напоминание о задаче",
        "category": "REMINDER",
        "subject": "Напоминание: задача {{task_title}} требует внимания",
        "body_text": """
Уважаемый(ая) {{recipient_name}}!

Напоминаем о необходимости выполнить задачу.

Задача: {{task_title}}
Срок выполнения: {{due_date}}
Осталось дней: {{days_left}}

Для выполнения задачи перейдите в систему:
{{task_url}}

С уважением,
Система управления соответствием
{{company_name}}
""",
        "variables": [
            "recipient_name",
            "task_title",
            "due_date",
            "days_left",
            "task_url",
            "company_name",
        ],
    },
    {
        "template_code": "RU-TASK-OVERDUE",
        "name": "Просроченная задача",
        "category": "OVERDUE",
        "subject": "[СРОЧНО] Просрочена задача: {{task_title}}",
        "body_text": """
Уважаемый(ая) {{recipient_name}}!

ВНИМАНИЕ: Задача просрочена!

Задача: {{task_title}}
Плановый срок: {{due_date}}
Просрочено дней: {{overdue_days}}

Просим незамедлительно выполнить задачу или связаться с руководителем.

Ссылка на задачу:
{{task_url}}

С уважением,
Система управления соответствием
{{company_name}}
""",
        "variables": [
            "recipient_name",
            "task_title",
            "due_date",
            "overdue_days",
            "task_url",
            "company_name",
        ],
    },
    {
        "template_code": "RU-WEEKLY-DIGEST",
        "name": "Еженедельный дайджест",
        "category": "DIGEST",
        "subject": "Еженедельный отчёт по соответствию за {{week_dates}}",
        "body_text": """
Уважаемый(ая) {{recipient_name}}!

Еженедельный отчёт по соответствию за период {{week_dates}}.

ОБЩАЯ СТАТИСТИКА:
- Всего задач: {{total_tasks}}
- Выполнено: {{completed_tasks}}
- В работе: {{in_progress_tasks}}
- Просрочено: {{overdue_tasks}}

ТРЕБУЕТ ВНИМАНИЯ:
{{attention_items}}

БЛИЖАЙШИЕ СРОКИ:
{{upcoming_deadlines}}

Подробности в системе:
{{dashboard_url}}

С уважением,
Система управления соответствием
{{company_name}}
""",
        "variables": [
            "recipient_name",
            "week_dates",
            "total_tasks",
            "completed_tasks",
            "in_progress_tasks",
            "overdue_tasks",
            "attention_items",
            "upcoming_deadlines",
            "dashboard_url",
            "company_name",
        ],
    },
    {
        "template_code": "RU-DOC-REVIEW",
        "name": "Документ на проверку",
        "category": "REVIEW",
        "subject": "Документ {{document_title}} ожидает проверки",
        "body_text": """
Уважаемый(ая) {{recipient_name}}!

Документ направлен вам на проверку.

Документ: {{document_title}}
Рамочный документ: {{framework}}
Подготовил: {{author_name}}
Дата подготовки: {{created_date}}

Для проверки документа перейдите по ссылке:
{{document_url}}

С уважением,
Система управления соответствием
{{company_name}}
""",
        "variables": [
            "recipient_name",
            "document_title",
            "framework",
            "author_name",
            "created_date",
            "document_url",
            "company_name",
        ],
    },
]
