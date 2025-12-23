from typing import Optional, List
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
