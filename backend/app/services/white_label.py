"""
White-Label Service
Custom branding for multi-tenant deployments.

Features:
- Custom logo and colors
- Custom domain mapping
- Email template customization
- PDF report branding
- Localization overrides
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import UUID, uuid4
import os
import json


class BrandingConfig(BaseModel):
    company_id: UUID

    # Logo and visuals
    logo_url: Optional[str] = None
    logo_dark_url: Optional[str] = None  # For dark mode
    favicon_url: Optional[str] = None

    # Colors (hex format)
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"
    accent_color: str = "#3b82f6"
    success_color: str = "#10b981"
    warning_color: str = "#f59e0b"
    error_color: str = "#ef4444"

    # Dark mode colors
    dark_bg_color: str = "#1f2937"
    dark_card_color: str = "#374151"
    dark_text_color: str = "#f3f4f6"

    # Typography
    font_family: str = "Inter, system-ui, sans-serif"
    heading_font: Optional[str] = None

    # Names and text
    platform_name: str = "CORTEX GRC"
    platform_name_ru: str = "CORTEX ГРК"
    tagline: Optional[str] = None
    tagline_ru: Optional[str] = None

    # Footer
    footer_text: str = "CORTEX GRC - Система управления соответствием"
    footer_links: List[Dict[str, str]] = []

    # Contact
    support_email: Optional[str] = None
    support_phone: Optional[str] = None

    # Legal
    terms_url: Optional[str] = None
    privacy_url: Optional[str] = None

    # Custom domain
    custom_domain: Optional[str] = None

    # Feature flags for white-label
    show_powered_by: bool = True
    show_version: bool = True

    updated_at: datetime = Field(default_factory=datetime.utcnow)


class EmailBranding(BaseModel):
    company_id: UUID
    header_logo_url: Optional[str] = None
    header_bg_color: str = "#2563eb"
    header_text_color: str = "#ffffff"
    button_color: str = "#2563eb"
    footer_text: str = "CORTEX GRC - Система управления соответствием"
    footer_logo_url: Optional[str] = None
    custom_css: Optional[str] = None


class PDFBranding(BaseModel):
    company_id: UUID
    header_logo_url: Optional[str] = None
    footer_logo_url: Optional[str] = None
    header_text: Optional[str] = None
    footer_text: str = "Сгенерировано системой CORTEX GRC"
    watermark_text: Optional[str] = None
    watermark_opacity: float = 0.1
    primary_color: str = "#2563eb"
    show_page_numbers: bool = True
    show_generation_date: bool = True


class WhiteLabelService:
    """
    Service for managing white-label branding.
    """

    def __init__(self):
        self.branding_configs: Dict[UUID, BrandingConfig] = {}
        self.email_branding: Dict[UUID, EmailBranding] = {}
        self.pdf_branding: Dict[UUID, PDFBranding] = {}
        self.domain_mapping: Dict[str, UUID] = {}  # domain -> company_id

    # ==========================================================================
    # Branding Configuration
    # ==========================================================================

    async def get_branding(self, company_id: UUID) -> BrandingConfig:
        """Get branding config for a company."""
        if company_id in self.branding_configs:
            return self.branding_configs[company_id]
        return BrandingConfig(company_id=company_id)

    async def update_branding(
        self,
        company_id: UUID,
        data: Dict[str, Any]
    ) -> BrandingConfig:
        """Update branding config."""
        config = await self.get_branding(company_id)

        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        config.updated_at = datetime.utcnow()
        self.branding_configs[company_id] = config

        # Update domain mapping if custom domain changed
        if "custom_domain" in data and data["custom_domain"]:
            self.domain_mapping[data["custom_domain"]] = company_id

        return config

    async def get_branding_by_domain(self, domain: str) -> Optional[BrandingConfig]:
        """Get branding config by custom domain."""
        company_id = self.domain_mapping.get(domain)
        if company_id:
            return await self.get_branding(company_id)
        return None

    # ==========================================================================
    # Email Branding
    # ==========================================================================

    async def get_email_branding(self, company_id: UUID) -> EmailBranding:
        """Get email branding for a company."""
        if company_id in self.email_branding:
            return self.email_branding[company_id]
        return EmailBranding(company_id=company_id)

    async def update_email_branding(
        self,
        company_id: UUID,
        data: Dict[str, Any]
    ) -> EmailBranding:
        """Update email branding."""
        config = await self.get_email_branding(company_id)

        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.email_branding[company_id] = config
        return config

    async def render_email_template(
        self,
        company_id: UUID,
        template: str,
        data: Dict[str, Any]
    ) -> str:
        """Render email template with company branding."""
        branding = await self.get_email_branding(company_id)

        # Replace branding placeholders
        rendered = template.replace("{{header_bg_color}}", branding.header_bg_color)
        rendered = rendered.replace("{{header_text_color}}", branding.header_text_color)
        rendered = rendered.replace("{{button_color}}", branding.button_color)
        rendered = rendered.replace("{{footer_text}}", branding.footer_text)

        if branding.header_logo_url:
            rendered = rendered.replace(
                "{{header_logo}}",
                f'<img src="{branding.header_logo_url}" alt="Logo" style="max-height: 50px;">'
            )
        else:
            rendered = rendered.replace("{{header_logo}}", "")

        # Apply data
        for key, value in data.items():
            rendered = rendered.replace(f"{{{{{key}}}}}", str(value))

        return rendered

    # ==========================================================================
    # PDF Branding
    # ==========================================================================

    async def get_pdf_branding(self, company_id: UUID) -> PDFBranding:
        """Get PDF branding for a company."""
        if company_id in self.pdf_branding:
            return self.pdf_branding[company_id]
        return PDFBranding(company_id=company_id)

    async def update_pdf_branding(
        self,
        company_id: UUID,
        data: Dict[str, Any]
    ) -> PDFBranding:
        """Update PDF branding."""
        config = await self.get_pdf_branding(company_id)

        for key, value in data.items():
            if hasattr(config, key):
                setattr(config, key, value)

        self.pdf_branding[company_id] = config
        return config

    # ==========================================================================
    # CSS Generation
    # ==========================================================================

    async def generate_css_variables(self, company_id: UUID) -> str:
        """Generate CSS variables for company branding."""
        branding = await self.get_branding(company_id)

        css = f"""
