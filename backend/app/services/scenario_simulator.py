from datetime import datetime, timezone
from typing import List, Dict, Any
from uuid import UUID
import structlog

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models import (
    Entity,
    Dependency,
    RiskScore,
    Scenario,
    ScenarioStatus,
    ScenarioType,
    Tenant,
)

logger = structlog.get_logger()


class ScenarioSimulator:
    """Service for running what-if scenario simulations."""

    def __init__(self, db: AsyncSession, tenant: Tenant):
        self.db = db
        self.tenant = tenant

    async def run(self, scenario_id: UUID) -> Dict[str, Any]:
        """Run a scenario simulation."""
        # Get scenario
        result = await self.db.execute(
            select(Scenario).where(Scenario.id == scenario_id)
        )
        scenario = result.scalar_one_or_none()

        if not scenario:
            raise ValueError(f"Scenario {scenario_id} not found")

        try:
            # Capture baseline
            baseline = await self._capture_baseline(scenario)
            scenario.baseline_snapshot = baseline

            # Run simulation based on type
            if scenario.type == ScenarioType.ENTITY_SANCTIONED:
                results = await self._simulate_entity_sanctioned(scenario)
            elif scenario.type == ScenarioType.COUNTRY_EMBARGO:
                results = await self._simulate_country_embargo(scenario)
            elif scenario.type == ScenarioType.SUPPLIER_UNAVAILABLE:
                results = await self._simulate_supplier_unavailable(scenario)
            else:
                results = await self._simulate_custom(scenario)

            # Handle cascading effects if depth > 1
            if scenario.cascade_depth > 1:
                cascade_results = await self._calculate_cascade(
                    scenario, results, scenario.cascade_depth
                )
                scenario.cascade_results = cascade_results

            # Update scenario with results
            scenario.results = results
            scenario.status = ScenarioStatus.COMPLETED
            scenario.completed_at = datetime.now(timezone.utc)

            await self.db.commit()

            logger.info(f"Scenario {scenario.name} completed", results=results)
            return results

        except Exception as e:
            logger.error(f"Scenario {scenario.name} failed", error=str(e))
            scenario.status = ScenarioStatus.FAILED
            scenario.results = {"error": str(e)}
            await self.db.commit()
            raise

    async def _capture_baseline(self, scenario: Scenario) -> Dict[str, Any]:
        """Capture current state as baseline for comparison."""
        # Get current risk scores for affected entities
        affected_ids = [UUID(id) for id in scenario.affected_entity_ids]

        if not affected_ids:
            # If no specific entities, get all
            result = await self.db.execute(
                select(Entity.id).where(
                    Entity.tenant_id == self.tenant.id,
                    Entity.is_active,
                )
            )
            affected_ids = [row[0] for row in result.all()]

        # Get current risk scores
        risk_scores = {}
        for entity_id in affected_ids[:100]:  # Limit for performance
            result = await self.db.execute(
                select(RiskScore)
                .where(
                    RiskScore.entity_id == entity_id,
                    RiskScore.tenant_id == self.tenant.id,
                )
                .order_by(RiskScore.calculated_at.desc())
                .limit(1)
            )
            score = result.scalar_one_or_none()
            if score:
                risk_scores[str(entity_id)] = {
                    "score": float(score.score),
                    "level": score.level.value,
                }

        return {
            "captured_at": datetime.now(timezone.utc).isoformat(),
            "entity_count": len(affected_ids),
            "risk_scores": risk_scores,
        }

    async def _simulate_entity_sanctioned(self, scenario: Scenario) -> Dict[str, Any]:
        """Simulate what happens if specific entities get sanctioned."""
        params = scenario.parameters
        target_ids = [UUID(id) for id in params.get("target_entity_ids", [])]

        if not target_ids:
            return {"error": "No target entities specified"}

        impacted = []
        risk_changes = {}

        for entity_id in target_ids:
            # Get entity
            result = await self.db.execute(select(Entity).where(Entity.id == entity_id))
            entity = result.scalar_one_or_none()

            if not entity:
                continue

            # Find all entities that depend on this one
            result = await self.db.execute(
                select(Dependency).where(
                    Dependency.tenant_id == self.tenant.id,
                    Dependency.target_entity_id == entity_id,
                    Dependency.is_active,
                )
            )
            incoming_deps = result.scalars().all()

            for dep in incoming_deps:
                # Each dependent entity would be impacted
                source_result = await self.db.execute(
                    select(Entity).where(Entity.id == dep.source_entity_id)
                )
                source_entity = source_result.scalar_one_or_none()

                if source_entity:
                    # Calculate new risk (would increase due to sanctioned dependency)
                    impact = {
                        "entity_id": str(source_entity.id),
                        "entity_name": source_entity.name,
                        "impact_type": "dependency_on_sanctioned",
                        "dependency_layer": dep.layer.value,
                        "criticality": dep.criticality,
                        "severity": "HIGH" if dep.criticality >= 4 else "MEDIUM",
                    }
                    impacted.append(impact)

                    # Estimate risk increase
                    baseline = scenario.baseline_snapshot.get("risk_scores", {}).get(
                        str(source_entity.id), {}
                    )
                    current_score = baseline.get("score", 50)
                    # Increase based on criticality
                    new_score = min(100, current_score + dep.criticality * 10)

                    risk_changes[str(source_entity.id)] = {
                        "before": current_score,
                        "after": new_score,
                        "change": new_score - current_score,
                    }

        # Determine overall severity
        high_impact = sum(1 for i in impacted if i["severity"] == "HIGH")
        severity = (
            "CRITICAL" if high_impact > 3 else "HIGH" if high_impact > 0 else "MEDIUM"
        )

        return {
            "summary": f"Sanctioning {len(target_ids)} entities would impact {len(impacted)} dependent entities",
            "severity": severity,
            "impacted_entities": impacted,
            "risk_score_changes": risk_changes,
            "recommendations": self._generate_recommendations(impacted, severity),
        }

    async def _simulate_country_embargo(self, scenario: Scenario) -> Dict[str, Any]:
        """Simulate what happens if a country gets embargoed."""
        params = scenario.parameters
        country_code = params.get("country_code", "").upper()

        if not country_code:
            return {"error": "No country code specified"}

        # Find all entities in this country
        result = await self.db.execute(
            select(Entity).where(
                Entity.tenant_id == self.tenant.id,
                Entity.country_code == country_code,
                Entity.is_active,
            )
        )
        country_entities = result.scalars().all()

        impacted = []
        risk_changes = {}

        for entity in country_entities:
            # Entity itself is directly impacted
            impacted.append(
                {
                    "entity_id": str(entity.id),
                    "entity_name": entity.name,
                    "impact_type": "direct_embargo",
                    "severity": "CRITICAL",
                }
            )

            # Find all entities depending on this one
            result = await self.db.execute(
                select(Dependency).where(
                    Dependency.tenant_id == self.tenant.id,
                    Dependency.target_entity_id == entity.id,
                    Dependency.is_active,
                )
            )
            deps = result.scalars().all()

            for dep in deps:
                source_result = await self.db.execute(
                    select(Entity).where(Entity.id == dep.source_entity_id)
                )
                source = source_result.scalar_one_or_none()

                if source and source.country_code != country_code:
                    impacted.append(
                        {
                            "entity_id": str(source.id),
                            "entity_name": source.name,
                            "impact_type": "dependency_in_embargoed_country",
                            "dependency_layer": dep.layer.value,
                            "severity": "HIGH" if dep.criticality >= 4 else "MEDIUM",
                        }
                    )

        severity = "CRITICAL" if len(country_entities) > 5 else "HIGH"

        return {
            "summary": f"Embargo on {country_code} would directly affect {len(country_entities)} entities and impact {len(impacted)} total",
            "severity": severity,
            "impacted_entities": impacted,
            "risk_score_changes": risk_changes,
            "recommendations": [
                f"Identify alternative suppliers outside {country_code}",
                "Review all contracts with entities in affected country",
                "Assess financial exposure and payment corridors",
            ],
        }

    async def _simulate_supplier_unavailable(
        self, scenario: Scenario
    ) -> Dict[str, Any]:
        """Simulate what happens if a supplier becomes unavailable."""
        params = scenario.parameters
        supplier_id = params.get("supplier_entity_id")

        if not supplier_id:
            return {"error": "No supplier entity specified"}

        supplier_id = UUID(supplier_id)

        # Get supplier
        result = await self.db.execute(select(Entity).where(Entity.id == supplier_id))
        supplier = result.scalar_one_or_none()

        if not supplier:
            return {"error": "Supplier entity not found"}

        # Find all entities depending on this supplier
        result = await self.db.execute(
            select(Dependency).where(
                Dependency.tenant_id == self.tenant.id,
                Dependency.target_entity_id == supplier_id,
                Dependency.is_active,
            )
        )
        deps = result.scalars().all()

        impacted = []
        for dep in deps:
            source_result = await self.db.execute(
                select(Entity).where(Entity.id == dep.source_entity_id)
            )
            source = source_result.scalar_one_or_none()

            if source:
                impacted.append(
                    {
                        "entity_id": str(source.id),
                        "entity_name": source.name,
                        "impact_type": "supplier_unavailable",
                        "dependency_layer": dep.layer.value,
                        "relationship": dep.relationship_type.value,
                        "criticality": dep.criticality,
                        "severity": "CRITICAL"
                        if dep.criticality == 5
                        else "HIGH"
                        if dep.criticality >= 4
                        else "MEDIUM",
                    }
                )

        critical_count = sum(1 for i in impacted if i["severity"] == "CRITICAL")
        severity = (
            "CRITICAL"
            if critical_count > 0
            else "HIGH"
            if len(impacted) > 5
            else "MEDIUM"
        )

        return {
            "summary": f"Loss of supplier {supplier.name} would affect {len(impacted)} dependent entities",
            "severity": severity,
            "impacted_entities": impacted,
            "risk_score_changes": {},
            "recommendations": [
                f"Identify backup suppliers for {supplier.name}",
                "Review inventory levels and lead times",
                "Assess contract termination clauses",
            ],
        }

    async def _simulate_custom(self, scenario: Scenario) -> Dict[str, Any]:
        """Run a custom scenario based on parameters."""
        params = scenario.parameters

        return {
            "summary": "Custom scenario simulation",
            "severity": "MEDIUM",
            "impacted_entities": [],
            "risk_score_changes": {},
            "recommendations": ["Review scenario parameters and adjust as needed"],
            "custom_data": params,
        }

    async def _calculate_cascade(
        self,
        scenario: Scenario,
        initial_results: Dict[str, Any],
        depth: int,
    ) -> Dict[str, Any]:
        """Calculate cascading effects over time."""
        cascade_effects = []
        current_impacted = set(
            i["entity_id"] for i in initial_results.get("impacted_entities", [])
        )

        for level in range(1, depth):
            # Find secondary impacts
            new_impacts = []

            for entity_id in current_impacted:
                # Find entities depending on currently impacted
                result = await self.db.execute(
                    select(Dependency).where(
                        Dependency.tenant_id == self.tenant.id,
                        Dependency.target_entity_id == UUID(entity_id),
                        Dependency.is_active,
                    )
                )
                deps = result.scalars().all()

                for dep in deps:
                    if str(dep.source_entity_id) not in current_impacted:
                        source_result = await self.db.execute(
                            select(Entity).where(Entity.id == dep.source_entity_id)
                        )
                        source = source_result.scalar_one_or_none()

                        if source:
                            new_impacts.append(
                                {
                                    "entity_id": str(source.id),
                                    "entity_name": source.name,
                                    "cascade_level": level + 1,
                                    "triggered_by": entity_id,
                                    "estimated_days": level * 30,  # Rough estimate
                                }
                            )
                            current_impacted.add(str(source.id))

            if new_impacts:
                cascade_effects.append(
                    {
                        "level": level + 1,
                        "estimated_timeline_days": level * 30,
                        "new_impacts": new_impacts,
                    }
                )

        return {
            "total_levels": len(cascade_effects) + 1,
            "total_entities_affected": len(current_impacted),
            "effects": cascade_effects,
        }

    def _generate_recommendations(
        self,
        impacted: List[Dict[str, Any]],
        severity: str,
    ) -> List[str]:
        """Generate recommendations based on impact analysis."""
        recommendations = []

        if severity == "CRITICAL":
            recommendations.append("Immediate executive review required")
            recommendations.append("Activate contingency plans")

        if any(i.get("dependency_layer") == "financial" for i in impacted):
            recommendations.append("Review financial exposure and payment alternatives")

        if any(i.get("dependency_layer") == "operational" for i in impacted):
            recommendations.append(
                "Identify alternative suppliers and logistics routes"
            )

        if any(i.get("criticality", 0) >= 4 for i in impacted):
            recommendations.append(
                "Prioritize mitigation for high-criticality dependencies"
            )

        if not recommendations:
            recommendations.append("Continue monitoring situation")

        return recommendations
