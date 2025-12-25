#!/usr/bin/env python3
"""
Data Loader for Generated Data (Phase 6)
Loads JSONL files into the database with progress tracking.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime
import structlog

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

logger = structlog.get_logger()


class DataLoader:
    """Load generated data into the database."""

    def __init__(self, database_url: str, data_dir: str = "/tmp/cortex-data"):
        self.data_dir = Path(data_dir)
        self.engine = create_async_engine(
            database_url,
            echo=False,
            pool_size=10,
            max_overflow=20,
        )
        self.Session = sessionmaker(
            self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
        )
        self.stats = {
            "entities": 0,
            "constraints": 0,
            "dependencies": 0,
            "audit_logs": 0,
            "errors": 0,
        }

    async def load_entities(self, batch_size: int = 1000):
        """Load entities from JSONL file."""
        filepath = self.data_dir / "entities.jsonl"
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return

        print(f"Loading entities from {filepath}...")
        batch = []

        async with self.Session() as session:
            with open(filepath) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        batch.append(data)

                        if len(batch) >= batch_size:
                            await self._insert_entities(session, batch)
                            self.stats["entities"] += len(batch)
                            batch = []

                            if self.stats["entities"] % 10000 == 0:
                                print(f"  Loaded {self.stats['entities']:,} entities")

                    except Exception as e:
                        self.stats["errors"] += 1
                        logger.error("Error loading entity", error=str(e))

                # Insert remaining
                if batch:
                    await self._insert_entities(session, batch)
                    self.stats["entities"] += len(batch)

        print(f"  Total: {self.stats['entities']:,} entities loaded")

    async def _insert_entities(self, session: AsyncSession, batch: list):
        """Batch insert entities using raw SQL for performance."""
        if not batch:
            return

        values = []
        for e in batch:
            values.append(f"""(
                '{e["id"]}',
                '{e["tenant_id"]}',
                '{e["name"].replace("'", "''")}',
                '{e["type"]}',
                '{e.get("country", "")}',
                '{e.get("description", "").replace("'", "''")}',
                '{json.dumps(e.get("aliases", []))}',
                '{json.dumps(e.get("identifiers", {}))}',
                '{json.dumps(e.get("metadata", {}))}',
                {e.get("is_active", True)},
                {e.get("current_risk_score") or "NULL"},
                '{e.get("risk_level", "low")}',
                '{e.get("created_at", datetime.utcnow().isoformat())}',
                '{e.get("updated_at", datetime.utcnow().isoformat())}'
            )""")

        sql = f"""
            INSERT INTO entities (
                id, tenant_id, name, type, country, description,
                aliases, identifiers, metadata, is_active,
                current_risk_score, risk_level, created_at, updated_at
            ) VALUES {",".join(values)}
            ON CONFLICT (id) DO NOTHING
        """

        try:
            await session.execute(text(sql))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Batch insert failed", error=str(e))
            self.stats["errors"] += len(batch)

    async def load_constraints(self, batch_size: int = 1000):
        """Load constraints from JSONL file."""
        filepath = self.data_dir / "constraints.jsonl"
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return

        print(f"Loading constraints from {filepath}...")
        batch = []

        async with self.Session() as session:
            with open(filepath) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        batch.append(data)

                        if len(batch) >= batch_size:
                            await self._insert_constraints(session, batch)
                            self.stats["constraints"] += len(batch)
                            batch = []

                            if self.stats["constraints"] % 10000 == 0:
                                print(f"  Loaded {self.stats['constraints']:,} constraints")

                    except Exception as e:
                        self.stats["errors"] += 1
                        logger.error("Error loading constraint", error=str(e))

                if batch:
                    await self._insert_constraints(session, batch)
                    self.stats["constraints"] += len(batch)

        print(f"  Total: {self.stats['constraints']:,} constraints loaded")

    async def _insert_constraints(self, session: AsyncSession, batch: list):
        """Batch insert constraints."""
        if not batch:
            return

        values = []
        for c in batch:
            expiry = f"'{c['expiry_date']}'" if c.get("expiry_date") else "NULL"
            values.append(f"""(
                '{c["id"]}',
                '{c["tenant_id"]}',
                '{c["name"].replace("'", "''")}',
                '{c["type"]}',
                '{c["severity"]}',
                '{c.get("source", "").replace("'", "''")}',
                '{c.get("description", "").replace("'", "''")}',
                '{c.get("effective_date", datetime.utcnow().isoformat())}',
                {expiry},
                {c.get("is_active", True)},
                '{json.dumps(c.get("metadata", {}))}',
                '{c.get("created_at", datetime.utcnow().isoformat())}',
                '{c.get("updated_at", datetime.utcnow().isoformat())}'
            )""")

        sql = f"""
            INSERT INTO constraints (
                id, tenant_id, name, type, severity, source, description,
                effective_date, expiry_date, is_active, metadata,
                created_at, updated_at
            ) VALUES {",".join(values)}
            ON CONFLICT (id) DO NOTHING
        """

        try:
            await session.execute(text(sql))
            await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error("Batch insert failed", error=str(e))
            self.stats["errors"] += len(batch)

    async def load_dependencies(self, batch_size: int = 1000):
        """Load dependencies from JSONL file."""
        filepath = self.data_dir / "dependencies.jsonl"
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return

        print(f"Loading dependencies from {filepath}...")
        batch = []

        async with self.Session() as session:
            with open(filepath) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        batch.append(data)

                        if len(batch) >= batch_size:
                            await self._insert_dependencies(session, batch)
                            self.stats["dependencies"] += len(batch)
                            batch = []

                            if self.stats["dependencies"] % 100000 == 0:
                                print(f"  Loaded {self.stats['dependencies']:,} dependencies")

                    except Exception:
                        self.stats["errors"] += 1

                if batch:
                    await self._insert_dependencies(session, batch)
                    self.stats["dependencies"] += len(batch)

        print(f"  Total: {self.stats['dependencies']:,} dependencies loaded")

    async def _insert_dependencies(self, session: AsyncSession, batch: list):
        """Batch insert dependencies."""
        if not batch:
            return

        values = []
        for d in batch:
            values.append(f"""(
                '{d["id"]}',
                '{d["tenant_id"]}',
                '{d["source_entity_id"]}',
                '{d["target_entity_id"]}',
                '{d["type"]}',
                {d.get("strength", 0.5)},
                '{d.get("description", "").replace("'", "''")}',
                '{json.dumps(d.get("metadata", {}))}',
                {d.get("is_active", True)},
                '{d.get("created_at", datetime.utcnow().isoformat())}'
            )""")

        sql = f"""
            INSERT INTO dependencies (
                id, tenant_id, source_entity_id, target_entity_id,
                type, strength, description, metadata, is_active, created_at
            ) VALUES {",".join(values)}
            ON CONFLICT (id) DO NOTHING
        """

        try:
            await session.execute(text(sql))
            await session.commit()
        except Exception:
            await session.rollback()
            self.stats["errors"] += len(batch)

    async def load_audit_logs(self, batch_size: int = 5000):
        """Load audit logs from JSONL file."""
        filepath = self.data_dir / "audit_logs.jsonl"
        if not filepath.exists():
            print(f"File not found: {filepath}")
            return

        print(f"Loading audit logs from {filepath}...")
        batch = []

        async with self.Session() as session:
            with open(filepath) as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        batch.append(data)

                        if len(batch) >= batch_size:
                            await self._insert_audit_logs(session, batch)
                            self.stats["audit_logs"] += len(batch)
                            batch = []

                            if self.stats["audit_logs"] % 500000 == 0:
                                print(f"  Loaded {self.stats['audit_logs']:,} audit logs")

                    except Exception:
                        self.stats["errors"] += 1

                if batch:
                    await self._insert_audit_logs(session, batch)
                    self.stats["audit_logs"] += len(batch)

        print(f"  Total: {self.stats['audit_logs']:,} audit logs loaded")

    async def _insert_audit_logs(self, session: AsyncSession, batch: list):
        """Batch insert audit logs."""
        if not batch:
            return

        values = []
        for a in batch:
            values.append(f"""(
                '{a["id"]}',
                '{a["tenant_id"]}',
                '{a["user_id"]}',
                '{a["user_email"]}',
                '{a["action"]}',
                '{a["resource_type"]}',
                '{a.get("resource_id", "")}',
                '{a.get("description", "").replace("'", "''")}',
                '{a.get("ip_address", "")}',
                {a.get("success", True)},
                '{a.get("created_at", datetime.utcnow().isoformat())}'
            )""")

        sql = f"""
            INSERT INTO audit_logs (
                id, tenant_id, user_id, user_email, action,
                resource_type, resource_id, description, ip_address,
                success, created_at
            ) VALUES {",".join(values)}
            ON CONFLICT (id) DO NOTHING
        """

        try:
            await session.execute(text(sql))
            await session.commit()
        except Exception:
            await session.rollback()
            self.stats["errors"] += len(batch)

    async def load_all(self):
        """Load all data files."""
        print("=" * 60)
        print("CORTEX-CI Data Loader")
        print("=" * 60)

        await self.load_entities()
        await self.load_constraints()
        await self.load_dependencies()
        await self.load_audit_logs()

        print("\n" + "=" * 60)
        print("LOADING COMPLETE")
        print("=" * 60)
        for key, value in self.stats.items():
            print(f"  {key}: {value:,}")

    async def close(self):
        """Close database connections."""
        await self.engine.dispose()


async def main():
    """Main entry point."""
    import os

    database_url = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://cortex:cortex@localhost:5432/cortex"
    )

    loader = DataLoader(database_url)
    try:
        await loader.load_all()
    finally:
        await loader.close()


if __name__ == "__main__":
    asyncio.run(main())
