from typing import Optional, List, Dict, Any
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, or_, and_
from sqlalchemy.orm import selectinload

from app.models import Dependency, DependencyLayer, RelationshipType, Entity, AuditLog, AuditAction
from app.schemas.dependency import (
    DependencyCreate,
    DependencyUpdate,
    DependencyResponse,
    DependencyListResponse,
    DependencyGraphResponse,
    DependencyGraphNode,
    DependencyGraphEdge,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


@router.get("", response_model=DependencyListResponse)
async def list_dependencies(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    layer: Optional[DependencyLayer] = None,
    entity_id: Optional[UUID] = None,
    is_active: bool = True,
):
    """List dependencies with pagination and filtering."""
    query = select(Dependency).where(
        Dependency.tenant_id == tenant.id,
        Dependency.is_active == is_active,
    )

    if layer:
        query = query.where(Dependency.layer == layer)

    if entity_id:
        query = query.where(
            or_(
                Dependency.source_entity_id == entity_id,
                Dependency.target_entity_id == entity_id,
            )
        )

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Dependency.created_at.desc())

    result = await db.execute(query)
    dependencies = result.scalars().all()

    return DependencyListResponse(
        items=dependencies,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/graph", response_model=DependencyGraphResponse)
async def get_dependency_graph(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    entity_id: Optional[UUID] = None,
    layer: Optional[DependencyLayer] = None,
    depth: int = Query(2, ge=1, le=5),
):
    """Get dependency graph for visualization."""
    # Get all relevant dependencies
    query = select(Dependency).where(
        Dependency.tenant_id == tenant.id,
        Dependency.is_active == True,
    )

    if layer:
        query = query.where(Dependency.layer == layer)

    result = await db.execute(query)
    dependencies = result.scalars().all()

    # Collect entity IDs
    entity_ids = set()
    for dep in dependencies:
        entity_ids.add(dep.source_entity_id)
        entity_ids.add(dep.target_entity_id)

    # Get entity details
    entity_result = await db.execute(
        select(Entity).where(Entity.id.in_(entity_ids))
    )
    entities = {e.id: e for e in entity_result.scalars().all()}

    # Build nodes
    nodes = []
    for entity_id, entity in entities.items():
        nodes.append(DependencyGraphNode(
            id=str(entity_id),
            label=entity.name,
            type=entity.type.value,
            criticality=entity.criticality,
            metadata={
                "country": entity.country_code,
                "category": entity.category,
            },
        ))

    # Build edges
    edges = []
    for dep in dependencies:
        edges.append(DependencyGraphEdge(
            id=str(dep.id),
            source=str(dep.source_entity_id),
            target=str(dep.target_entity_id),
            layer=dep.layer.value,
            relationship=dep.relationship_type.value,
            criticality=dep.criticality,
            is_bidirectional=dep.is_bidirectional,
        ))

    # Stats
    stats = {
        "total_nodes": len(nodes),
        "total_edges": len(edges),
        "layers": {layer.value: 0 for layer in DependencyLayer},
    }
    for dep in dependencies:
        stats["layers"][dep.layer.value] += 1

    return DependencyGraphResponse(
        nodes=nodes,
        edges=edges,
        stats=stats,
    )


@router.get("/{dependency_id}", response_model=DependencyResponse)
async def get_dependency(
    dependency_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific dependency by ID."""
    result = await db.execute(
        select(Dependency).where(
            Dependency.id == dependency_id,
            Dependency.tenant_id == tenant.id,
        )
    )
    dependency = result.scalar_one_or_none()

    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found",
        )

    return dependency


@router.post("", response_model=DependencyResponse, status_code=status.HTTP_201_CREATED)
async def create_dependency(
    dependency_data: DependencyCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new dependency."""
    # Verify both entities exist and belong to tenant
    for entity_id in [dependency_data.source_entity_id, dependency_data.target_entity_id]:
        result = await db.execute(
            select(Entity).where(
                Entity.id == entity_id,
                Entity.tenant_id == tenant.id,
            )
        )
        if not result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Entity {entity_id} not found",
            )

    # Prevent self-reference
    if dependency_data.source_entity_id == dependency_data.target_entity_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Source and target entities cannot be the same",
        )

    dependency = Dependency(
        tenant_id=tenant.id,
        **dependency_data.model_dump(),
    )
    db.add(dependency)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="dependency",
        resource_id=dependency.id,
        after_state=dependency_data.model_dump(mode="json"),
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(dependency)

    return dependency


@router.put("/{dependency_id}", response_model=DependencyResponse)
async def update_dependency(
    dependency_id: UUID,
    dependency_data: DependencyUpdate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Update a dependency."""
    result = await db.execute(
        select(Dependency).where(
            Dependency.id == dependency_id,
            Dependency.tenant_id == tenant.id,
        )
    )
    dependency = result.scalar_one_or_none()

    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found",
        )

    before_state = {
        "layer": dependency.layer.value,
        "relationship_type": dependency.relationship_type.value,
        "criticality": dependency.criticality,
    }

    update_data = dependency_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(dependency, field, value)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="dependency",
        resource_id=dependency.id,
        before_state=before_state,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(dependency)

    return dependency


@router.delete("/{dependency_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_dependency(
    dependency_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete a dependency (soft delete)."""
    result = await db.execute(
        select(Dependency).where(
            Dependency.id == dependency_id,
            Dependency.tenant_id == tenant.id,
        )
    )
    dependency = result.scalar_one_or_none()

    if not dependency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Dependency not found",
        )

    dependency.is_active = False

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="dependency",
        resource_id=dependency.id,
        success=True,
    )
    db.add(audit)
    await db.commit()


