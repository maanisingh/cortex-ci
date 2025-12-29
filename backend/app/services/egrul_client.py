"""
EGRUL Client - Interface to the EGRUL data service.
Fetches Russian company data from the local EGRUL service.
"""

import os
import httpx
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import date, datetime
from functools import lru_cache

# EGRUL Service Configuration
EGRUL_SERVICE_URL = os.getenv("EGRUL_SERVICE_URL", "http://localhost:8200")


class CompanyInfo(BaseModel):
    inn: str
    ogrn: Optional[str] = None
    kpp: Optional[str] = None
    full_name: str
    short_name: Optional[str] = None
    legal_address: Optional[str] = None
    registration_date: Optional[date] = None
    director_name: Optional[str] = None
    director_position: Optional[str] = None
    status: str = "active"
    okved_main: Optional[str] = None
    okved_main_name: Optional[str] = None
    authorized_capital: Optional[float] = None
    employee_count: Optional[str] = None
    last_updated: Optional[datetime] = None
    source: str = "cache"


class EgrulClient:
    """
    Client for EGRUL data service.

    Provides company data lookup via:
    1. Local cache (PostgreSQL)
    2. Web scraping (fallback)
    3. Bulk data import from data.gov.ru
    """

    def __init__(self, base_url: str = EGRUL_SERVICE_URL):
        self.base_url = base_url.rstrip("/")

    async def get_company(
        self,
        inn: str,
        force_refresh: bool = False
    ) -> Optional[CompanyInfo]:
        """
        Get company information by INN.

        Args:
            inn: Company INN (10 or 12 digits)
            force_refresh: If True, fetch fresh data instead of cache

        Returns:
            CompanyInfo or None if not found
        """
        try:
            params = {"force_refresh": force_refresh}

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/company/{inn}",
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return CompanyInfo(**data)
                elif response.status_code == 404:
                    return None
                else:
                    print(f"EGRUL service error: {response.status_code}")
                    return None

        except Exception as e:
            print(f"Failed to fetch company data: {e}")
            return None

    async def search_companies(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> Dict[str, Any]:
        """
        Search companies by name, INN, or OGRN.

        Args:
            query: Search query (min 3 characters)
            limit: Max results to return
            offset: Pagination offset

        Returns:
            Dict with total count and list of companies
        """
        try:
            params = {
                "q": query,
                "limit": limit,
                "offset": offset
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/search",
                    params=params,
                    timeout=30.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "total": data.get("total", 0),
                        "companies": [
                            CompanyInfo(**c) for c in data.get("companies", [])
                        ]
                    }

        except Exception as e:
            print(f"Failed to search companies: {e}")

        return {"total": 0, "companies": []}

    async def batch_lookup(self, inns: List[str]) -> Dict[str, Any]:
        """
        Look up multiple companies by INN.

        Args:
            inns: List of INNs to look up

        Returns:
            Dict with found companies and missing INNs
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/batch/lookup",
                    json=inns,
                    timeout=60.0
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "found": [CompanyInfo(**c) for c in data.get("found", [])],
                        "missing": data.get("missing", [])
                    }

        except Exception as e:
            print(f"Failed batch lookup: {e}")

        return {"found": [], "missing": inns}

    async def start_bulk_import(self, source_url: Optional[str] = None) -> bool:
        """Start bulk import from EGRUL dump."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/api/bulk-import/start",
                    params={"source_url": source_url} if source_url else {},
                    timeout=10.0
                )
                return response.status_code == 200

        except Exception as e:
            print(f"Failed to start bulk import: {e}")
            return False

    async def get_import_status(self) -> Dict[str, Any]:
        """Get status of bulk import."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/bulk-import/status",
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            print(f"Failed to get import status: {e}")

        return {"status": "unknown"}

    async def get_stats(self) -> Dict[str, Any]:
        """Get EGRUL database statistics."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/api/stats",
                    timeout=10.0
                )

                if response.status_code == 200:
                    return response.json()

        except Exception as e:
            print(f"Failed to get stats: {e}")

        return {}

    async def health_check(self) -> bool:
        """Check if EGRUL service is healthy."""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/health",
                    timeout=5.0
                )
                return response.status_code == 200

        except Exception:
            return False


# Singleton instance
egrul_client = EgrulClient()


# FastAPI Router
from fastapi import APIRouter, HTTPException, Query

router = APIRouter()


@router.get("/company/{inn}")
async def get_company(
    inn: str,
    force_refresh: bool = False
):
    """Get company by INN."""
    company = await egrul_client.get_company(inn, force_refresh)
    if company:
        return company
    raise HTTPException(status_code=404, detail=f"Company not found: {inn}")


@router.get("/search")
async def search_companies(
    q: str = Query(..., min_length=3, description="Search query"),
    limit: int = 20,
    offset: int = 0
):
    """Search companies."""
    return await egrul_client.search_companies(q, limit, offset)


@router.post("/batch-lookup")
async def batch_lookup(inns: List[str]):
    """Batch lookup companies by INN."""
    return await egrul_client.batch_lookup(inns)


@router.get("/stats")
async def get_stats():
    """Get EGRUL database statistics."""
    return await egrul_client.get_stats()


@router.post("/import/start")
async def start_import(source_url: Optional[str] = None):
    """Start bulk data import."""
    success = await egrul_client.start_bulk_import(source_url)
    if success:
        return {"status": "started"}
    raise HTTPException(status_code=500, detail="Failed to start import")


@router.get("/import/status")
async def get_import_status():
    """Get import status."""
    return await egrul_client.get_import_status()


@router.get("/health")
async def health_check():
    """Check EGRUL service health."""
    healthy = await egrul_client.health_check()
    if healthy:
        return {"status": "healthy"}
    raise HTTPException(status_code=503, detail="EGRUL service unavailable")
