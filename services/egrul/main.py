"""
EGRUL Data Service - Russian Company Registry
Provides company data lookup via:
1. Local PostgreSQL cache (fastest)
2. Web scraping from public sources (fallback)
3. Bulk data import from data.gov.ru dumps

No API signup required - fully self-contained.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
from typing import Optional, List
from datetime import datetime, date
import asyncio
import json
import re

from database import Database
from scraper import EgrulScraper
from bulk_importer import BulkImporter

class Settings(BaseSettings):
    database_url: str = "postgresql://postgres:postgres@localhost:5432/egrul_cache"
    redis_url: str = "redis://localhost:6379/1"
    scrape_delay: int = 2  # seconds between scrape requests

    class Config:
        env_file = ".env"

settings = Settings()
app = FastAPI(
    title="EGRUL Data Service",
    description="Russian company registry data without API signup",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
db = Database(settings.database_url)
scraper = EgrulScraper(delay=settings.scrape_delay)
importer = BulkImporter(db)


# =============================================================================
# Models
# =============================================================================

class CompanyBase(BaseModel):
    inn: str = Field(..., description="INN (10 or 12 digits)")

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
    status: str = "active"  # active, liquidating, liquidated
    okved_main: Optional[str] = None
    okved_main_name: Optional[str] = None
    authorized_capital: Optional[float] = None
    employee_count: Optional[str] = None
    last_updated: datetime
    source: str = "cache"  # cache, scraped, bulk_import

class CompanySearchResult(BaseModel):
    total: int
    companies: List[CompanyInfo]

class BulkImportStatus(BaseModel):
    status: str
    total_records: int
    imported: int
    errors: int
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


# =============================================================================
# Endpoints
# =============================================================================

@app.on_event("startup")
async def startup():
    await db.connect()
    await db.create_tables()

@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "egrul"}


@app.get("/api/company/{inn}", response_model=CompanyInfo)
async def get_company_by_inn(inn: str, force_refresh: bool = False):
    """
    Get company info by INN.

    1. First checks local cache
    2. If not found or force_refresh, scrapes from public sources
    3. Caches result for future requests
    """
    # Validate INN format
    if not re.match(r'^\d{10}$|^\d{12}$', inn):
        raise HTTPException(status_code=400, detail="Invalid INN format. Must be 10 or 12 digits.")

    # Check cache first
    if not force_refresh:
        cached = await db.get_company(inn)
        if cached:
            return cached

    # Scrape from public sources
    try:
        company_data = await scraper.fetch_company(inn)
        if company_data:
            # Cache the result
            await db.save_company(company_data)
            return company_data
    except Exception as e:
        # If scraping fails, check if we have stale cache
        cached = await db.get_company(inn)
        if cached:
            return cached
        raise HTTPException(status_code=404, detail=f"Company not found: {inn}")

    raise HTTPException(status_code=404, detail=f"Company not found: {inn}")


@app.get("/api/search", response_model=CompanySearchResult)
async def search_companies(
    q: str,
    limit: int = 20,
    offset: int = 0
):
    """
    Search companies by name, INN, or OGRN.
    Only searches local cache - does not scrape.
    """
    if len(q) < 3:
        raise HTTPException(status_code=400, detail="Query must be at least 3 characters")

    companies = await db.search_companies(q, limit=limit, offset=offset)
    total = await db.count_search_results(q)

    return CompanySearchResult(total=total, companies=companies)


@app.post("/api/bulk-import/start")
async def start_bulk_import(
    background_tasks: BackgroundTasks,
    source_url: Optional[str] = None
):
    """
    Start bulk import from data.gov.ru EGRUL dump.

    Default source: https://data.gov.ru/opendata/7707329152-egrul

    This runs in background and can import millions of records.
    """
    if importer.is_running:
        raise HTTPException(status_code=409, detail="Import already in progress")

    background_tasks.add_task(importer.import_from_dump, source_url)

    return {"status": "started", "message": "Bulk import started in background"}


@app.get("/api/bulk-import/status", response_model=BulkImportStatus)
async def get_import_status():
    """Get status of current or last bulk import."""
    return importer.get_status()


@app.get("/api/stats")
async def get_stats():
    """Get database statistics."""
    stats = await db.get_stats()
    return {
        "total_companies": stats["total"],
        "active_companies": stats["active"],
        "last_import": stats["last_import"],
        "cache_size_mb": stats["size_mb"]
    }


# =============================================================================
# Batch Operations
# =============================================================================

@app.post("/api/batch/lookup")
async def batch_lookup(inns: List[str]):
    """
    Look up multiple companies by INN.
    Returns cached results immediately, queues missing for scraping.
    """
    results = []
    missing = []

    for inn in inns[:100]:  # Limit to 100 per request
        cached = await db.get_company(inn)
        if cached:
            results.append(cached)
        else:
            missing.append(inn)

    return {
        "found": results,
        "missing": missing,
        "message": f"Found {len(results)} in cache. {len(missing)} will need scraping."
    }