:root {{
    --primary: {branding.primary_color};
    --secondary: {branding.secondary_color};
    --accent: {branding.accent_color};
    --success: {branding.success_color};
    --warning: {branding.warning_color};
    --error: {branding.error_color};
    --font-family: {branding.font_family};
    {"--heading-font: " + branding.heading_font + ";" if branding.heading_font else ""}
}}

.dark {{
    --bg-primary: {branding.dark_bg_color};
    --bg-card: {branding.dark_card_color};
    --text-primary: {branding.dark_text_color};
}}
        """.strip()

        return css

    async def get_frontend_config(self, company_id: UUID) -> Dict[str, Any]:
        """Get frontend configuration for white-label."""
        branding = await self.get_branding(company_id)

        return {
            "platformName": branding.platform_name,
            "platformNameRu": branding.platform_name_ru,
            "tagline": branding.tagline,
            "taglineRu": branding.tagline_ru,
            "logoUrl": branding.logo_url,
            "logoDarkUrl": branding.logo_dark_url,
            "faviconUrl": branding.favicon_url,
            "colors": {
                "primary": branding.primary_color,
                "secondary": branding.secondary_color,
                "accent": branding.accent_color,
                "success": branding.success_color,
                "warning": branding.warning_color,
                "error": branding.error_color
            },
            "darkColors": {
                "bgPrimary": branding.dark_bg_color,
                "bgCard": branding.dark_card_color,
                "textPrimary": branding.dark_text_color
            },
            "fontFamily": branding.font_family,
            "headingFont": branding.heading_font,
            "footer": {
                "text": branding.footer_text,
                "links": branding.footer_links
            },
            "support": {
                "email": branding.support_email,
                "phone": branding.support_phone
            },
            "legal": {
                "termsUrl": branding.terms_url,
                "privacyUrl": branding.privacy_url
            },
            "showPoweredBy": branding.show_powered_by,
            "showVersion": branding.show_version
        }


# Singleton instance
white_label_service = WhiteLabelService()


# FastAPI Router
from fastapi import APIRouter, HTTPException

router = APIRouter()


@router.get("/branding/{company_id}")
async def get_branding(company_id: str):
    """Get company branding."""
    branding = await white_label_service.get_branding(UUID(company_id))
    return branding.model_dump()


@router.put("/branding/{company_id}")
async def update_branding(company_id: str, data: Dict[str, Any]):
    """Update company branding."""
    branding = await white_label_service.update_branding(UUID(company_id), data)
    return branding.model_dump()


@router.get("/branding/domain/{domain}")
async def get_branding_by_domain(domain: str):
    """Get branding by custom domain."""
    branding = await white_label_service.get_branding_by_domain(domain)
    if branding:
        return branding.model_dump()
    raise HTTPException(status_code=404, detail="Domain not configured")


@router.get("/branding/{company_id}/email")
async def get_email_branding(company_id: str):
    """Get email branding."""
    branding = await white_label_service.get_email_branding(UUID(company_id))
    return branding.model_dump()


@router.put("/branding/{company_id}/email")
async def update_email_branding(company_id: str, data: Dict[str, Any]):
    """Update email branding."""
    branding = await white_label_service.update_email_branding(UUID(company_id), data)
    return branding.model_dump()


@router.get("/branding/{company_id}/pdf")
async def get_pdf_branding(company_id: str):
    """Get PDF branding."""
    branding = await white_label_service.get_pdf_branding(UUID(company_id))
    return branding.model_dump()


@router.put("/branding/{company_id}/pdf")
async def update_pdf_branding(company_id: str, data: Dict[str, Any]):
    """Update PDF branding."""
    branding = await white_label_service.update_pdf_branding(UUID(company_id), data)
    return branding.model_dump()


@router.get("/branding/{company_id}/css")
async def get_css_variables(company_id: str):
    """Get CSS variables for company."""
    css = await white_label_service.generate_css_variables(UUID(company_id))
    return {"css": css}


@router.get("/branding/{company_id}/frontend-config")
async def get_frontend_config(company_id: str):
    """Get frontend configuration."""
    return await white_label_service.get_frontend_config(UUID(company_id))
