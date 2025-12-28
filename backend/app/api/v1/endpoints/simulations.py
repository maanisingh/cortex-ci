"""
Simulation API Endpoints (Phase 5.1)
Advanced simulation and analysis endpoints.
"""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_user
from app.core.database import get_db
from app.models import User
from app.services.advanced_simulation import (
    MonteCarloConfig,
    SimulationType,
    WhatIfScenario,
    simulation_engine,
)

router = APIRouter()


class MonteCarloRequest(BaseModel):
    """Request for Monte Carlo simulation."""

    entity_ids: list[UUID] | None = Field(None, description="Specific entities to simulate")
    iterations: int = Field(1000, ge=100, le=10000)
    confidence_level: float = Field(0.95, ge=0.8, le=0.99)
    risk_volatility: float = Field(0.15, ge=0.01, le=0.5)
    seed: int | None = None


class CascadeRequest(BaseModel):
    """Request for cascade analysis."""

    trigger_entity_id: UUID
    max_depth: int = Field(5, ge=1, le=10)


class WhatIfRequest(BaseModel):
    """Request for what-if analysis."""

    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field("", max_length=500)
    constraint_changes: list[dict] = Field(default_factory=list)
    entity_changes: list[dict] = Field(default_factory=list)
    global_modifiers: dict = Field(default_factory=dict)


class StressTestRequest(BaseModel):
    """Request for stress test."""

    scenarios: list[str] | None = Field(None, description="Stress scenarios to run")


@router.post("/monte-carlo")
async def run_monte_carlo_simulation(
    request: MonteCarloRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run Monte Carlo simulation for risk score distribution analysis.

    Returns probabilistic outcomes including:
    - Per-entity risk distributions
    - Portfolio-level statistics
    - Value at Risk (VaR) metrics
    - Confidence intervals
    """
    config = MonteCarloConfig(
        iterations=request.iterations,
        confidence_level=request.confidence_level,
        risk_volatility=request.risk_volatility,
        seed=request.seed,
    )

    result = await simulation_engine.run_monte_carlo(
        db=db,
        tenant_id=current_user.tenant_id,
        entity_ids=request.entity_ids,
        config=config,
    )

    return result.to_dict()


@router.post("/cascade")
async def run_cascade_analysis(
    request: CascadeRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Analyze cascade effects when an entity's risk changes.

    Returns:
    - Cascade paths showing how risk propagates
    - Impact factors for each affected entity
    - Depth analysis of the cascade
    """
    result = await simulation_engine.run_cascade_analysis(
        db=db,
        tenant_id=current_user.tenant_id,
        trigger_entity_id=request.trigger_entity_id,
        max_depth=request.max_depth,
    )

    return result.to_dict()


@router.post("/what-if")
async def run_what_if_analysis(
    request: WhatIfRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run what-if scenario analysis.

    Allows testing hypothetical changes:
    - Constraint modifications
    - Entity risk adjustments
    - Global risk multipliers

    Returns comparison of current vs projected state.
    """
    scenario = WhatIfScenario(
        name=request.name,
        description=request.description,
        constraint_changes=request.constraint_changes,
        entity_changes=request.entity_changes,
        global_modifiers=request.global_modifiers,
    )

    result = await simulation_engine.run_what_if_analysis(
        db=db,
        tenant_id=current_user.tenant_id,
        scenario=scenario,
    )

    return result.to_dict()


@router.post("/stress-test")
async def run_stress_test(
    request: StressTestRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Run stress test scenarios.

    Default scenarios:
    - regulatory_crackdown: Major regulatory enforcement
    - market_crisis: Severe market downturn
    - geopolitical_event: Major geopolitical disruption
    - supply_chain_disruption: Global supply chain crisis

    Returns resilience scores and impact analysis.
    """
    result = await simulation_engine.run_stress_test(
        db=db,
        tenant_id=current_user.tenant_id,
        stress_scenarios=request.scenarios,
    )

    return result.to_dict()


@router.get("/{simulation_id}")
async def get_simulation(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Get simulation result by ID."""
    result = simulation_engine.get_simulation(simulation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found",
        )
    return result.to_dict()


@router.get("/")
async def list_simulations(
    limit: int = 20,
    simulation_type: SimulationType | None = None,
    current_user: User = Depends(get_current_user),
):
    """List recent simulations."""
    return {
        "simulations": simulation_engine.list_simulations(
            limit=limit,
            simulation_type=simulation_type,
        )
    }


@router.delete("/{simulation_id}")
async def cancel_simulation(
    simulation_id: str,
    current_user: User = Depends(get_current_user),
):
    """Cancel a running simulation."""
    success = await simulation_engine.cancel_simulation(simulation_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Simulation not found or already completed",
        )
    return {"status": "cancelled", "simulation_id": simulation_id}