# Phase 2.1: Multi-Layer Dependency Modeling endpoints

@router.get("/layers/summary")
async def get_layer_summary(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """Get summary statistics for each dependency layer."""
    # Count by layer
    layer_query = select(
        Dependency.layer,
        func.count(Dependency.id).label("count"),
        func.avg(Dependency.criticality).label("avg_criticality"),
    ).where(
        Dependency.tenant_id == tenant.id,
        Dependency.is_active == True,
    ).group_by(Dependency.layer)

    result = await db.execute(layer_query)
    layer_stats = {}

    for row in result:
        layer_stats[row.layer.value] = {
            "count": row.count,
            "avg_criticality": round(float(row.avg_criticality or 0), 2),
            "risk_weight": _get_layer_risk_weight(row.layer),
        }

    # Fill in missing layers
    for layer in DependencyLayer:
        if layer.value not in layer_stats:
            layer_stats[layer.value] = {
                "count": 0,
                "avg_criticality": 0,
                "risk_weight": _get_layer_risk_weight(layer),
            }

    return {
        "layers": layer_stats,
        "total_dependencies": sum(s["count"] for s in layer_stats.values()),
        "layer_descriptions": {
            "legal": "Contracts, grants, legal obligations",
            "financial": "Banks, currencies, payment corridors",
            "operational": "Suppliers, logistics, IT systems",
            "human": "Key personnel, irreplaceable staff",
            "academic": "Research partners, funding sources",
        },
    }


@router.get("/cross-layer-impact/{entity_id}")
async def get_cross_layer_impact(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
) -> Dict[str, Any]:
    """
    Calculate cross-layer impact for an entity.

    Shows how disruption to this entity would cascade across different layers.
    """
    # Verify entity exists
    entity_result = await db.execute(
        select(Entity).where(Entity.id == entity_id, Entity.tenant_id == tenant.id)
    )
    entity = entity_result.scalar_one_or_none()
    if not entity:
        raise HTTPException(status_code=404, detail="Entity not found")

    # Get all dependencies where this entity is the source (outgoing)
    outgoing_query = select(Dependency).where(
        Dependency.tenant_id == tenant.id,
        Dependency.source_entity_id == entity_id,
        Dependency.is_active == True,
    )
    outgoing_result = await db.execute(outgoing_query)
    outgoing_deps = outgoing_result.scalars().all()

    # Get all dependencies where this entity is the target (incoming)
    incoming_query = select(Dependency).where(
        Dependency.tenant_id == tenant.id,
        Dependency.target_entity_id == entity_id,
        Dependency.is_active == True,
    )
    incoming_result = await db.execute(incoming_query)
    incoming_deps = incoming_result.scalars().all()

    # Calculate impact by layer
    layer_impact = {layer.value: {"outgoing": 0, "incoming": 0, "risk_score": 0.0} for layer in DependencyLayer}

    for dep in outgoing_deps:
        layer_impact[dep.layer.value]["outgoing"] += 1
        layer_impact[dep.layer.value]["risk_score"] += dep.criticality * _get_layer_risk_weight(dep.layer)

    for dep in incoming_deps:
        layer_impact[dep.layer.value]["incoming"] += 1
        layer_impact[dep.layer.value]["risk_score"] += dep.criticality * _get_layer_risk_weight(dep.layer) * 0.5

    # Calculate total cross-layer risk
    total_risk = sum(li["risk_score"] for li in layer_impact.values())
    primary_layer = max(layer_impact.items(), key=lambda x: x[1]["risk_score"])[0] if layer_impact else "operational"

    # Get affected entities
    affected_entity_ids = set()
    for dep in outgoing_deps:
        affected_entity_ids.add(dep.target_entity_id)
    for dep in incoming_deps:
        affected_entity_ids.add(dep.source_entity_id)

    return {
        "entity_id": str(entity_id),
        "entity_name": entity.name,
        "layer_impact": layer_impact,
        "total_cross_layer_risk": round(total_risk, 2),
        "primary_exposure_layer": primary_layer,
        "total_outgoing": len(outgoing_deps),
        "total_incoming": len(incoming_deps),
        "unique_entities_affected": len(affected_entity_ids),
        "recommendation": _get_risk_recommendation(total_risk, primary_layer),
    }


def _get_layer_risk_weight(layer: DependencyLayer) -> float:
    """Get risk weight multiplier for each layer."""
    weights = {
        DependencyLayer.LEGAL: 1.5,
        DependencyLayer.FINANCIAL: 1.4,
        DependencyLayer.OPERATIONAL: 1.0,
        DependencyLayer.HUMAN: 1.2,
        DependencyLayer.ACADEMIC: 0.8,
    }
    return weights.get(layer, 1.0)


def _get_risk_recommendation(total_risk: float, primary_layer: str) -> str:
    """Generate risk recommendation based on cross-layer analysis."""
    if total_risk > 50:
        return f"HIGH PRIORITY: Entity has significant cross-layer exposure, primarily in {primary_layer}. Recommend immediate diversification strategy."
    elif total_risk > 25:
        return f"MEDIUM PRIORITY: Notable dependency concentration in {primary_layer} layer. Consider backup arrangements."
    elif total_risk > 10:
        return f"LOW PRIORITY: Moderate {primary_layer} dependencies. Monitor for changes."
    else:
        return "MINIMAL: Low cross-layer exposure. Standard monitoring sufficient."
