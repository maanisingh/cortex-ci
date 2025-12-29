"""
EGRUL Scraper Service
Scrapes company data from public sources like Rusprofile.ru
"""

import asyncio
import logging
import re
from datetime import datetime
from typing import Any

import httpx
from bs4 import BeautifulSoup
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.compliance.egrul import (
    CompanyStatus,
    DataSource,
    EGRULCompany,
    EGRULFetchLog,
)

logger = logging.getLogger(__name__)

# Rate limiting
MIN_REQUEST_INTERVAL = 2.0  # seconds between requests


class EGRULScraperService:
    """Service for scraping EGRUL company data from public sources."""

    RUSPROFILE_BASE_URL = "https://www.rusprofile.ru"
    RUSPROFILE_SEARCH_URL = "https://www.rusprofile.ru/search?query={inn}"

    # User agent to avoid blocks
    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Accept-Language": "ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7",
    }

    def __init__(self, db: AsyncSession):
        self.db = db
        self._last_request_time: float = 0

    async def _rate_limit(self) -> None:
        """Ensure minimum time between requests."""
        now = asyncio.get_event_loop().time()
        elapsed = now - self._last_request_time
        if elapsed < MIN_REQUEST_INTERVAL:
            await asyncio.sleep(MIN_REQUEST_INTERVAL - elapsed)
        self._last_request_time = asyncio.get_event_loop().time()

    async def fetch_company_by_inn(
        self,
        inn: str,
        force_refresh: bool = False,
    ) -> EGRULCompany | None:
        """
        Fetch company data by INN.
        First checks cache, then scrapes if needed.

        Args:
            inn: Company INN (10 or 12 digits)
            force_refresh: If True, always scrape fresh data

        Returns:
            EGRULCompany or None if not found
        """
        # Validate INN
        inn = inn.strip()
        if not re.match(r"^\d{10}$|^\d{12}$", inn):
            logger.warning(f"Invalid INN format: {inn}")
            return None

        # Check cache first
        if not force_refresh:
            cached = await self._get_cached_company(inn)
            if cached and not cached.needs_refresh:
                logger.info(f"Using cached data for INN {inn}")
                return cached

        # Scrape fresh data
        logger.info(f"Scraping data for INN {inn}")
        company_data = await self._scrape_rusprofile(inn)

        if company_data:
            return await self._save_company(inn, company_data)

        return None

    async def _get_cached_company(self, inn: str) -> EGRULCompany | None:
        """Get company from cache."""
        result = await self.db.execute(
            select(EGRULCompany).where(EGRULCompany.inn == inn)
        )
        return result.scalar_one_or_none()

    async def _scrape_rusprofile(self, inn: str) -> dict[str, Any] | None:
        """Scrape company data from Rusprofile.ru."""
        await self._rate_limit()

        start_time = datetime.utcnow()
        log_entry = EGRULFetchLog(
            inn=inn,
            source=DataSource.RUSPROFILE.value,
            success=False,
        )

        try:
            async with httpx.AsyncClient(
                headers=self.HEADERS,
                follow_redirects=True,
                timeout=30.0,
            ) as client:
                # Search for company
                search_url = self.RUSPROFILE_SEARCH_URL.format(inn=inn)
                response = await client.get(search_url)

                log_entry.response_code = response.status_code
                log_entry.response_time_ms = int(
                    (datetime.utcnow() - start_time).total_seconds() * 1000
                )

                if response.status_code != 200:
                    log_entry.error_message = f"HTTP {response.status_code}"
                    await self._save_log(log_entry)
                    return None

                # Parse HTML
                soup = BeautifulSoup(response.text, "lxml")
                data = self._parse_rusprofile_page(soup, inn)

                if data:
                    log_entry.success = True
                    log_entry.company_found = True
                    log_entry.company_name = data.get("full_name", "")[:500]
                else:
                    log_entry.error_message = "Company not found in response"

                await self._save_log(log_entry)
                return data

        except httpx.TimeoutException:
            log_entry.error_message = "Request timeout"
            await self._save_log(log_entry)
            logger.warning(f"Timeout fetching INN {inn}")
            return None

        except Exception as e:
            log_entry.error_message = str(e)[:500]
            await self._save_log(log_entry)
            logger.exception(f"Error fetching INN {inn}")
            return None

    def _parse_rusprofile_page(
        self, soup: BeautifulSoup, inn: str
    ) -> dict[str, Any] | None:
        """Parse Rusprofile search results page."""
        data: dict[str, Any] = {"inn": inn}

        try:
            # Check if we're on a company page or search results
            # Look for company card
            company_card = soup.find("div", class_="company-row") or soup.find(
                "div", class_="main-company-info"
            )

            if not company_card:
                # Try direct company page elements
                title_elem = soup.find("h1", class_="company-name") or soup.find(
                    "div", class_="company-title"
                )
                if not title_elem:
                    return None

            # Extract company name
            name_elem = (
                soup.find("h1", class_="company-name")
                or soup.find("a", class_="company-name")
                or soup.find("span", class_="company-name")
            )
            if name_elem:
                data["full_name"] = name_elem.get_text(strip=True)

            # Short name (often in title or separate element)
            short_name_elem = soup.find("div", class_="company-short-name")
            if short_name_elem:
                data["short_name"] = short_name_elem.get_text(strip=True)

            # Find info blocks
            info_blocks = soup.find_all("div", class_="info-row") or soup.find_all(
                "dl", class_="company-info"
            )

            for block in info_blocks:
                label = block.find("dt") or block.find("span", class_="label")
                value = block.find("dd") or block.find("span", class_="value")

                if not label or not value:
                    continue

                label_text = label.get_text(strip=True).lower()
                value_text = value.get_text(strip=True)

                if "инн" in label_text:
                    data["inn"] = re.sub(r"\D", "", value_text)[:12]
                elif "огрн" in label_text:
                    data["ogrn"] = re.sub(r"\D", "", value_text)[:15]
                elif "кпп" in label_text:
                    data["kpp"] = re.sub(r"\D", "", value_text)[:9]
                elif "оквэд" in label_text and "основной" in label_text:
                    # Extract OKVED code and name
                    okved_match = re.match(r"([\d.]+)\s*(.*)", value_text)
                    if okved_match:
                        data["okved_main"] = okved_match.group(1)
                        data["okved_main_name"] = okved_match.group(2).strip()
                elif "адрес" in label_text:
                    data["legal_address"] = value_text
                elif "директор" in label_text or "руководитель" in label_text:
                    data["director_name"] = value_text
                elif "капитал" in label_text:
                    # Extract numeric value
                    amount = re.sub(r"[^\d]", "", value_text)
                    if amount:
                        data["authorized_capital"] = int(amount)
                elif "регистрац" in label_text and "дата" in label_text:
                    # Try to parse date
                    date_match = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", value_text)
                    if date_match:
                        try:
                            data["registration_date"] = datetime(
                                int(date_match.group(3)),
                                int(date_match.group(2)),
                                int(date_match.group(1)),
                            )
                        except ValueError:
                            pass
                elif "статус" in label_text:
                    status_text = value_text.lower()
                    if "действу" in status_text:
                        data["status"] = CompanyStatus.ACTIVE.value
                    elif "ликвид" in status_text:
                        if "процесс" in status_text:
                            data["status"] = CompanyStatus.LIQUIDATING.value
                        else:
                            data["status"] = CompanyStatus.LIQUIDATED.value
                    elif "банкрот" in status_text:
                        data["status"] = CompanyStatus.BANKRUPT.value

            # Extract legal form from name
            name = data.get("full_name", "")
            if name.startswith("ООО") or "ОБЩЕСТВО С ОГРАНИЧЕННОЙ" in name.upper():
                data["legal_form"] = "ООО"
            elif name.startswith("АО") or "АКЦИОНЕРНОЕ ОБЩЕСТВО" in name.upper():
                data["legal_form"] = "АО"
            elif name.startswith("ПАО"):
                data["legal_form"] = "ПАО"
            elif name.startswith("ИП") or len(inn) == 12:
                data["legal_form"] = "ИП"
            elif name.startswith("ЗАО"):
                data["legal_form"] = "ЗАО"

            # Set source info
            data["source"] = DataSource.RUSPROFILE.value
            data["source_url"] = f"{self.RUSPROFILE_BASE_URL}/search?query={inn}"

            return data if data.get("full_name") else None

        except Exception as e:
            logger.exception(f"Error parsing Rusprofile page for INN {inn}")
            return None

    async def _save_company(
        self, inn: str, data: dict[str, Any]
    ) -> EGRULCompany | None:
        """Save or update company in database."""
        try:
            # Check if exists
            existing = await self._get_cached_company(inn)

            if existing:
                # Update existing record
                for key, value in data.items():
                    if hasattr(existing, key) and value is not None:
                        setattr(existing, key, value)
                existing.last_fetched = datetime.utcnow()
                existing.is_stale = False
                existing.last_error = None
                company = existing
            else:
                # Create new record
                company = EGRULCompany(
                    inn=inn,
                    last_fetched=datetime.utcnow(),
                    **{k: v for k, v in data.items() if k != "inn" and v is not None},
                )
                self.db.add(company)

            await self.db.commit()
            await self.db.refresh(company)
            return company

        except Exception as e:
            logger.exception(f"Error saving company {inn}")
            await self.db.rollback()
            return None

    async def _save_log(self, log_entry: EGRULFetchLog) -> None:
        """Save fetch log entry."""
        try:
            self.db.add(log_entry)
            await self.db.commit()
        except Exception:
            await self.db.rollback()

    async def refresh_stale_companies(self, limit: int = 100) -> int:
        """Refresh companies with stale data."""
        result = await self.db.execute(
            select(EGRULCompany)
            .where(EGRULCompany.is_stale == True)
            .limit(limit)
        )
        stale_companies = result.scalars().all()

        refreshed = 0
        for company in stale_companies:
            try:
                await self.fetch_company_by_inn(company.inn, force_refresh=True)
                refreshed += 1
            except Exception as e:
                logger.warning(f"Failed to refresh {company.inn}: {e}")

        return refreshed

    async def mark_old_entries_stale(self, days: int = 7) -> int:
        """Mark entries older than N days as stale."""
        from datetime import timedelta

        from sqlalchemy import update

        cutoff = datetime.utcnow() - timedelta(days=days)

        result = await self.db.execute(
            update(EGRULCompany)
            .where(
                EGRULCompany.last_fetched < cutoff,
                EGRULCompany.is_stale == False,
            )
            .values(is_stale=True)
        )
        await self.db.commit()

        return result.rowcount


# Factory function for dependency injection
async def get_egrul_service(db: AsyncSession) -> EGRULScraperService:
    """Create EGRUL scraper service instance."""
    return EGRULScraperService(db)
