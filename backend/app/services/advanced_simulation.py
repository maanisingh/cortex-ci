"""
Advanced Simulation Engine (Phase 5.1)
Monte Carlo simulations, what-if analysis, cascade modeling.
"""

import asyncio
import random
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from uuid import UUID, uuid4

import numpy as np
import structlog
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Constraint, Dependency, Entity

logger = structlog.get_logger()


class SimulationType(str, Enum):
    """Types of simulations available."""

    MONTE_CARLO = "monte_carlo"
    WHAT_IF = "what_if"
    CASCADE = "cascade"
    STRESS_TEST = "stress_test"
    HISTORICAL = "historical"


class SimulationStatus(str, Enum):
    """Status of simulation runs."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class SimulationResult:
    """Result of a simulation run."""

    simulation_id: str
    simulation_type: SimulationType
    status: SimulationStatus
    started_at: datetime
    completed_at: datetime | None = None
    iterations: int = 0
    total_iterations: int = 0
    results: dict[str, Any] = field(default_factory=dict)
    metrics: dict[str, float] = field(default_factory=dict)
    affected_entities: list[dict[str, Any]] = field(default_factory=list)
    cascade_paths: list[list[str]] = field(default_factory=list)
    confidence_interval: dict[str, float] = field(default_factory=dict)
    errors: list[str] = field(default_factory=list)

    @property
    def progress(self) -> float:
        if self.total_iterations == 0:
            return 0.0
        return (self.iterations / self.total_iterations) * 100

    def to_dict(self) -> dict[str, Any]:
        return {
            "simulation_id": self.simulation_id,
            "simulation_type": self.simulation_type.value,
            "status": self.status.value,
            "started_at": self.started_at.isoformat(),
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "iterations": self.iterations,
            "total_iterations": self.total_iterations,
            "progress": round(self.progress, 2),
            "results": self.results,
            "metrics": self.metrics,
            "affected_entities": self.affected_entities,
            "cascade_paths": self.cascade_paths,
            "confidence_interval": self.confidence_interval,
            "errors": self.errors,
            "duration_seconds": (
                (self.completed_at - self.started_at).total_seconds() if self.completed_at else None
            ),
        }


@dataclass
class MonteCarloConfig:
    """Configuration for Monte Carlo simulation."""

    iterations: int = 1000
    confidence_level: float = 0.95
    risk_volatility: float = 0.15
    seed: int | None = None


@dataclass
class WhatIfScenario:
    """What-if scenario configuration."""

    name: str
    description: str
    constraint_changes: list[dict[str, Any]] = field(default_factory=list)
    entity_changes: list[dict[str, Any]] = field(default_factory=list)
    global_modifiers: dict[str, float] = field(default_factory=dict)


class AdvancedSimulationEngine:
    """
    Advanced simulation engine for risk analysis and scenario modeling.
    """

    def __init__(self):
        self._simulations: dict[str, SimulationResult] = {}
        self._running_tasks: dict[str, asyncio.Task] = {}

    async def run_monte_carlo(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        entity_ids: list[UUID] | None = None,
        config: MonteCarloConfig | None = None,
    ) -> SimulationResult:
        """
        Run Monte Carlo simulation for risk score distribution.

        Args:
            db: Database session
            tenant_id: Tenant ID
            entity_ids: Specific entities to simulate (all if None)
            config: Simulation configuration

        Returns:
            SimulationResult with probabilistic outcomes
        """
        config = config or MonteCarloConfig()
        if config.seed:
            np.random.seed(config.seed)
            random.seed(config.seed)

        simulation_id = str(uuid4())
        result = SimulationResult(
            simulation_id=simulation_id,
            simulation_type=SimulationType.MONTE_CARLO,
            status=SimulationStatus.RUNNING,
            started_at=datetime.utcnow(),
            total_iterations=config.iterations,
        )
        self._simulations[simulation_id] = result

        try:
            # Get entities
            query = select(Entity).where(
                Entity.tenant_id == tenant_id,
                Entity.is_active == True,  # noqa: E712
            )
            if entity_ids:
                query = query.where(Entity.id.in_(entity_ids))

            entities_result = await db.execute(query)
            entities = entities_result.scalars().all()

            if not entities:
                result.status = SimulationStatus.COMPLETED
                result.completed_at = datetime.utcnow()
                result.results = {"message": "No entities to simulate"}
                return result

            # Run Monte Carlo iterations
            risk_distributions: dict[str, list[float]] = {str(e.id): [] for e in entities}
            portfolio_scores: list[float] = []

            for i in range(config.iterations):
                iteration_scores = []
                for entity in entities:
                    base_score = entity.current_risk_score or 50.0
                    # Apply random walk with volatility
                    shock = np.random.normal(0, config.risk_volatility * base_score)
                    simulated_score = max(0, min(100, base_score + shock))
                    risk_distributions[str(entity.id)].append(simulated_score)
                    iteration_scores.append(simulated_score)

                portfolio_scores.append(np.mean(iteration_scores))
                result.iterations = i + 1

            # Calculate statistics
            entity_stats = {}
            for entity in entities:
                scores = risk_distributions[str(entity.id)]
                percentile_low = (1 - config.confidence_level) / 2 * 100
                percentile_high = (1 + config.confidence_level) / 2 * 100

                entity_stats[str(entity.id)] = {
                    "name": entity.name,
                    "current_score": entity.current_risk_score,
                    "mean": float(np.mean(scores)),
                    "std_dev": float(np.std(scores)),
                    "median": float(np.median(scores)),
                    "min": float(np.min(scores)),
                    "max": float(np.max(scores)),
                    "var_95": float(np.percentile(scores, 95)),
                    "var_99": float(np.percentile(scores, 99)),
                    "confidence_interval": {
                        "lower": float(np.percentile(scores, percentile_low)),
                        "upper": float(np.percentile(scores, percentile_high)),
                    },
                }

            # Portfolio-level stats
            result.results = {
                "entity_statistics": entity_stats,
                "portfolio": {
                    "mean_score": float(np.mean(portfolio_scores)),
                    "std_dev": float(np.std(portfolio_scores)),
                    "var_95": float(np.percentile(portfolio_scores, 95)),
                    "var_99": float(np.percentile(portfolio_scores, 99)),
                    "worst_case": float(np.max(portfolio_scores)),
                    "best_case": float(np.min(portfolio_scores)),
                },
                "distribution": {
                    "high_risk_probability": float(
                        np.mean([1 if s > 75 else 0 for s in portfolio_scores])
                    ),
                    "medium_risk_probability": float(
                        np.mean([1 if 50 <= s <= 75 else 0 for s in portfolio_scores])
                    ),
                    "low_risk_probability": float(
                        np.mean([1 if s < 50 else 0 for s in portfolio_scores])
                    ),
                },
            }

            result.metrics = {
                "total_entities": len(entities),
                "iterations_completed": config.iterations,
                "confidence_level": config.confidence_level,
            }

            result.confidence_interval = {
                "lower": float(np.percentile(portfolio_scores, 2.5)),
                "upper": float(np.percentile(portfolio_scores, 97.5)),
            }

            result.status = SimulationStatus.COMPLETED
            result.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error("Monte Carlo simulation failed", error=str(e))
            result.status = SimulationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.utcnow()

        return result

    async def run_cascade_analysis(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        trigger_entity_id: UUID,
        max_depth: int = 5,
    ) -> SimulationResult:
        """
        Analyze cascade effects when an entity's risk changes.

        Args:
            db: Database session
            tenant_id: Tenant ID
            trigger_entity_id: The entity that triggers the cascade
            max_depth: Maximum depth of cascade analysis

        Returns:
            SimulationResult with cascade paths and impact analysis
        """
        simulation_id = str(uuid4())
        result = SimulationResult(
            simulation_id=simulation_id,
            simulation_type=SimulationType.CASCADE,
            status=SimulationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self._simulations[simulation_id] = result

        try:
            # Get trigger entity
            trigger_query = await db.execute(
                select(Entity).where(
                    Entity.id == trigger_entity_id,
                    Entity.tenant_id == tenant_id,
                )
            )
            trigger_entity = trigger_query.scalar_one_or_none()
            if not trigger_entity:
                raise ValueError(f"Entity {trigger_entity_id} not found")

            # Get all dependencies
            deps_result = await db.execute(
                select(Dependency).where(Dependency.tenant_id == tenant_id)
            )
            dependencies = deps_result.scalars().all()

            # Build adjacency graph
            graph: dict[str, list[dict[str, Any]]] = {}
            for dep in dependencies:
                source_id = str(dep.source_entity_id)
                if source_id not in graph:
                    graph[source_id] = []
                graph[source_id].append(
                    {
                        "target_id": str(dep.target_entity_id),
                        "strength": dep.strength or 0.5,
                        "type": dep.type.value if dep.type else "unknown",
                    }
                )

            # BFS to find cascade paths
            visited: set = set()
            cascade_paths: list[list[str]] = []
            affected: list[dict[str, Any]] = []

            def find_cascades(
                current_id: str,
                path: list[str],
                depth: int,
                cumulative_impact: float,
            ):
                if depth > max_depth or current_id in visited:
                    return

                visited.add(current_id)
                current_path = path + [current_id]

                if current_id in graph:
                    for edge in graph[current_id]:
                        target_id = edge["target_id"]
                        impact = cumulative_impact * edge["strength"]

                        if impact > 0.1:  # Only track significant impacts
                            cascade_paths.append(current_path + [target_id])
                            affected.append(
                                {
                                    "entity_id": target_id,
                                    "path_length": depth + 1,
                                    "impact_factor": round(impact, 4),
                                    "dependency_type": edge["type"],
                                }
                            )

                        find_cascades(target_id, current_path, depth + 1, impact)

            # Start cascade from trigger entity
            find_cascades(str(trigger_entity_id), [], 0, 1.0)

            # Get entity names for affected entities
            affected_ids = [UUID(a["entity_id"]) for a in affected]
            if affected_ids:
                entities_result = await db.execute(
                    select(Entity).where(Entity.id.in_(affected_ids))
                )
                entity_map = {str(e.id): e.name for e in entities_result.scalars()}
                for a in affected:
                    a["entity_name"] = entity_map.get(a["entity_id"], "Unknown")

            # Calculate impact distribution
            result.affected_entities = affected
            result.cascade_paths = cascade_paths
            result.results = {
                "trigger_entity": {
                    "id": str(trigger_entity.id),
                    "name": trigger_entity.name,
                    "current_risk": trigger_entity.current_risk_score,
                },
                "total_affected": len(set(a["entity_id"] for a in affected)),
                "max_cascade_depth": max(len(p) - 1 for p in cascade_paths) if cascade_paths else 0,
                "impact_by_depth": {},
                "high_impact_entities": [a for a in affected if a["impact_factor"] > 0.5],
            }

            # Group by depth
            depth_impacts: dict[int, list[float]] = {}
            for a in affected:
                d = a["path_length"]
                if d not in depth_impacts:
                    depth_impacts[d] = []
                depth_impacts[d].append(a["impact_factor"])

            for d, impacts in depth_impacts.items():
                result.results["impact_by_depth"][str(d)] = {
                    "count": len(impacts),
                    "avg_impact": round(sum(impacts) / len(impacts), 4),
                    "max_impact": round(max(impacts), 4),
                }

            result.metrics = {
                "entities_analyzed": len(visited),
                "cascade_paths_found": len(cascade_paths),
                "max_depth_reached": max_depth,
            }

            result.status = SimulationStatus.COMPLETED
            result.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error("Cascade analysis failed", error=str(e))
            result.status = SimulationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.utcnow()

        return result

    async def run_what_if_analysis(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        scenario: WhatIfScenario,
    ) -> SimulationResult:
        """
        Run what-if scenario analysis.

        Args:
            db: Database session
            tenant_id: Tenant ID
            scenario: The what-if scenario to analyze

        Returns:
            SimulationResult with comparison of before/after states
        """
        simulation_id = str(uuid4())
        result = SimulationResult(
            simulation_id=simulation_id,
            simulation_type=SimulationType.WHAT_IF,
            status=SimulationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self._simulations[simulation_id] = result

        try:
            # Get current state
            entities_result = await db.execute(
                select(Entity).where(
                    Entity.tenant_id == tenant_id,
                    Entity.is_active == True,  # noqa: E712
                )
            )
            entities = entities_result.scalars().all()

            constraints_result = await db.execute(
                select(Constraint).where(
                    Constraint.tenant_id == tenant_id,
                    Constraint.is_active == True,  # noqa: E712
                )
            )
            constraints = constraints_result.scalars().all()

            # Calculate current metrics
            current_state = {
                "total_entities": len(entities),
                "total_constraints": len(constraints),
                "avg_risk_score": (
                    sum(e.current_risk_score or 0 for e in entities) / len(entities)
                    if entities
                    else 0
                ),
                "high_risk_count": sum(1 for e in entities if (e.current_risk_score or 0) >= 75),
                "medium_risk_count": sum(
                    1 for e in entities if 50 <= (e.current_risk_score or 0) < 75
                ),
                "low_risk_count": sum(1 for e in entities if (e.current_risk_score or 0) < 50),
            }

            # Apply scenario modifications (simulated)
            modified_scores = {}
            for entity in entities:
                base_score = entity.current_risk_score or 50

                # Apply global modifiers
                risk_modifier = scenario.global_modifiers.get("risk_multiplier", 1.0)
                modified_score = base_score * risk_modifier

                # Apply entity-specific changes
                for change in scenario.entity_changes:
                    if change.get("entity_id") == str(entity.id):
                        if "risk_adjustment" in change:
                            modified_score += change["risk_adjustment"]
                        if "risk_override" in change:
                            modified_score = change["risk_override"]

                # Clamp to valid range
                modified_scores[str(entity.id)] = max(0, min(100, modified_score))

            # Calculate projected state
            projected_state = {
                "total_entities": len(entities),
                "total_constraints": len(constraints),
                "avg_risk_score": (
                    sum(modified_scores.values()) / len(modified_scores) if modified_scores else 0
                ),
                "high_risk_count": sum(1 for s in modified_scores.values() if s >= 75),
                "medium_risk_count": sum(1 for s in modified_scores.values() if 50 <= s < 75),
                "low_risk_count": sum(1 for s in modified_scores.values() if s < 50),
            }

            # Calculate deltas
            deltas = {}
            for key in current_state:
                if isinstance(current_state[key], (int, float)):
                    deltas[key] = round(projected_state[key] - current_state[key], 2)

            # Find most impacted entities
            impact_details = []
            for entity in entities:
                original = entity.current_risk_score or 50
                projected = modified_scores.get(str(entity.id), original)
                change = projected - original
                if abs(change) > 1:  # Only significant changes
                    impact_details.append(
                        {
                            "entity_id": str(entity.id),
                            "entity_name": entity.name,
                            "original_score": round(original, 2),
                            "projected_score": round(projected, 2),
                            "change": round(change, 2),
                            "direction": "increase" if change > 0 else "decrease",
                        }
                    )

            # Sort by absolute change
            impact_details.sort(key=lambda x: abs(x["change"]), reverse=True)

            result.results = {
                "scenario_name": scenario.name,
                "scenario_description": scenario.description,
                "current_state": current_state,
                "projected_state": projected_state,
                "deltas": deltas,
                "impact_details": impact_details[:20],  # Top 20 impacts
                "recommendation": self._generate_recommendation(deltas),
            }

            result.affected_entities = impact_details
            result.metrics = {
                "entities_analyzed": len(entities),
                "entities_impacted": len(impact_details),
                "risk_change_pct": round(
                    (
                        (projected_state["avg_risk_score"] - current_state["avg_risk_score"])
                        / current_state["avg_risk_score"]
                        * 100
                    )
                    if current_state["avg_risk_score"] > 0
                    else 0,
                    2,
                ),
            }

            result.status = SimulationStatus.COMPLETED
            result.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error("What-if analysis failed", error=str(e))
            result.status = SimulationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.utcnow()

        return result

    async def run_stress_test(
        self,
        db: AsyncSession,
        tenant_id: UUID,
        stress_scenarios: list[str] | None = None,
    ) -> SimulationResult:
        """
        Run stress test scenarios.

        Args:
            db: Database session
            tenant_id: Tenant ID
            stress_scenarios: List of stress scenario names to run

        Returns:
            SimulationResult with stress test outcomes
        """
        simulation_id = str(uuid4())
        result = SimulationResult(
            simulation_id=simulation_id,
            simulation_type=SimulationType.STRESS_TEST,
            status=SimulationStatus.RUNNING,
            started_at=datetime.utcnow(),
        )
        self._simulations[simulation_id] = result

        default_scenarios = stress_scenarios or [
            "regulatory_crackdown",
            "market_crisis",
            "geopolitical_event",
            "supply_chain_disruption",
        ]

        try:
            # Get entities
            entities_result = await db.execute(
                select(Entity).where(
                    Entity.tenant_id == tenant_id,
                    Entity.is_active == True,  # noqa: E712
                )
            )
            entities = entities_result.scalars().all()

            result.total_iterations = len(default_scenarios)
            scenario_results = {}

            for i, scenario_name in enumerate(default_scenarios):
                # Define stress multipliers
                stress_config = self._get_stress_config(scenario_name)

                stressed_scores = []
                impacted = []

                for entity in entities:
                    base_score = entity.current_risk_score or 50

                    # Apply stress based on entity type
                    multiplier = stress_config.get(
                        entity.type.value if entity.type else "default",
                        stress_config.get("default", 1.2),
                    )
                    stressed = min(100, base_score * multiplier)
                    stressed_scores.append(stressed)

                    if stressed - base_score > 10:
                        impacted.append(
                            {
                                "entity_name": entity.name,
                                "original": round(base_score, 1),
                                "stressed": round(stressed, 1),
                                "increase": round(stressed - base_score, 1),
                            }
                        )

                scenario_results[scenario_name] = {
                    "description": stress_config.get("description", ""),
                    "avg_stressed_score": round(np.mean(stressed_scores), 2),
                    "max_stressed_score": round(max(stressed_scores), 2),
                    "entities_at_critical": sum(1 for s in stressed_scores if s >= 90),
                    "entities_at_high_risk": sum(1 for s in stressed_scores if s >= 75),
                    "most_impacted": sorted(impacted, key=lambda x: x["increase"], reverse=True)[
                        :5
                    ],
                }

                result.iterations = i + 1

            result.results = {
                "scenarios_tested": default_scenarios,
                "scenario_results": scenario_results,
                "overall_resilience_score": self._calculate_resilience(scenario_results),
            }

            result.metrics = {
                "entities_tested": len(entities),
                "scenarios_completed": len(default_scenarios),
            }

            result.status = SimulationStatus.COMPLETED
            result.completed_at = datetime.utcnow()

        except Exception as e:
            logger.error("Stress test failed", error=str(e))
            result.status = SimulationStatus.FAILED
            result.errors.append(str(e))
            result.completed_at = datetime.utcnow()

        return result

    def _get_stress_config(self, scenario_name: str) -> dict[str, Any]:
        """Get stress configuration for a scenario."""
        configs = {
            "regulatory_crackdown": {
                "description": "Major regulatory enforcement action",
                "default": 1.3,
                "organization": 1.5,
                "financial_institution": 1.6,
                "government": 1.2,
            },
            "market_crisis": {
                "description": "Severe market downturn",
                "default": 1.4,
                "organization": 1.4,
                "financial_institution": 1.7,
                "vessel": 1.3,
            },
            "geopolitical_event": {
                "description": "Major geopolitical disruption",
                "default": 1.5,
                "government": 1.8,
                "organization": 1.4,
                "individual": 1.3,
            },
            "supply_chain_disruption": {
                "description": "Global supply chain crisis",
                "default": 1.3,
                "vessel": 1.6,
                "organization": 1.5,
                "aircraft": 1.4,
            },
        }
        return configs.get(scenario_name, {"default": 1.2})

    def _calculate_resilience(self, scenario_results: dict[str, dict]) -> dict[str, Any]:
        """Calculate overall resilience score from stress test results."""
        critical_counts = [r["entities_at_critical"] for r in scenario_results.values()]
        high_risk_counts = [r["entities_at_high_risk"] for r in scenario_results.values()]

        return {
            "score": round(
                100 - (np.mean(critical_counts) * 10 + np.mean(high_risk_counts) * 2), 1
            ),
            "rating": (
                "Strong"
                if np.mean(critical_counts) < 1
                else "Moderate"
                if np.mean(critical_counts) < 5
                else "Weak"
            ),
            "worst_scenario": max(
                scenario_results.keys(), key=lambda k: scenario_results[k]["avg_stressed_score"]
            ),
        }

    def _generate_recommendation(self, deltas: dict[str, float]) -> str:
        """Generate recommendation based on deltas."""
        risk_change = deltas.get("avg_risk_score", 0)

        if risk_change > 10:
            return "CRITICAL: This scenario significantly increases risk exposure. Consider additional mitigation measures."
        elif risk_change > 5:
            return "WARNING: Moderate risk increase expected. Monitor affected entities closely."
        elif risk_change < -5:
            return (
                "POSITIVE: This scenario reduces overall risk. Consider implementing these changes."
            )
        else:
            return "NEUTRAL: Minimal impact on overall risk profile."

    def get_simulation(self, simulation_id: str) -> SimulationResult | None:
        """Get simulation result by ID."""
        return self._simulations.get(simulation_id)

    def list_simulations(
        self,
        limit: int = 20,
        simulation_type: SimulationType | None = None,
    ) -> list[dict[str, Any]]:
        """List recent simulations."""
        simulations = list(self._simulations.values())

        if simulation_type:
            simulations = [s for s in simulations if s.simulation_type == simulation_type]

        simulations.sort(key=lambda x: x.started_at, reverse=True)
        return [s.to_dict() for s in simulations[:limit]]

    async def cancel_simulation(self, simulation_id: str) -> bool:
        """Cancel a running simulation."""
        if simulation_id in self._running_tasks:
            self._running_tasks[simulation_id].cancel()
            del self._running_tasks[simulation_id]

        if simulation_id in self._simulations:
            self._simulations[simulation_id].status = SimulationStatus.CANCELLED
            self._simulations[simulation_id].completed_at = datetime.utcnow()
            return True

        return False


# Global instance
simulation_engine = AdvancedSimulationEngine()
