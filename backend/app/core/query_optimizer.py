"""
Query Optimizer (Phase 5.2)
Database query optimization utilities and patterns.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Generic, TypeVar

import structlog
from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

logger = structlog.get_logger()

T = TypeVar("T")


class SortOrder(str, Enum):
    """Sort order for queries."""

    ASC = "asc"
    DESC = "desc"


@dataclass
class PaginationParams:
    """Pagination parameters."""

    page: int = 1
    page_size: int = 20
    max_page_size: int = 100

    def __post_init__(self):
        if self.page < 1:
            self.page = 1
        if self.page_size < 1:
            self.page_size = 20
        if self.page_size > self.max_page_size:
            self.page_size = self.max_page_size

    @property
    def offset(self) -> int:
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        return self.page_size


@dataclass
class SortParams:
    """Sorting parameters."""

    field: str
    order: SortOrder = SortOrder.DESC

    def apply(self, query, model):
        """Apply sorting to query."""
        column = getattr(model, self.field, None)
        if column is not None:
            if self.order == SortOrder.DESC:
                return query.order_by(column.desc())
            return query.order_by(column.asc())
        return query


@dataclass
class FilterParams:
    """Filter parameters."""

    field: str
    operator: str  # eq, ne, gt, lt, gte, lte, like, in, is_null
    value: Any

    def apply(self, query, model):
        """Apply filter to query."""
        column = getattr(model, self.field, None)
        if column is None:
            return query

        if self.operator == "eq":
            return query.where(column == self.value)
        elif self.operator == "ne":
            return query.where(column != self.value)
        elif self.operator == "gt":
            return query.where(column > self.value)
        elif self.operator == "lt":
            return query.where(column < self.value)
        elif self.operator == "gte":
            return query.where(column >= self.value)
        elif self.operator == "lte":
            return query.where(column <= self.value)
        elif self.operator == "like":
            return query.where(column.ilike(f"%{self.value}%"))
        elif self.operator == "in":
            return query.where(column.in_(self.value))
        elif self.operator == "is_null":
            if self.value:
                return query.where(column.is_(None))
            return query.where(column.isnot(None))

        return query


@dataclass
class PaginatedResult(Generic[T]):
    """Paginated result container."""

    items: list[T]
    total: int
    page: int
    page_size: int
    total_pages: int

    def to_dict(self) -> dict:
        return {
            "items": self.items,
            "total": self.total,
            "page": self.page,
            "page_size": self.page_size,
            "total_pages": self.total_pages,
            "has_next": self.page < self.total_pages,
            "has_prev": self.page > 1,
        }


class QueryBuilder:
    """
    Optimized query builder with eager loading and caching support.
    """

    def __init__(self, model, db: AsyncSession):
        self.model = model
        self.db = db
        self._query = select(model)
        self._eager_loads = []
        self._filters = []
        self._sorts = []

    def filter(self, *filters: FilterParams) -> "QueryBuilder":
        """Add filters to query."""
        self._filters.extend(filters)
        return self

    def filter_by(self, **kwargs) -> "QueryBuilder":
        """Add simple equality filters."""
        for field, value in kwargs.items():
            self._filters.append(FilterParams(field, "eq", value))
        return self

    def sort(self, *sorts: SortParams) -> "QueryBuilder":
        """Add sorting to query."""
        self._sorts.extend(sorts)
        return self

    def sort_by(self, field: str, order: str = "desc") -> "QueryBuilder":
        """Add simple sorting."""
        self._sorts.append(SortParams(field, SortOrder(order)))
        return self

    def eager_load(self, *relationships: str) -> "QueryBuilder":
        """Add eager loading for relationships."""
        self._eager_loads.extend(relationships)
        return self

    def _build_query(self):
        """Build the final query."""
        query = self._query

        # Apply eager loading
        for rel in self._eager_loads:
            if hasattr(self.model, rel):
                query = query.options(selectinload(getattr(self.model, rel)))

        # Apply filters
        for f in self._filters:
            query = f.apply(query, self.model)

        # Apply sorting
        for s in self._sorts:
            query = s.apply(query, self.model)

        return query

    async def all(self) -> list:
        """Execute query and return all results."""
        query = self._build_query()
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def first(self) -> Any | None:
        """Execute query and return first result."""
        query = self._build_query().limit(1)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def count(self) -> int:
        """Get count of matching records."""
        count_query = select(func.count()).select_from(self.model)
        for f in self._filters:
            count_query = f.apply(count_query, self.model)
        result = await self.db.execute(count_query)
        return result.scalar() or 0

    async def paginate(self, pagination: PaginationParams) -> PaginatedResult:
        """Execute paginated query."""
        # Get total count
        total = await self.count()
        total_pages = (total + pagination.page_size - 1) // pagination.page_size

        # Get items
        query = self._build_query()
        query = query.offset(pagination.offset).limit(pagination.limit)
        result = await self.db.execute(query)
        items = list(result.scalars().all())

        return PaginatedResult(
            items=items,
            total=total,
            page=pagination.page,
            page_size=pagination.page_size,
            total_pages=total_pages,
        )

    async def exists(self) -> bool:
        """Check if any matching records exist."""
        query = select(func.count()).select_from(self.model).limit(1)
        for f in self._filters:
            query = f.apply(query, self.model)
        result = await self.db.execute(query)
        return (result.scalar() or 0) > 0


class BatchProcessor:
    """
    Process records in batches for memory efficiency.
    """

    def __init__(self, db: AsyncSession, batch_size: int = 1000):
        self.db = db
        self.batch_size = batch_size

    async def process_in_batches(
        self,
        model,
        processor: callable,
        filters: list[FilterParams] | None = None,
    ) -> dict:
        """
        Process all matching records in batches.

        Args:
            model: SQLAlchemy model
            processor: Async function to process each record
            filters: Optional filters

        Returns:
            Processing statistics
        """
        stats = {
            "processed": 0,
            "errors": 0,
            "batches": 0,
        }

        offset = 0
        while True:
            query = select(model)
            if filters:
                for f in filters:
                    query = f.apply(query, model)

            query = query.offset(offset).limit(self.batch_size)
            result = await self.db.execute(query)
            batch = list(result.scalars().all())

            if not batch:
                break

            for record in batch:
                try:
                    await processor(record)
                    stats["processed"] += 1
                except Exception as e:
                    logger.error("Batch processing error", error=str(e))
                    stats["errors"] += 1

            stats["batches"] += 1
            offset += self.batch_size

            # Commit after each batch
            await self.db.commit()

        return stats


class QueryAnalyzer:
    """
    Analyze and optimize query performance.
    """

    def __init__(self, db: AsyncSession):
        self.db = db

    async def explain(self, query) -> dict:
        """Get query execution plan."""
        try:
            explain_query = text(f"EXPLAIN ANALYZE {str(query)}")
            result = await self.db.execute(explain_query)
            plan = [row[0] for row in result]
            return {
                "plan": plan,
                "estimated_cost": self._extract_cost(plan),
            }
        except Exception as e:
            return {"error": str(e)}

    def _extract_cost(self, plan: list[str]) -> float | None:
        """Extract cost from execution plan."""
        for line in plan:
            if "cost=" in line:
                try:
                    cost_str = line.split("cost=")[1].split(" ")[0]
                    return float(cost_str.split("..")[1])
                except (IndexError, ValueError):
                    pass
        return None

    async def get_slow_queries(self, threshold_ms: int = 100) -> list[dict]:
        """Get slow queries from pg_stat_statements if available."""
        try:
            query = text("""
                SELECT query, calls, mean_time, total_time
                FROM pg_stat_statements
                WHERE mean_time > :threshold
                ORDER BY mean_time DESC
                LIMIT 20
            """)
            result = await self.db.execute(query, {"threshold": threshold_ms})
            return [
                {
                    "query": row[0][:200],
                    "calls": row[1],
                    "mean_time_ms": round(row[2], 2),
                    "total_time_ms": round(row[3], 2),
                }
                for row in result
            ]
        except Exception:
            return []

    async def get_table_stats(self, table_name: str) -> dict:
        """Get table statistics."""
        try:
            query = text("""
                SELECT
                    reltuples::bigint as row_count,
                    pg_size_pretty(pg_total_relation_size(:table)) as total_size,
                    pg_size_pretty(pg_indexes_size(:table)) as index_size
                FROM pg_class
                WHERE relname = :table
            """)
            result = await self.db.execute(query, {"table": table_name})
            row = result.first()
            if row:
                return {
                    "row_count": row[0],
                    "total_size": row[1],
                    "index_size": row[2],
                }
            return {}
        except Exception as e:
            return {"error": str(e)}


def query(model):
    """
    Factory function for creating QueryBuilder instances.

    Usage:
        results = await query(Entity).filter_by(tenant_id=tid).all()
    """

    async def builder(db: AsyncSession) -> QueryBuilder:
        return QueryBuilder(model, db)

    return builder
