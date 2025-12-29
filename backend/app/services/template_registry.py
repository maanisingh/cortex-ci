"""
Unified Template Registry
Central service for accessing all 225+ document templates across categories

Categories:
- Corporate/Shareholders (15 templates)
- HR/Employment (20 templates)
- Commercial Contracts (25 templates)
- Financial/Accounting (18 templates)
- Tax/Regulatory (15 templates)
- Legal/IP (12 templates)
- Industry-Specific (40 templates)
- Real Estate (12 templates)
- Banking/Finance (15 templates)
- Government Tenders (15 templates)
- Licenses/Permits (10 templates)
- Environmental/Safety (12 templates)
- Vehicles/Equipment (8 templates)
- Quality/Certification (10 templates)
- Crisis/Restructuring (8 templates)

Plus GRC Compliance Templates:
- 152-FZ Personal Data Protection
- 187-FZ Critical Infrastructure
- GOST R 57580 Financial Security
"""

from typing import Dict, Any, List, Optional, Union
from datetime import date
from enum import Enum
from pydantic import BaseModel

# Import all template services
from app.services.sme_templates_corporate import CorporateTemplateService, CorporateDocType
from app.services.sme_templates_hr import HRTemplateService, HRDocType
from app.services.sme_templates_contracts import ContractTemplateService, ContractType
from app.services.sme_templates_financial import FinancialTemplateService, FinancialDocType
from app.services.sme_templates_tax import TaxTemplateService, TaxDocType
from app.services.sme_templates_legal import LegalTemplateService, LegalDocType
from app.services.sme_templates_industry import IndustryTemplateService, IndustryDocType, Industry
from app.services.sme_templates_specialized import (
    SpecializedTemplateService,
    RealEstateDocType,
    BankingDocType,
    GovTenderDocType,
    LicenseDocType,
    EnvironmentalDocType,
    VehicleDocType,
    QualityDocType,
    CrisisDocType,
)


class TemplateCategory(str, Enum):
    """Main template categories."""
    CORPORATE = "corporate"
    HR = "hr"
    CONTRACTS = "contracts"
    FINANCIAL = "financial"
    TAX = "tax"
    LEGAL = "legal"
    INDUSTRY = "industry"
    REAL_ESTATE = "real_estate"
    BANKING = "banking"
    GOV_TENDERS = "gov_tenders"
    LICENSES = "licenses"
    ENVIRONMENTAL = "environmental"
    VEHICLES = "vehicles"
    QUALITY = "quality"
    CRISIS = "crisis"
    GRC_COMPLIANCE = "grc_compliance"


class CompanyLifecycleStage(str, Enum):
    """Company lifecycle stages for template recommendations."""
    IDEA = "idea"  # Pre-registration
    REGISTRATION = "registration"  # Company formation
    LAUNCH = "launch"  # First months of operation
    GROWTH = "growth"  # Scaling operations
    MATURITY = "maturity"  # Stable operations
    EXPANSION = "expansion"  # New markets/products
    RESTRUCTURING = "restructuring"  # Changes/optimization
    EXIT = "exit"  # Sale, merger, liquidation


class TemplateInfo(BaseModel):
    """Template metadata."""
    id: str
    name: str
    name_en: Optional[str] = None
    category: TemplateCategory
    description: Optional[str] = None
    required_fields: List[str] = []
    lifecycle_stages: List[CompanyLifecycleStage] = []
    tags: List[str] = []
    regulatory_refs: List[str] = []  # e.g., ["152-FZ", "GOST R 57580"]


