"""OpenSanctions Screening Service

Integrates with the OpenSanctions yente API for real-time sanctions screening.
"""

import logging
from datetime import UTC, datetime
from typing import Any
from uuid import UUID, uuid4

import httpx
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.compliance.customer import Customer
from app.models.compliance.screening import (
    MatchStatus,
    ScreeningMatch,
    ScreeningResult,
)

logger = logging.getLogger(__name__)


class MatchResult(BaseModel):
    """Match result from yente API"""

    id: str
    schema_: str
    caption: str
    score: float
    datasets: list[str]
    properties: dict[str, Any]


class ScreeningService:
    """Service for sanctions and PEP screening via OpenSanctions"""

    def __init__(self, base_url: str | None = None):
        self.base_url = base_url or getattr(settings, "OPENSANCTIONS_URL", "http://localhost:8000")
        self.api_key = getattr(settings, "OPENSANCTIONS_API_KEY", None)
        self.timeout = 30.0
        self.match_threshold = 0.7  # Minimum score to consider a match

    async def _make_request(self, method: str, endpoint: str, **kwargs) -> dict[str, Any]:
        """Make HTTP request to yente API"""
        headers = kwargs.pop("headers", {})
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        async with httpx.AsyncClient(timeout=self.timeout) as client:
            url = f"{self.base_url}{endpoint}"
            response = await client.request(method, url, headers=headers, **kwargs)
            response.raise_for_status()
            return response.json()

    async def check_health(self) -> dict[str, Any]:
        """Check yente API health status"""
        try:
            result = await self._make_request("GET", "/healthz")
            return {"status": "healthy", "details": result}
        except Exception as e:
            logger.error(f"OpenSanctions health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}

    async def get_datasets(self) -> list[dict[str, Any]]:
        """Get available datasets from yente"""
        try:
            result = await self._make_request("GET", "/catalog")
            return result.get("datasets", [])
        except Exception as e:
            logger.error(f"Failed to get datasets: {e}")
            return []

    async def screen_entity(
        self,
        name: str,
        schema: str = "Person",
        birth_date: str | None = None,
        countries: list[str] | None = None,
        id_numbers: list[str] | None = None,
        datasets: list[str] | None = None,
    ) -> list[MatchResult]:
        """
        Screen an entity against sanctions and PEP lists.

        Args:
            name: Entity name to screen
            schema: Entity type (Person, Company, Organization)
            birth_date: Birth date for person screening
            countries: Countries associated with entity
            id_numbers: ID numbers (passport, national ID, etc.)
            datasets: Specific datasets to search (default: all)

        Returns:
            List of matching entities with scores
        """
        # Build the query properties
        properties = {"name": [name]}

        if birth_date:
            properties["birthDate"] = [birth_date]
        if countries:
            properties["country"] = countries
        if id_numbers:
            properties["idNumber"] = id_numbers

        query = {"schema": schema, "properties": properties}

        params = {}
        if datasets:
            params["dataset"] = datasets

        try:
            result = await self._make_request(
                "POST", "/match/default", json={"queries": {"q1": query}}, params=params
            )

            matches = []
            for resp in result.get("responses", {}).get("q1", {}).get("results", []):
                matches.append(
                    MatchResult(
                        id=resp.get("id", ""),
                        schema_=resp.get("schema", ""),
                        caption=resp.get("caption", ""),
                        score=resp.get("score", 0.0),
                        datasets=resp.get("datasets", []),
                        properties=resp.get("properties", {}),
                    )
                )

            return [m for m in matches if m.score >= self.match_threshold]

        except Exception as e:
            logger.error(f"Screening failed for {name}: {e}")
            raise

    async def screen_customer(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        customer_id: UUID,
        screened_by: UUID | None = None,
    ) -> ScreeningResult:
        """
        Screen a customer against all watchlists and save results.

        Args:
            db: Database session
            tenant_id: Tenant ID
            customer_id: Customer to screen
            screened_by: User performing screening

        Returns:
            ScreeningResult with matches
        """
        # Get customer
        result = await db.execute(select(Customer).where(Customer.id == customer_id))
        customer = result.scalar_one_or_none()
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")

        # Determine schema based on customer type
        schema = "Person" if customer.customer_type == "INDIVIDUAL" else "Company"

        # Build screening parameters
        countries = []
        if customer.country_of_residence:
            countries.append(customer.country_of_residence)
        if customer.nationality:
            countries.append(customer.nationality)

        # Screen against OpenSanctions
        now = datetime.now(UTC)
        screening_result_id = uuid4()

        try:
            matches = await self.screen_entity(
                name=customer.full_name or customer.legal_name,
                schema=schema,
                birth_date=customer.date_of_birth.isoformat() if customer.date_of_birth else None,
                countries=countries if countries else None,
            )

            # Create screening result
            screening_result = ScreeningResult(
                id=screening_result_id,
                tenant_id=tenant_id,
                customer_id=customer_id,
                screening_type="SANCTIONS",
                screened_at=now,
                screened_by=screened_by,
                total_matches=len(matches),
                confirmed_matches=0,
                false_positives=0,
                pending_review=len(matches),
                status="PENDING_REVIEW" if matches else "CLEAR",
                datasets_searched=["opensanctions"],
            )
            db.add(screening_result)

            # Create match records
            for match in matches:
                # Determine match type
                match_type = "SANCTIONS"
                if any("pep" in ds.lower() for ds in match.datasets):
                    match_type = "PEP"

                screening_match = ScreeningMatch(
                    id=uuid4(),
                    tenant_id=tenant_id,
                    screening_result_id=screening_result_id,
                    watchlist_entity_id=match.id,
                    match_score=match.score,
                    match_type=match_type,
                    matched_name=match.caption,
                    matched_fields={"properties": match.properties},
                    datasets=match.datasets,
                    status=MatchStatus.PENDING,
                )
                db.add(screening_match)

            # Update customer flags
            if matches:
                high_score_matches = [m for m in matches if m.score >= 0.9]
                if high_score_matches:
                    customer.has_sanctions_match = True
                    if any("pep" in ds.lower() for ds in high_score_matches[0].datasets):
                        customer.is_pep = True

            await db.commit()
            await db.refresh(screening_result)
            return screening_result

        except Exception as e:
            logger.error(f"Customer screening failed: {e}")
            # Create failed screening result
            screening_result = ScreeningResult(
                id=screening_result_id,
                tenant_id=tenant_id,
                customer_id=customer_id,
                screening_type="SANCTIONS",
                screened_at=now,
                screened_by=screened_by,
                total_matches=0,
                status="ERROR",
                datasets_searched=["opensanctions"],
            )
            db.add(screening_result)
            await db.commit()
            raise

    async def batch_screen_customers(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        customer_ids: list[UUID],
        screened_by: UUID | None = None,
    ) -> dict[str, Any]:
        """
        Screen multiple customers in batch.

        Returns summary of results.
        """
        results = {
            "total": len(customer_ids),
            "screened": 0,
            "matches_found": 0,
            "errors": 0,
            "details": [],
        }

        for customer_id in customer_ids:
            try:
                screening_result = await self.screen_customer(
                    db, tenant_id, customer_id, screened_by
                )
                results["screened"] += 1
                if screening_result.total_matches > 0:
                    results["matches_found"] += 1
                results["details"].append(
                    {
                        "customer_id": str(customer_id),
                        "status": screening_result.status,
                        "matches": screening_result.total_matches,
                    }
                )
            except Exception as e:
                results["errors"] += 1
                results["details"].append(
                    {"customer_id": str(customer_id), "status": "ERROR", "error": str(e)}
                )

        return results

    async def resolve_match(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        match_id: UUID,
        status: MatchStatus,
        resolution_notes: str | None = None,
        resolved_by: UUID | None = None,
    ) -> ScreeningMatch:
        """
        Resolve a screening match as true positive or false positive.
        """
        result = await db.execute(
            select(ScreeningMatch).where(
                ScreeningMatch.id == match_id, ScreeningMatch.tenant_id == tenant_id
            )
        )
        match = result.scalar_one_or_none()
        if not match:
            raise ValueError(f"Match {match_id} not found")

        match.status = status
        match.resolution_notes = resolution_notes
        match.resolved_at = datetime.now(UTC)
        match.resolved_by = resolved_by

        # Update screening result counts
        screening_result = await db.execute(
            select(ScreeningResult).where(ScreeningResult.id == match.screening_result_id)
        )
        sr = screening_result.scalar_one_or_none()
        if sr:
            sr.pending_review -= 1
            if status == MatchStatus.CONFIRMED:
                sr.confirmed_matches += 1
            elif status == MatchStatus.FALSE_POSITIVE:
                sr.false_positives += 1

            # Update overall status
            if sr.pending_review == 0:
                sr.status = "HIT" if sr.confirmed_matches > 0 else "CLEAR"

        await db.commit()
        await db.refresh(match)
        return match

    async def get_entity_details(self, entity_id: str) -> dict[str, Any]:
        """Get full details of a watchlist entity"""
        try:
            result = await self._make_request("GET", f"/entities/{entity_id}")
            return result
        except Exception as e:
            logger.error(f"Failed to get entity {entity_id}: {e}")
            raise


# Global service instance
screening_service = ScreeningService()
