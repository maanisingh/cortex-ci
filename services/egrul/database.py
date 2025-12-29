"""
Database layer for EGRUL cache.
Uses PostgreSQL for persistent storage.
"""

import asyncpg
from typing import Optional, List, Dict, Any
from datetime import datetime
import json


class Database:
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.pool: Optional[asyncpg.Pool] = None

    async def connect(self):
        self.pool = await asyncpg.create_pool(
            self.database_url,
            min_size=2,
            max_size=10
        )

    async def disconnect(self):
        if self.pool:
            await self.pool.close()

    async def create_tables(self):
        """Create database tables if they don't exist."""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS companies (
                    inn VARCHAR(12) PRIMARY KEY,
                    ogrn VARCHAR(15),
                    kpp VARCHAR(9),
                    full_name TEXT NOT NULL,
                    short_name VARCHAR(500),
                    legal_address TEXT,
                    registration_date DATE,
                    director_name VARCHAR(500),
                    director_position VARCHAR(200),
                    status VARCHAR(50) DEFAULT 'active',
                    okved_main VARCHAR(20),
                    okved_main_name VARCHAR(500),
                    authorized_capital DECIMAL(18,2),
                    employee_count VARCHAR(50),
                    raw_data JSONB,
                    source VARCHAR(50) DEFAULT 'scraped',
                    created_at TIMESTAMP DEFAULT NOW(),
                    updated_at TIMESTAMP DEFAULT NOW()
                );

                CREATE INDEX IF NOT EXISTS idx_companies_ogrn ON companies(ogrn);
                CREATE INDEX IF NOT EXISTS idx_companies_name ON companies USING gin(to_tsvector('russian', full_name));
                CREATE INDEX IF NOT EXISTS idx_companies_status ON companies(status);
                CREATE INDEX IF NOT EXISTS idx_companies_updated ON companies(updated_at);
            ''')

            await conn.execute('''
                CREATE TABLE IF NOT EXISTS import_logs (
                    id SERIAL PRIMARY KEY,
                    source_url TEXT,
                    status VARCHAR(50),
                    total_records INTEGER DEFAULT 0,
                    imported INTEGER DEFAULT 0,
                    errors INTEGER DEFAULT 0,
                    error_details JSONB,
                    started_at TIMESTAMP,
                    completed_at TIMESTAMP
                );
            ''')

    async def get_company(self, inn: str) -> Optional[Dict[str, Any]]:
        """Get company by INN from cache."""
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                'SELECT * FROM companies WHERE inn = $1',
                inn
            )
            if row:
                return self._row_to_dict(row)
            return None

    async def save_company(self, company: Dict[str, Any]) -> bool:
        """Save or update company in cache."""
        async with self.pool.acquire() as conn:
            await conn.execute('''
                INSERT INTO companies (
                    inn, ogrn, kpp, full_name, short_name, legal_address,
                    registration_date, director_name, director_position, status,
                    okved_main, okved_main_name, authorized_capital, employee_count,
                    source, updated_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, NOW())
                ON CONFLICT (inn) DO UPDATE SET
                    ogrn = EXCLUDED.ogrn,
                    kpp = EXCLUDED.kpp,
                    full_name = EXCLUDED.full_name,
                    short_name = EXCLUDED.short_name,
                    legal_address = EXCLUDED.legal_address,
                    registration_date = EXCLUDED.registration_date,
                    director_name = EXCLUDED.director_name,
                    director_position = EXCLUDED.director_position,
                    status = EXCLUDED.status,
                    okved_main = EXCLUDED.okved_main,
                    okved_main_name = EXCLUDED.okved_main_name,
                    authorized_capital = EXCLUDED.authorized_capital,
                    employee_count = EXCLUDED.employee_count,
                    source = EXCLUDED.source,
                    updated_at = NOW()
            ''',
                company.get('inn'),
                company.get('ogrn'),
                company.get('kpp'),
                company.get('full_name'),
                company.get('short_name'),
                company.get('legal_address'),
                company.get('registration_date'),
                company.get('director_name'),
                company.get('director_position'),
                company.get('status', 'active'),
                company.get('okved_main'),
                company.get('okved_main_name'),
                company.get('authorized_capital'),
                company.get('employee_count'),
                company.get('source', 'scraped')
            )
            return True

    async def search_companies(
        self,
        query: str,
        limit: int = 20,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Search companies by name, INN, or OGRN."""
        async with self.pool.acquire() as conn:
            # Check if query is INN/OGRN (digits only)
            if query.isdigit():
                rows = await conn.fetch('''
                    SELECT * FROM companies
                    WHERE inn LIKE $1 OR ogrn LIKE $1
                    ORDER BY updated_at DESC
                    LIMIT $2 OFFSET $3
                ''', f'{query}%', limit, offset)
            else:
                # Full-text search on name
                rows = await conn.fetch('''
                    SELECT * FROM companies
                    WHERE to_tsvector('russian', full_name) @@ plainto_tsquery('russian', $1)
                       OR full_name ILIKE $2
                    ORDER BY updated_at DESC
                    LIMIT $3 OFFSET $4
                ''', query, f'%{query}%', limit, offset)

            return [self._row_to_dict(row) for row in rows]

    async def count_search_results(self, query: str) -> int:
        """Count total search results."""
        async with self.pool.acquire() as conn:
            if query.isdigit():
                result = await conn.fetchval('''
                    SELECT COUNT(*) FROM companies
                    WHERE inn LIKE $1 OR ogrn LIKE $1
                ''', f'{query}%')
            else:
                result = await conn.fetchval('''
                    SELECT COUNT(*) FROM companies
                    WHERE to_tsvector('russian', full_name) @@ plainto_tsquery('russian', $1)
                       OR full_name ILIKE $2
                ''', query, f'%{query}%')
            return result or 0

    async def get_stats(self) -> Dict[str, Any]:
        """Get database statistics."""
        async with self.pool.acquire() as conn:
            total = await conn.fetchval('SELECT COUNT(*) FROM companies')
            active = await conn.fetchval(
                "SELECT COUNT(*) FROM companies WHERE status = 'active'"
            )
            last_import = await conn.fetchrow('''
                SELECT completed_at, imported FROM import_logs
                WHERE status = 'completed'
                ORDER BY completed_at DESC LIMIT 1
            ''')
            size = await conn.fetchval('''
                SELECT pg_size_pretty(pg_total_relation_size('companies'))
            ''')

            return {
                "total": total or 0,
                "active": active or 0,
                "last_import": last_import['completed_at'] if last_import else None,
                "size_mb": size or "0 bytes"
            }

    async def bulk_insert(self, companies: List[Dict[str, Any]]) -> int:
        """Bulk insert companies for import."""
        if not companies:
            return 0

        async with self.pool.acquire() as conn:
            # Use COPY for fast bulk insert
            inserted = 0
            for company in companies:
                try:
                    await conn.execute('''
                        INSERT INTO companies (
                            inn, ogrn, kpp, full_name, short_name, legal_address,
                            registration_date, status, source, updated_at
                        ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, 'bulk_import', NOW())
                        ON CONFLICT (inn) DO NOTHING
                    ''',
                        company.get('inn'),
                        company.get('ogrn'),
                        company.get('kpp'),
                        company.get('full_name'),
                        company.get('short_name'),
                        company.get('legal_address'),
                        company.get('registration_date'),
                        company.get('status', 'active')
                    )
                    inserted += 1
                except Exception:
                    pass
            return inserted

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """Convert database row to dictionary."""
        return {
            "inn": row['inn'],
            "ogrn": row['ogrn'],
            "kpp": row['kpp'],
            "full_name": row['full_name'],
            "short_name": row['short_name'],
            "legal_address": row['legal_address'],
            "registration_date": row['registration_date'],
            "director_name": row['director_name'],
            "director_position": row['director_position'],
            "status": row['status'],
            "okved_main": row['okved_main'],
            "okved_main_name": row['okved_main_name'],
            "authorized_capital": float(row['authorized_capital']) if row['authorized_capital'] else None,
            "employee_count": row['employee_count'],
            "last_updated": row['updated_at'],
            "source": row['source']
        }