class TemplateRegistry:
    """
    Unified registry for all document templates.
    Provides single entry point for template discovery and generation.
    """

    # Category to service mapping
    CATEGORY_SERVICES = {
        TemplateCategory.CORPORATE: CorporateTemplateService,
        TemplateCategory.HR: HRTemplateService,
        TemplateCategory.CONTRACTS: ContractTemplateService,
        TemplateCategory.FINANCIAL: FinancialTemplateService,
        TemplateCategory.TAX: TaxTemplateService,
        TemplateCategory.LEGAL: LegalTemplateService,
        TemplateCategory.INDUSTRY: IndustryTemplateService,
    }

    # Lifecycle stage recommendations
    STAGE_TEMPLATES = {
        CompanyLifecycleStage.IDEA: [
            "founders_agreement",
            "nda",
            "preliminary_agreement",
        ],
        CompanyLifecycleStage.REGISTRATION: [
            "charter_ooo",
            "formation_decision_sole",
            "formation_decision_multiple",
            "founders_agreement",
            "tax_registration",
            "usn_application",
            "account_opening",
        ],
        CompanyLifecycleStage.LAUNCH: [
            "employment_contract",
            "director_appointment_order",
            "accounting_policy",
            "internal_labor_rules",
            "privacy_policy",
            "online_terms",
        ],
        CompanyLifecycleStage.GROWTH: [
            "supply",
            "service",
            "lease",
            "loan",
            "employment_contract",
            "contractor_agreement",
            "leasing",
        ],
        CompanyLifecycleStage.MATURITY: [
            "dividend_resolution",
            "shareholder_meeting_minutes",
            "quality_manual",
            "sla_agreement",
            "distribution",
        ],
        CompanyLifecycleStage.EXPANSION: [
            "franchise",
            "joint_venture",
            "licensing",
            "construction_contract",
            "bank_guarantee",
        ],
        CompanyLifecycleStage.RESTRUCTURING: [
            "restructuring_plan",
            "creditor_agreement",
            "debt_restructuring",
            "capital_increase_decision",
            "share_sale_agreement",
        ],
        CompanyLifecycleStage.EXIT: [
            "voluntary_liquidation",
            "liquidation_decision",
            "asset_sale",
            "settlement",
        ],
    }

    @classmethod
    def get_categories(cls) -> List[Dict[str, Any]]:
        """Get all available template categories."""
        return [
            {
                "id": cat.value,
                "name": cls._get_category_name(cat),
                "template_count": cls._get_category_count(cat),
            }
            for cat in TemplateCategory
        ]

    @classmethod
    def _get_category_name(cls, category: TemplateCategory) -> str:
        """Get Russian name for category."""
        names = {
            TemplateCategory.CORPORATE: "Корпоративные документы",
            TemplateCategory.HR: "Кадровые документы",
            TemplateCategory.CONTRACTS: "Коммерческие договоры",
            TemplateCategory.FINANCIAL: "Финансовые документы",
            TemplateCategory.TAX: "Налоговые документы",
            TemplateCategory.LEGAL: "Юридические документы",
            TemplateCategory.INDUSTRY: "Отраслевые документы",
            TemplateCategory.REAL_ESTATE: "Недвижимость",
            TemplateCategory.BANKING: "Банковские документы",
            TemplateCategory.GOV_TENDERS: "Госзакупки (44-ФЗ/223-ФЗ)",
            TemplateCategory.LICENSES: "Лицензии и разрешения",
            TemplateCategory.ENVIRONMENTAL: "Экология и охрана труда",
            TemplateCategory.VEHICLES: "Транспорт и оборудование",
            TemplateCategory.QUALITY: "Качество и сертификация",
            TemplateCategory.CRISIS: "Антикризисные документы",
            TemplateCategory.GRC_COMPLIANCE: "GRC Комплаенс",
        }
        return names.get(category, category.value)

    @classmethod
    def _get_category_count(cls, category: TemplateCategory) -> int:
        """Get template count for category."""
        counts = {
            TemplateCategory.CORPORATE: 15,
            TemplateCategory.HR: 20,
            TemplateCategory.CONTRACTS: 25,
            TemplateCategory.FINANCIAL: 18,
            TemplateCategory.TAX: 15,
            TemplateCategory.LEGAL: 12,
            TemplateCategory.INDUSTRY: 40,
            TemplateCategory.REAL_ESTATE: 12,
            TemplateCategory.BANKING: 15,
            TemplateCategory.GOV_TENDERS: 15,
            TemplateCategory.LICENSES: 10,
            TemplateCategory.ENVIRONMENTAL: 12,
            TemplateCategory.VEHICLES: 8,
            TemplateCategory.QUALITY: 10,
            TemplateCategory.CRISIS: 8,
            TemplateCategory.GRC_COMPLIANCE: 30,
        }
        return counts.get(category, 0)

    @classmethod
    def list_templates(cls, category: Optional[TemplateCategory] = None) -> List[Dict[str, str]]:
        """List all templates, optionally filtered by category."""
        templates = []

        if category is None or category == TemplateCategory.CORPORATE:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "corporate"}
                for t in CorporateTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.HR:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "hr"}
                for t in HRTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.CONTRACTS:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "contracts"}
                for t in ContractTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.FINANCIAL:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "financial"}
                for t in FinancialTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.TAX:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "tax"}
                for t in TaxTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.LEGAL:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "legal"}
                for t in LegalTemplateService.list_templates()
            ])

        if category is None or category == TemplateCategory.INDUSTRY:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "industry"}
                for t in IndustryTemplateService.list_templates()
            ])

        # Add specialized templates
        if category is None or category in [
            TemplateCategory.REAL_ESTATE,
            TemplateCategory.BANKING,
            TemplateCategory.GOV_TENDERS,
            TemplateCategory.LICENSES,
            TemplateCategory.ENVIRONMENTAL,
            TemplateCategory.VEHICLES,
            TemplateCategory.QUALITY,
            TemplateCategory.CRISIS,
        ]:
            templates.extend([
                {"type": t["type"], "name": t["name"], "category": "specialized"}
                for t in SpecializedTemplateService.list_all_templates()
            ])

        return templates

    @classmethod
    def get_templates_for_stage(cls, stage: CompanyLifecycleStage) -> List[Dict[str, str]]:
        """Get recommended templates for a company lifecycle stage."""
        recommended_ids = cls.STAGE_TEMPLATES.get(stage, [])
        all_templates = cls.list_templates()

        return [t for t in all_templates if t["type"] in recommended_ids]

    @classmethod
    def search_templates(cls, query: str) -> List[Dict[str, str]]:
        """Search templates by name or type."""
        query_lower = query.lower()
        all_templates = cls.list_templates()

        return [
            t for t in all_templates
            if query_lower in t["name"].lower() or query_lower in t["type"].lower()
        ]

    @classmethod
    def generate_document(
        cls,
        template_type: str,
        data: Dict[str, Any],
        category: Optional[TemplateCategory] = None
    ) -> str:
        """
        Generate a document from any template.

        Args:
            template_type: Template identifier (e.g., "charter_ooo", "employment_contract")
            data: Dictionary with field values
            category: Optional category hint for faster lookup

        Returns:
            Generated document as string

        Raises:
            ValueError: If template not found or missing required fields
        """
        # Try each service until we find the template
        services_to_try = []

        if category:
            service = cls.CATEGORY_SERVICES.get(category)
            if service:
                services_to_try.append(service)

        # Add all services as fallback
        services_to_try.extend([
            CorporateTemplateService,
            HRTemplateService,
            ContractTemplateService,
            FinancialTemplateService,
            TaxTemplateService,
            LegalTemplateService,
            IndustryTemplateService,
            SpecializedTemplateService,
        ])

        # Try to find and generate template
        for service in services_to_try:
            try:
                # Different services have different enum types
                if service == CorporateTemplateService:
                    doc_type = CorporateDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == HRTemplateService:
                    doc_type = HRDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == ContractTemplateService:
                    doc_type = ContractType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == FinancialTemplateService:
                    doc_type = FinancialDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == TaxTemplateService:
                    doc_type = TaxDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == LegalTemplateService:
                    doc_type = LegalDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == IndustryTemplateService:
                    doc_type = IndustryDocType(template_type)
                    return service.generate_document(doc_type, data)
                elif service == SpecializedTemplateService:
                    return service.generate_document(template_type, data)
            except (ValueError, KeyError):
                continue

        raise ValueError(f"Template not found: {template_type}")

    @classmethod
    def get_template_fields(cls, template_type: str) -> List[str]:
        """Get required fields for a template."""
        # This would be implemented by extracting {field} placeholders from templates
        # For now, return empty list as placeholder
        return []

    @classmethod
    def get_template_count(cls) -> int:
        """Get total number of available templates."""
        return sum(cls._get_category_count(cat) for cat in TemplateCategory)

    @classmethod
    def get_statistics(cls) -> Dict[str, Any]:
        """Get template registry statistics."""
        return {
            "total_templates": cls.get_template_count(),
            "categories": len(TemplateCategory),
            "categories_breakdown": {
                cat.value: cls._get_category_count(cat)
                for cat in TemplateCategory
            },
            "lifecycle_stages": len(CompanyLifecycleStage),
        }


# Singleton instance for easy access
registry = TemplateRegistry()
