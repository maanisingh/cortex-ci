"""
EGRUL Web Scraper - Fetches company data from public sources.
No API keys required.

Sources:
1. list-org.com - Primary source
2. rusprofile.ru - Fallback
3. checko.ru - Secondary fallback
"""

import httpx
from bs4 import BeautifulSoup
from typing import Optional, Dict, Any
from datetime import datetime, date
import asyncio
import re
from fake_useragent import UserAgent
from tenacity import retry, stop_after_attempt, wait_exponential


class EgrulScraper:
    def __init__(self, delay: int = 2):
        self.delay = delay
        self.ua = UserAgent()
        self.last_request = datetime.now()

        # Source configurations
        self.sources = [
            {
                "name": "list-org",
                "url_template": "https://www.list-org.com/search?val={inn}",
                "parser": self._parse_list_org
            },
            {
                "name": "rusprofile",
                "url_template": "https://www.rusprofile.ru/search?query={inn}",
                "parser": self._parse_rusprofile
            }
        ]

    async def fetch_company(self, inn: str) -> Optional[Dict[str, Any]]:
        """
        Fetch company data by INN from public sources.
        Tries multiple sources until one succeeds.
        """
        for source in self.sources:
            try:
                result = await self._fetch_from_source(inn, source)
                if result:
                    result['source'] = f"scraped:{source['name']}"
                    return result
            except Exception as e:
                print(f"Error fetching from {source['name']}: {e}")
                continue

        return None

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(min=1, max=10))
    async def _fetch_from_source(
        self,
        inn: str,
        source: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """Fetch from a specific source with retry logic."""
        # Rate limiting
        elapsed = (datetime.now() - self.last_request).total_seconds()
        if elapsed < self.delay:
            await asyncio.sleep(self.delay - elapsed)

        url = source["url_template"].format(inn=inn)

        async with httpx.AsyncClient() as client:
            response = await client.get(
                url,
                headers={
                    "User-Agent": self.ua.random,
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "ru-RU,ru;q=0.9,en;q=0.8"
                },
                follow_redirects=True,
                timeout=30.0
            )
            self.last_request = datetime.now()

            if response.status_code == 200:
                return source["parser"](response.text, inn)

        return None

    def _parse_list_org(self, html: str, inn: str) -> Optional[Dict[str, Any]]:
        """Parse company data from list-org.com."""
        soup = BeautifulSoup(html, 'lxml')

        # Find company card
        company_card = soup.find('div', class_='org_list') or soup.find('table', class_='org_table')
        if not company_card:
            return None

        data = {"inn": inn}

        # Extract company name
        name_elem = soup.find('h1') or soup.find('a', class_='org_name')
        if name_elem:
            data['full_name'] = name_elem.get_text(strip=True)

        # Extract data from table rows
        for row in soup.find_all('tr'):
            cells = row.find_all('td')
            if len(cells) >= 2:
                label = cells[0].get_text(strip=True).lower()
                value = cells[1].get_text(strip=True)

                if 'огрн' in label:
                    data['ogrn'] = re.sub(r'\D', '', value)[:15]
                elif 'кпп' in label:
                    data['kpp'] = re.sub(r'\D', '', value)[:9]
                elif 'адрес' in label:
                    data['legal_address'] = value
                elif 'директор' in label or 'руководитель' in label:
                    data['director_name'] = value
                    data['director_position'] = 'Генеральный директор'
                elif 'дата регистрации' in label:
                    try:
                        data['registration_date'] = self._parse_date(value)
                    except:
                        pass
                elif 'оквэд' in label:
                    parts = value.split(' ', 1)
                    data['okved_main'] = parts[0]
                    if len(parts) > 1:
                        data['okved_main_name'] = parts[1]
                elif 'статус' in label:
                    if 'действ' in value.lower():
                        data['status'] = 'active'
                    elif 'ликвид' in value.lower():
                        data['status'] = 'liquidated'
                    else:
                        data['status'] = 'unknown'

        if 'full_name' in data:
            data['last_updated'] = datetime.now()
            return data

        return None

    def _parse_rusprofile(self, html: str, inn: str) -> Optional[Dict[str, Any]]:
        """Parse company data from rusprofile.ru."""
        soup = BeautifulSoup(html, 'lxml')

        data = {"inn": inn}

        # Company name
        name_elem = soup.find('h1', class_='company-name') or soup.find('div', class_='company-header')
        if name_elem:
            data['full_name'] = name_elem.get_text(strip=True)

        # Data items
        for item in soup.find_all('div', class_='company-info__item'):
            label_elem = item.find('span', class_='company-info__title')
            value_elem = item.find('span', class_='company-info__text')

            if label_elem and value_elem:
                label = label_elem.get_text(strip=True).lower()
                value = value_elem.get_text(strip=True)

                if 'огрн' in label:
                    data['ogrn'] = re.sub(r'\D', '', value)[:15]
                elif 'кпп' in label:
                    data['kpp'] = re.sub(r'\D', '', value)[:9]
                elif 'адрес' in label:
                    data['legal_address'] = value
                elif 'руководитель' in label:
                    data['director_name'] = value
                elif 'оквэд' in label:
                    parts = value.split(' ', 1)
                    data['okved_main'] = parts[0]

        if 'full_name' in data:
            data['last_updated'] = datetime.now()
            data['status'] = 'active'
            return data

        return None

    def _parse_date(self, date_str: str) -> Optional[date]:
        """Parse Russian date format."""
        # Try common formats
        formats = [
            '%d.%m.%Y',
            '%d/%m/%Y',
            '%Y-%m-%d',
            '%d %B %Y'
        ]

        # Russian month names
        ru_months = {
            'января': '01', 'февраля': '02', 'марта': '03',
            'апреля': '04', 'мая': '05', 'июня': '06',
            'июля': '07', 'августа': '08', 'сентября': '09',
            'октября': '10', 'ноября': '11', 'декабря': '12'
        }

        # Replace Russian month names
        for ru, num in ru_months.items():
            date_str = date_str.replace(ru, num)

        for fmt in formats:
            try:
                return datetime.strptime(date_str.strip(), fmt).date()
            except ValueError:
                continue

        return None
