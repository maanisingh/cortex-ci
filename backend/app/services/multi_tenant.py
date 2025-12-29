"""
Multi-Tenant / Multi-Company Management Service
Allows managing multiple legal entities under one account.

Features:
- Company hierarchy (parent/subsidiaries)
- Shared and isolated data
- Cross-company reporting
- Consolidated compliance dashboard
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class CompanyType(str, Enum):
    PARENT = "parent"           # Головная компания
    SUBSIDIARY = "subsidiary"   # Дочерняя компания
    BRANCH = "branch"           # Филиал
    AFFILIATE = "affiliate"     # Аффилированное лицо


class CompanyStatus(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    PENDING = "pending"
    SUSPENDED = "suspended"


class Company(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    parent_id: Optional[UUID] = None
    company_type: CompanyType = CompanyType.PARENT

    # Basic info
    inn: str
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    legal_name: str
    short_name: Optional[str] = None
    legal_address: Optional[str] = None
    actual_address: Optional[str] = None

    # Contact info
    phone: Optional[str] = None
    email: Optional[str] = None
    website: Optional[str] = None

    # Responsible persons
    director_name: Optional[str] = None
    director_position: str = "Генеральный директор"
    dpo_name: Optional[str] = None
    dpo_email: Optional[str] = None

    # Status
    status: CompanyStatus = CompanyStatus.ACTIVE
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Branding (white-label)
    logo_url: Optional[str] = None
    primary_color: str = "#2563eb"
    secondary_color: str = "#1e40af"


class CompanySettings(BaseModel):
    company_id: UUID
    timezone: str = "Europe/Moscow"
    language: str = "ru"
    date_format: str = "%d.%m.%Y"
    currency: str = "RUB"

    # Feature flags
    enable_gap_analysis: bool = True
    enable_audit_prep: bool = True
    enable_training: bool = True
    enable_incident_management: bool = True

    # Compliance frameworks
    enabled_frameworks: List[str] = ["152-FZ", "187-FZ", "GOST-57580"]

    # Notification settings
    email_notifications: bool = True
    push_notifications: bool = True
    reminder_days: List[int] = [7, 3, 1]

    # Data retention
    document_retention_years: int = 5
    audit_log_retention_years: int = 10


class MultiTenantService:
    """
    Service for managing multiple companies.
    """

    def __init__(self):
        # In-memory storage for demo (replace with database in production)
        self.companies: Dict[UUID, Company] = {}
        self.settings: Dict[UUID, CompanySettings] = {}
        self.user_company_access: Dict[str, List[UUID]] = {}  # user_id -> company_ids

    # ==========================================================================
    # Company CRUD
    # ==========================================================================

    async def create_company(
        self,
        data: Dict[str, Any],
        parent_id: Optional[UUID] = None
    ) -> Company:
        """Create a new company."""
        company = Company(
            parent_id=parent_id,
            company_type=CompanyType.SUBSIDIARY if parent_id else CompanyType.PARENT,
            **data
        )
        self.companies[company.id] = company

        # Create default settings
        settings = CompanySettings(company_id=company.id)
        self.settings[company.id] = settings

        return company

    async def get_company(self, company_id: UUID) -> Optional[Company]:
        """Get company by ID."""
        return self.companies.get(company_id)

    async def update_company(
        self,
        company_id: UUID,
        data: Dict[str, Any]
    ) -> Optional[Company]:
        """Update company details."""
        company = self.companies.get(company_id)
        if company:
            for key, value in data.items():
                if hasattr(company, key):
                    setattr(company, key, value)
            company.updated_at = datetime.utcnow()
            self.companies[company_id] = company
            return company
        return None

    async def delete_company(self, company_id: UUID) -> bool:
        """Delete a company (soft delete - set to inactive)."""
        company = self.companies.get(company_id)
        if company:
            company.status = CompanyStatus.INACTIVE
            company.updated_at = datetime.utcnow()
            return True
        return False

    async def list_companies(
        self,
        parent_id: Optional[UUID] = None,
        status: Optional[CompanyStatus] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Company]:
        """List companies with optional filters."""
        companies = list(self.companies.values())

        if parent_id:
            companies = [c for c in companies if c.parent_id == parent_id]
        if status:
            companies = [c for c in companies if c.status == status]

        return companies[offset:offset + limit]

    # ==========================================================================
    # Company Hierarchy
    # ==========================================================================

    async def get_company_tree(self, root_id: UUID) -> Dict[str, Any]:
        """Get company hierarchy tree."""
        company = self.companies.get(root_id)
        if not company:
            return {}

        children = [
            await self.get_company_tree(c.id)
            for c in self.companies.values()
            if c.parent_id == root_id
        ]

        return {
            "company": company.model_dump(),
            "children": children
        }

    async def get_subsidiaries(self, parent_id: UUID) -> List[Company]:
        """Get all subsidiaries of a parent company."""
        return [
            c for c in self.companies.values()
            if c.parent_id == parent_id and c.status == CompanyStatus.ACTIVE
        ]

    async def get_parent_company(self, company_id: UUID) -> Optional[Company]:
        """Get parent company."""
        company = self.companies.get(company_id)
        if company and company.parent_id:
            return self.companies.get(company.parent_id)
        return None

    # ==========================================================================
    # User Access
    # ==========================================================================

    async def grant_access(self, user_id: str, company_id: UUID) -> bool:
        """Grant user access to a company."""
        if user_id not in self.user_company_access:
            self.user_company_access[user_id] = []

        if company_id not in self.user_company_access[user_id]:
            self.user_company_access[user_id].append(company_id)
        return True

    async def revoke_access(self, user_id: str, company_id: UUID) -> bool:
        """Revoke user access to a company."""
        if user_id in self.user_company_access:
            if company_id in self.user_company_access[user_id]:
                self.user_company_access[user_id].remove(company_id)
                return True
        return False

    async def get_user_companies(self, user_id: str) -> List[Company]:
        """Get all companies a user has access to."""
        company_ids = self.user_company_access.get(user_id, [])
        return [
            self.companies[cid]
            for cid in company_ids
            if cid in self.companies
        ]

    async def check_access(self, user_id: str, company_id: UUID) -> bool:
        """Check if user has access to a company."""
        company_ids = self.user_company_access.get(user_id, [])
        return company_id in company_ids

    # ==========================================================================
    # Settings
    # ==========================================================================

    async def get_settings(self, company_id: UUID) -> Optional[CompanySettings]:
        """Get company settings."""
        return self.settings.get(company_id)

    async def update_settings(
        self,
        company_id: UUID,
        data: Dict[str, Any]
    ) -> Optional[CompanySettings]:
        """Update company settings."""
        settings = self.settings.get(company_id)
        if settings:
            for key, value in data.items():
                if hasattr(settings, key):
                    setattr(settings, key, value)
            self.settings[company_id] = settings
            return settings
        return None

    # ==========================================================================
    # Consolidated Reporting
    # ==========================================================================

    async def get_consolidated_compliance(
        self,
        parent_id: UUID
    ) -> Dict[str, Any]:
        """Get consolidated compliance status for all subsidiaries."""
        companies = await self.get_subsidiaries(parent_id)
        companies.insert(0, self.companies[parent_id])  # Include parent

        # In production, this would aggregate real compliance data
        return {
            "total_companies": len(companies),
            "companies": [
                {
                    "id": str(c.id),
                    "name": c.legal_name,
                    "compliance_score": 85.0,  # Placeholder
                    "frameworks": {
                        "152-FZ": {"score": 90, "controls": 45, "gaps": 5},
                        "187-FZ": {"score": 80, "controls": 30, "gaps": 8},
                    }
                }
                for c in companies
            ],
            "overall_score": 85.0,
            "total_controls": 150,
            "total_gaps": 20
        }


# Singleton instance
multi_tenant_service = MultiTenantService()


# FastAPI Router
from fastapi import APIRouter, HTTPException, Depends
from uuid import UUID

router = APIRouter()


@router.post("/companies")
async def create_company(
    data: Dict[str, Any],
    parent_id: Optional[str] = None
):
    """Create a new company."""
    parent_uuid = UUID(parent_id) if parent_id else None
    company = await multi_tenant_service.create_company(data, parent_uuid)
    return company


@router.get("/companies")
async def list_companies(
    parent_id: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = 50,
    offset: int = 0
):
    """List all companies."""
    parent_uuid = UUID(parent_id) if parent_id else None
    status_enum = CompanyStatus(status) if status else None

    companies = await multi_tenant_service.list_companies(
        parent_id=parent_uuid,
        status=status_enum,
        limit=limit,
        offset=offset
    )
    return {"companies": companies}


@router.get("/companies/{company_id}")
async def get_company(company_id: str):
    """Get company by ID."""
    company = await multi_tenant_service.get_company(UUID(company_id))
    if company:
        return company
    raise HTTPException(status_code=404, detail="Company not found")


@router.put("/companies/{company_id}")
async def update_company(company_id: str, data: Dict[str, Any]):
    """Update company details."""
    company = await multi_tenant_service.update_company(UUID(company_id), data)
    if company:
        return company
    raise HTTPException(status_code=404, detail="Company not found")


@router.delete("/companies/{company_id}")
async def delete_company(company_id: str):
    """Delete a company."""
    success = await multi_tenant_service.delete_company(UUID(company_id))
    if success:
        return {"status": "deleted"}
    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/companies/{company_id}/tree")
async def get_company_tree(company_id: str):
    """Get company hierarchy tree."""
    tree = await multi_tenant_service.get_company_tree(UUID(company_id))
    if tree:
        return tree
    raise HTTPException(status_code=404, detail="Company not found")


@router.get("/companies/{company_id}/subsidiaries")
async def get_subsidiaries(company_id: str):
    """Get all subsidiaries."""
    subsidiaries = await multi_tenant_service.get_subsidiaries(UUID(company_id))
    return {"subsidiaries": subsidiaries}


@router.get("/companies/{company_id}/settings")
async def get_company_settings(company_id: str):
    """Get company settings."""
    settings = await multi_tenant_service.get_settings(UUID(company_id))
    if settings:
        return settings
    raise HTTPException(status_code=404, detail="Settings not found")


@router.put("/companies/{company_id}/settings")
async def update_company_settings(company_id: str, data: Dict[str, Any]):
    """Update company settings."""
    settings = await multi_tenant_service.update_settings(UUID(company_id), data)
    if settings:
        return settings
    raise HTTPException(status_code=404, detail="Settings not found")


@router.get("/companies/{company_id}/consolidated-compliance")
async def get_consolidated_compliance(company_id: str):
    """Get consolidated compliance for company group."""
    return await multi_tenant_service.get_consolidated_compliance(UUID(company_id))
