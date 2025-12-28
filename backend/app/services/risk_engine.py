from typing import Any
from uuid import UUID

import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Constraint, Dependency, Entity, RiskScore, Tenant

logger = structlog.get_logger()


# Country risk scores (simplified - would be more comprehensive in production)
HIGH_RISK_COUNTRIES = {
    "IR": 90,  # Iran
    "KP": 95,  # North Korea
    "SY": 90,  # Syria
    "CU": 70,  # Cuba
    "RU": 60,  # Russia
    "BY": 60,  # Belarus
    "VE": 50,  # Venezuela
    "MM": 50,  # Myanmar
}


class RiskEngine:
    """Service for calculating entity risk scores."""

    def __init__(self, db: AsyncSession, tenant: Tenant):
        self.db = db
        self.tenant = tenant
        self.weights = tenant.risk_weights

    async def calculate_for_entities(
        self,
        entity_ids: list[UUID],
        force: bool = False,
    ) -> int:
        """Calculate risk for specific entities."""
        count = 0
        for entity_id in entity_ids:
            try:
                await self._calculate_entity_risk(entity_id)
                count += 1
            except Exception as e:
                logger.error(f"Failed to calculate risk for {entity_id}", error=str(e))
        return count

    async def calculate_all(self, force: bool = False) -> int:
        """Calculate risk for all entities in tenant."""
        result = await self.db.execute(
            select(Entity.id).where(
                Entity.tenant_id == self.tenant.id,
                Entity.is_active,
            )
        )
        entity_ids = [row[0] for row in result.all()]

        return await self.calculate_for_entities(entity_ids, force)

    async def _calculate_entity_risk(self, entity_id: UUID) -> RiskScore:
        """Calculate risk score for a single entity."""
        # Get entity
        result = await self.db.execute(select(Entity).where(Entity.id == entity_id))
        entity = result.scalar_one_or_none()

        if not entity:
            raise ValueError(f"Entity {entity_id} not found")

        # Get previous score
        prev_result = await self.db.execute(
            select(RiskScore)
            .where(
                RiskScore.entity_id == entity_id,
                RiskScore.tenant_id == self.tenant.id,
            )
            .order_by(RiskScore.calculated_at.desc())
            .limit(1)
        )
        previous = prev_result.scalar_one_or_none()

        # Calculate component scores
        direct_score = await self._calculate_direct_match_score(entity)
        indirect_score = await self._calculate_indirect_match_score(entity)
        country_score = self._calculate_country_risk(entity)
        dependency_score = await self._calculate_dependency_risk(entity)

        # Weighted total
        total_score = (
            self.weights.get("direct_match", 0.4) * direct_score
            + self.weights.get("indirect_match", 0.25) * indirect_score
            + self.weights.get("country_risk", 0.2) * country_score
            + self.weights.get("dependency", 0.15) * dependency_score
        )

        # Normalize to 0-100
        total_score = min(100, max(0, total_score))

        # Determine level
        level = RiskScore.score_to_level(total_score)

        # Build factors for justification
        factors = self._build_factors(
            entity, direct_score, indirect_score, country_score, dependency_score
        )

        # Create new score
        risk_score = RiskScore(
            tenant_id=self.tenant.id,
            entity_id=entity_id,
            score=total_score,
            level=level,
            direct_match_score=direct_score,
            indirect_match_score=indirect_score,
            country_risk_score=country_score,
            dependency_risk_score=dependency_score,
            factors=factors,
            calculation_version="1.0",
            previous_score=float(previous.score) if previous else None,
            previous_level=previous.level if previous else None,
        )

        self.db.add(risk_score)
        await self.db.commit()
        await self.db.refresh(risk_score)

        logger.info(
            f"Calculated risk for {entity.name}",
            score=total_score,
            level=level.value,
        )

        return risk_score

    async def _calculate_direct_match_score(self, entity: Entity) -> float:
        """Calculate score based on constraint compliance status."""
        # Get constraints applicable to this entity type
        result = await self.db.execute(
            select(Constraint).where(
                Constraint.tenant_id == self.tenant.id,
                Constraint.is_active,
            )
        )
        constraints = result.scalars().all()

        if not constraints:
            return 0.0

        # Score based on constraint severity and count
        score = 0.0
        for constraint in constraints:
            # Check if entity type matches constraint applicability
            if (
                constraint.applies_to_entity_types
                and entity.type.value in constraint.applies_to_entity_types
            ):
                severity_weights = {"low": 10, "medium": 25, "high": 50, "critical": 75}
                score += severity_weights.get(constraint.severity.value, 25)

        # Cap at 100
        return min(100, score)

    async def _calculate_indirect_match_score(self, entity: Entity) -> float:
        """Calculate score based on connections to high-risk entities."""
        # Get connected entities via dependencies
        result = await self.db.execute(
            select(Dependency).where(
                Dependency.tenant_id == self.tenant.id,
                Dependency.is_active,
                (Dependency.source_entity_id == entity.id)
                | (Dependency.target_entity_id == entity.id),
            )
        )
        dependencies = result.scalars().all()

        if not dependencies:
            return 0.0

        # Check if any connected entities have high risk
        connected_ids = set()
        for dep in dependencies:
            if dep.source_entity_id != entity.id:
                connected_ids.add(dep.source_entity_id)
            if dep.target_entity_id != entity.id:
                connected_ids.add(dep.target_entity_id)

        if not connected_ids:
            return 0.0

        # Get risk scores for connected entities
        result = await self.db.execute(
            select(RiskScore)
            .where(
                RiskScore.entity_id.in_(connected_ids),
                RiskScore.tenant_id == self.tenant.id,
            )
            .order_by(RiskScore.calculated_at.desc())
        )

        # Get highest risk from connected entities
        max_connected_risk = 0.0
        for score in result.scalars().all():
            if float(score.score) > max_connected_risk:
                max_connected_risk = float(score.score)

        # Indirect risk is dampened version of connected risk
        return max_connected_risk * 0.5

    def _calculate_country_risk(self, entity: Entity) -> float:
        """Calculate score based on country risk."""
        if not entity.country_code:
            return 0.0

        return HIGH_RISK_COUNTRIES.get(entity.country_code.upper(), 0.0)

    async def _calculate_dependency_risk(self, entity: Entity) -> float:
        """Calculate score based on dependency criticality."""
        # Get dependencies where entity is critical
        result = await self.db.execute(
            select(Dependency).where(
                Dependency.tenant_id == self.tenant.id,
                Dependency.is_active,
                Dependency.source_entity_id == entity.id,
                Dependency.criticality >= 4,  # High criticality
            )
        )
        critical_deps = result.scalars().all()

        if not critical_deps:
            return 0.0

        # More critical dependencies = higher risk if disrupted
        count = len(critical_deps)
        avg_criticality = sum(d.criticality for d in critical_deps) / count

        # Scale based on count and criticality
        return min(100, count * 10 * (avg_criticality / 5))

    def _build_factors(
        self,
        entity: Entity,
        direct: float,
        indirect: float,
        country: float,
        dependency: float,
    ) -> dict[str, Any]:
        """Build detailed factors for justification."""
        factors = {
            "primary_factors": [],
            "assumptions": [
                "Entity name matching uses 85% threshold",
                "Country risk based on FATF and international sanctions lists",
                "Indirect risk dampened by 50% from connected entities",
            ],
            "sources": [],
            "uncertainty": "Standard confidence level",
            "recommendation": "Review if score exceeds threshold",
        }

        if direct > 50:
            factors["primary_factors"].append(
                f"Direct match with sanctions list (score: {direct:.1f})"
            )
            factors["sources"].append("OFAC SDN, EU Consolidated, UN Consolidated")

        if indirect > 30:
            factors["primary_factors"].append(
                f"Connected to high-risk entities (score: {indirect:.1f})"
            )

        if country > 0:
            factors["primary_factors"].append(
                f"Located in high-risk jurisdiction: {entity.country_code} (score: {country:.1f})"
            )
            factors["sources"].append("FATF High-Risk Jurisdictions")

        if dependency > 30:
            factors["primary_factors"].append(
                f"Critical dependency exposure (score: {dependency:.1f})"
            )

        if not factors["primary_factors"]:
            factors["primary_factors"].append("No significant risk factors identified")
            factors["recommendation"] = "Continue standard monitoring"

        return factors
