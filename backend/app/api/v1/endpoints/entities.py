from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.models import Entity, EntityType, AuditLog, AuditAction
from app.schemas.entity import (
    EntityCreate,
    EntityUpdate,
    EntityResponse,
    EntityListResponse,
    EntityBulkImportRequest,
    EntityBulkImportResponse,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


@router.get("", response_model=EntityListResponse)
async def list_entities(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=500),
    type: Optional[EntityType] = None,
    search: Optional[str] = None,
    country_code: Optional[str] = None,
    is_active: bool = True,
):
    """List entities with pagination and filtering."""
    query = select(Entity).where(
        Entity.tenant_id == tenant.id,
        Entity.is_active == is_active,
    )

    if type:
        query = query.where(Entity.type == type)

    if country_code:
        query = query.where(Entity.country_code == country_code)

    if search:
        search_filter = or_(
            Entity.name.ilike(f"%{search}%"),
            Entity.external_id.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Entity.created_at.desc())

    result = await db.execute(query)
    entities = result.scalars().all()

    return EntityListResponse(
        items=entities,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{entity_id}", response_model=EntityResponse)
async def get_entity(
    entity_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific entity by ID."""
    result = await db.execute(
        select(Entity).where(
            Entity.id == entity_id,
            Entity.tenant_id == tenant.id,
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )

    return entity


@router.post("", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(
    entity_data: EntityCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new entity."""
    entity = Entity(
        tenant_id=tenant.id,
        **entity_data.model_dump(),
    )
    db.add(entity)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="entity",
        resource_id=entity.id,
        resource_name=entity.name,
        after_state=entity_data.model_dump(),
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(entity)

    return entity


@router.put("/{entity_id}", response_model=EntityResponse)
async def update_entity(
    entity_id: UUID,
    entity_data: EntityUpdate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Update an entity."""
    result = await db.execute(
        select(Entity).where(
            Entity.id == entity_id,
            Entity.tenant_id == tenant.id,
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )

    before_state = {
        "name": entity.name,
        "aliases": entity.aliases,
        "country_code": entity.country_code,
        "criticality": entity.criticality,
    }

    update_data = entity_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(entity, field, value)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="entity",
        resource_id=entity.id,
        resource_name=entity.name,
        before_state=before_state,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(entity)

    return entity


@router.delete("/{entity_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_entity(
    entity_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete an entity (soft delete)."""
    result = await db.execute(
        select(Entity).where(
            Entity.id == entity_id,
            Entity.tenant_id == tenant.id,
        )
    )
    entity = result.scalar_one_or_none()

    if not entity:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Entity not found",
        )

    entity.is_active = False

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="entity",
        resource_id=entity.id,
        resource_name=entity.name,
        success=True,
    )
    db.add(audit)
    await db.commit()


@router.post("/bulk-import", response_model=EntityBulkImportResponse)
async def bulk_import_entities(
    import_data: EntityBulkImportRequest,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Bulk import entities."""
    imported = 0
    skipped = 0
    errors = []

    for idx, entity_data in enumerate(import_data.entities):
        try:
            # Check for duplicates by name
            if import_data.skip_duplicates:
                result = await db.execute(
                    select(Entity).where(
                        Entity.tenant_id == tenant.id,
                        Entity.name == entity_data.name,
                        Entity.type == entity_data.type,
                    )
                )
                if result.scalar_one_or_none():
                    skipped += 1
                    continue

            entity = Entity(
                tenant_id=tenant.id,
                **entity_data.model_dump(),
            )
            db.add(entity)
            imported += 1

        except Exception as e:
            errors.append({
                "index": idx,
                "name": entity_data.name,
                "error": str(e),
            })

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.ENTITY_IMPORT,
        description=f"Bulk import: {imported} imported, {skipped} skipped, {len(errors)} errors",
        metadata={"imported": imported, "skipped": skipped, "error_count": len(errors)},
        success=len(errors) == 0,
    )
    db.add(audit)
    await db.commit()

    return EntityBulkImportResponse(
        imported=imported,
        skipped=skipped,
        errors=errors,
    )
