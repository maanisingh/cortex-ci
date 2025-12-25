"""Phase 2.2: Scenario Chains API - Cascading effect simulation."""

from typing import Optional, List
from uuid import UUID
from decimal import Decimal
from datetime import datetime

from fastapi import APIRouter, HTTPException, status, Query
from pydantic import BaseModel
from sqlalchemy import select

from app.models import (
    ScenarioChain,
    ChainEffect,
    EffectSeverity,
    Entity,
    Dependency,
    DependencyLayer,
    AuditLog,
    AuditAction,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


# Schemas
class ChainEffectCreate(BaseModel):
    entity_id: UUID
    effect_description: str
    severity: EffectSeverity
    cascade_depth: int = 1
    time_delay_days: int = 0
    risk_score_delta: float = 0.0
    probability: float = 1.0
    caused_by_effect_id: Optional[UUID] = None
    notes: Optional[str] = None


class ScenarioChainCreate(BaseModel):
    name: str
    description: Optional[str] = None
    trigger_event: str
    trigger_entity_id: Optional[UUID] = None


class ScenarioChainResponse(BaseModel):
    id: UUID
    name: str
    description: Optional[str]
    trigger_event: str
    trigger_entity_id: Optional[UUID]
    total_entities_affected: int
    max_cascade_depth: int
    estimated_timeline_days: int
    overall_severity: str
    total_risk_increase: float
    is_active: bool
    last_simulated_at: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ChainEffectResponse(BaseModel):
    id: UUID
    entity_id: UUID
    entity_name: Optional[str] = None
    effect_description: str
    severity: str
    cascade_depth: int
    time_delay_days: int
    risk_score_delta: float
    probability: float
    caused_by_effect_id: Optional[UUID]

    class Config:
        from_attributes = True


class CascadeSimulationResult(BaseModel):
    scenario_chain_id: UUID
    trigger_event: str
    immediate_effects: List[ChainEffectResponse]
    delayed_effects: List[ChainEffectResponse]
    total_entities_affected: int
    max_cascade_depth: int
    estimated_timeline_days: int
    overall_severity: str
    risk_impact_summary: dict


@router.get("", response_model=List[ScenarioChainResponse])
async def list_scenario_chains(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
):
    """List all scenario chains."""
    query = (
        select(ScenarioChain)
        .where(
            ScenarioChain.tenant_id == tenant.id,
            ScenarioChain.is_active,
        )
        .offset((page - 1) * page_size)
        .limit(page_size)
    )

    result = await db.execute(query)
    return result.scalars().all()


@router.post(
    "", response_model=ScenarioChainResponse, status_code=status.HTTP_201_CREATED
)
async def create_scenario_chain(
    data: ScenarioChainCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new scenario chain."""
    chain = ScenarioChain(
        tenant_id=tenant.id,
        name=data.name,
        description=data.description,
        trigger_event=data.trigger_event,
        trigger_entity_id=data.trigger_entity_id,
    )
    db.add(chain)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="scenario_chain",
        resource_id=chain.id,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(chain)

    return chain


@router.get("/{chain_id}", response_model=ScenarioChainResponse)
async def get_scenario_chain(
    chain_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific scenario chain."""
    result = await db.execute(
        select(ScenarioChain).where(
            ScenarioChain.id == chain_id,
            ScenarioChain.tenant_id == tenant.id,
        )
    )
    chain = result.scalar_one_or_none()

    if not chain:
        raise HTTPException(status_code=404, detail="Scenario chain not found")

    return chain


@router.get("/{chain_id}/effects", response_model=List[ChainEffectResponse])
async def get_chain_effects(
    chain_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get all effects in a scenario chain."""
    # Verify chain exists
    chain_result = await db.execute(
        select(ScenarioChain).where(
            ScenarioChain.id == chain_id,
            ScenarioChain.tenant_id == tenant.id,
        )
    )
    if not chain_result.scalar_one_or_none():
        raise HTTPException(status_code=404, detail="Scenario chain not found")

    # Get effects with entity names
    result = await db.execute(
        select(ChainEffect, Entity.name)
        .join(Entity, ChainEffect.entity_id == Entity.id)
        .where(
            ChainEffect.scenario_chain_id == chain_id,
        )
        .order_by(ChainEffect.cascade_depth, ChainEffect.time_delay_days)
    )

    effects = []
    for effect, entity_name in result:
        effects.append(
            ChainEffectResponse(
                id=effect.id,
                entity_id=effect.entity_id,
                entity_name=entity_name,
                effect_description=effect.effect_description,
                severity=effect.severity.value,
                cascade_depth=effect.cascade_depth,
                time_delay_days=effect.time_delay_days,
                risk_score_delta=float(effect.risk_score_delta),
                probability=float(effect.probability),
                caused_by_effect_id=effect.caused_by_effect_id,
            )
        )

    return effects


@router.post(
    "/{chain_id}/effects",
    response_model=ChainEffectResponse,
    status_code=status.HTTP_201_CREATED,
)
async def add_chain_effect(
    chain_id: UUID,
    data: ChainEffectCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Add an effect to a scenario chain."""
    # Verify chain exists
    chain_result = await db.execute(
        select(ScenarioChain).where(
            ScenarioChain.id == chain_id,
            ScenarioChain.tenant_id == tenant.id,
        )
    )
    chain = chain_result.scalar_one_or_none()
    if not chain:
        raise HTTPException(status_code=404, detail="Scenario chain not found")

    # Verify entity exists
    entity_result = await db.execute(
        select(Entity).where(Entity.id == data.entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=400, detail="Entity not found")

    effect = ChainEffect(
        scenario_chain_id=chain_id,
        entity_id=data.entity_id,
        effect_description=data.effect_description,
        severity=data.severity,
        cascade_depth=data.cascade_depth,
        time_delay_days=data.time_delay_days,
        risk_score_delta=Decimal(str(data.risk_score_delta)),
        probability=Decimal(str(data.probability)),
        caused_by_effect_id=data.caused_by_effect_id,
        notes=data.notes,
    )
    db.add(effect)

    # Update chain stats
    chain.total_entities_affected = (chain.total_entities_affected or 0) + 1
    chain.max_cascade_depth = max(chain.max_cascade_depth or 0, data.cascade_depth)
    chain.estimated_timeline_days = max(
        chain.estimated_timeline_days or 0, data.time_delay_days
    )

    await db.commit()
    await db.refresh(effect)

    return ChainEffectResponse(
        id=effect.id,
        entity_id=effect.entity_id,
        entity_name=entity.name,
        effect_description=effect.effect_description,
        severity=effect.severity.value,
        cascade_depth=effect.cascade_depth,
        time_delay_days=effect.time_delay_days,
        risk_score_delta=float(effect.risk_score_delta),
        probability=float(effect.probability),
        caused_by_effect_id=effect.caused_by_effect_id,
    )


@router.post("/{chain_id}/simulate", response_model=CascadeSimulationResult)
async def simulate_cascade(
    chain_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    max_depth: int = Query(3, ge=1, le=5),
):
    """
    Simulate cascading effects from a scenario chain.

    This automatically discovers second and third-order effects
    by following dependency relationships.
    """
    # Get the scenario chain
    chain_result = await db.execute(
        select(ScenarioChain).where(
            ScenarioChain.id == chain_id,
            ScenarioChain.tenant_id == tenant.id,
        )
    )
    chain = chain_result.scalar_one_or_none()
    if not chain:
        raise HTTPException(status_code=404, detail="Scenario chain not found")

    # Get existing effects (first-order)
    effects_result = await db.execute(
        select(ChainEffect, Entity.name)
        .join(Entity, ChainEffect.entity_id == Entity.id)
        .where(ChainEffect.scenario_chain_id == chain_id)
    )
    existing_effects = list(effects_result)

    # Collect affected entity IDs
    affected_entities = {e[0].entity_id for e in existing_effects}
    immediate_effects = []
    delayed_effects = []

    for effect, entity_name in existing_effects:
        effect_response = ChainEffectResponse(
            id=effect.id,
            entity_id=effect.entity_id,
            entity_name=entity_name,
            effect_description=effect.effect_description,
            severity=effect.severity.value,
            cascade_depth=effect.cascade_depth,
            time_delay_days=effect.time_delay_days,
            risk_score_delta=float(effect.risk_score_delta),
            probability=float(effect.probability),
            caused_by_effect_id=effect.caused_by_effect_id,
        )
        if effect.time_delay_days == 0:
            immediate_effects.append(effect_response)
        else:
            delayed_effects.append(effect_response)

    # Simulate cascading effects through dependencies
    current_depth_entities = affected_entities.copy()
    total_risk_delta = sum(float(e[0].risk_score_delta) for e in existing_effects)
    severity_counts = {s.value: 0 for s in EffectSeverity}

    for effect, _ in existing_effects:
        severity_counts[effect.severity.value] += 1

    for depth in range(2, max_depth + 1):
        # Find entities that depend on currently affected entities
        deps_result = await db.execute(
            select(Dependency, Entity)
            .join(Entity, Dependency.target_entity_id == Entity.id)
            .where(
                Dependency.tenant_id == tenant.id,
                Dependency.is_active,
                Dependency.source_entity_id.in_(current_depth_entities),
                ~Dependency.target_entity_id.in_(affected_entities),
            )
        )

        new_effects = []
        for dep, entity in deps_result:
            # Calculate derived severity based on criticality
            if dep.criticality >= 5:
                severity = EffectSeverity.SEVERE
            elif dep.criticality >= 4:
                severity = EffectSeverity.SIGNIFICANT
            elif dep.criticality >= 3:
                severity = EffectSeverity.MODERATE
            else:
                severity = EffectSeverity.MINOR

            # Estimate time delay based on layer
            time_delay = {
                DependencyLayer.OPERATIONAL: 7,
                DependencyLayer.FINANCIAL: 14,
                DependencyLayer.LEGAL: 30,
                DependencyLayer.HUMAN: 7,
                DependencyLayer.ACADEMIC: 60,
            }.get(dep.layer, 14) * (depth - 1)

            # Risk delta decreases with depth
            base_risk_delta = 5.0 * (dep.criticality / 5) * (0.7 ** (depth - 1))

            effect_response = ChainEffectResponse(
                id=dep.id,  # Use dependency ID as placeholder
                entity_id=entity.id,
                entity_name=entity.name,
                effect_description=f"Cascading impact via {dep.relationship_type.value} relationship (depth {depth})",
                severity=severity.value,
                cascade_depth=depth,
                time_delay_days=time_delay,
                risk_score_delta=round(base_risk_delta, 2),
                probability=round(0.9**depth, 2),
                caused_by_effect_id=None,
            )

            new_effects.append(effect_response)
            affected_entities.add(entity.id)
            total_risk_delta += base_risk_delta
            severity_counts[severity.value] += 1

        # Sort new effects into immediate vs delayed
        for eff in new_effects:
            if eff.time_delay_days == 0:
                immediate_effects.append(eff)
            else:
                delayed_effects.append(eff)

        current_depth_entities = {e.entity_id for e in new_effects}
        if not current_depth_entities:
            break

    # Determine overall severity
    if severity_counts.get("catastrophic", 0) > 0:
        overall_severity = "catastrophic"
    elif severity_counts.get("severe", 0) > 0:
        overall_severity = "severe"
    elif severity_counts.get("significant", 0) > 0:
        overall_severity = "significant"
    elif severity_counts.get("moderate", 0) > 0:
        overall_severity = "moderate"
    else:
        overall_severity = "minor"

    # Update chain with simulation results
    chain.total_entities_affected = len(affected_entities)
    chain.max_cascade_depth = max_depth
    chain.estimated_timeline_days = max(
        (e.time_delay_days for e in immediate_effects + delayed_effects), default=0
    )
    chain.overall_severity = EffectSeverity(overall_severity)
    chain.total_risk_increase = Decimal(str(round(total_risk_delta, 2)))
    chain.last_simulated_at = datetime.utcnow()

    await db.commit()

    return CascadeSimulationResult(
        scenario_chain_id=chain.id,
        trigger_event=chain.trigger_event,
        immediate_effects=immediate_effects,
        delayed_effects=sorted(delayed_effects, key=lambda x: x.time_delay_days),
        total_entities_affected=len(affected_entities),
        max_cascade_depth=max(
            (e.cascade_depth for e in immediate_effects + delayed_effects), default=1
        ),
        estimated_timeline_days=max(
            (e.time_delay_days for e in immediate_effects + delayed_effects), default=0
        ),
        overall_severity=overall_severity,
        risk_impact_summary={
            "total_risk_increase": round(total_risk_delta, 2),
            "severity_distribution": severity_counts,
            "layers_affected": ["operational", "financial", "legal"],
        },
    )


@router.delete("/{chain_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario_chain(
    chain_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete a scenario chain (soft delete)."""
    result = await db.execute(
        select(ScenarioChain).where(
            ScenarioChain.id == chain_id,
            ScenarioChain.tenant_id == tenant.id,
        )
    )
    chain = result.scalar_one_or_none()

    if not chain:
        raise HTTPException(status_code=404, detail="Scenario chain not found")

    chain.is_active = False

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="scenario_chain",
        resource_id=chain.id,
        success=True,
    )
    db.add(audit)
    await db.commit()
