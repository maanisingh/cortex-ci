from datetime import date, timedelta
from typing import Optional, List
from uuid import UUID

from fastapi import APIRouter, HTTPException, status, Query
from sqlalchemy import select, func, or_

from app.models import Constraint, ConstraintType, ConstraintSeverity, AuditLog, AuditAction
from app.schemas.constraint import (
    ConstraintCreate,
    ConstraintUpdate,
    ConstraintResponse,
    ConstraintListResponse,
    ConstraintSummary,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


@router.get("", response_model=ConstraintListResponse)
async def list_constraints(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    type: Optional[ConstraintType] = None,
    severity: Optional[ConstraintSeverity] = None,
    search: Optional[str] = None,
    is_active: bool = True,
    is_mandatory: Optional[bool] = None,
):
    """List constraints with pagination and filtering."""
    query = select(Constraint).where(
        Constraint.tenant_id == tenant.id,
        Constraint.is_active == is_active,
    )

    if type:
        query = query.where(Constraint.type == type)

    if severity:
        query = query.where(Constraint.severity == severity)

    if is_mandatory is not None:
        query = query.where(Constraint.is_mandatory == is_mandatory)

    if search:
        search_filter = or_(
            Constraint.name.ilike(f"%{search}%"),
            Constraint.description.ilike(f"%{search}%"),
            Constraint.reference_code.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Constraint.created_at.desc())

    result = await db.execute(query)
    constraints = result.scalars().all()

    return ConstraintListResponse(
        items=constraints,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/summary", response_model=ConstraintSummary)
async def get_constraint_summary(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get summary of all constraints."""
    # Get all active constraints
    result = await db.execute(
        select(Constraint).where(
            Constraint.tenant_id == tenant.id,
            Constraint.is_active == True,
        )
    )
    constraints = result.scalars().all()

    # Count by type
    by_type = {}
    for ct in ConstraintType:
        by_type[ct.value] = sum(1 for c in constraints if c.type == ct)

    # Count by severity
    by_severity = {}
    for cs in ConstraintSeverity:
        by_severity[cs.value] = sum(1 for c in constraints if c.severity == cs)

    # Expiring soon (within 30 days)
    today = date.today()
    thirty_days = today + timedelta(days=30)
    expiring_soon = sum(
        1 for c in constraints
        if c.expiry_date and today <= c.expiry_date <= thirty_days
    )

    return ConstraintSummary(
        total=len(constraints),
        by_type=by_type,
        by_severity=by_severity,
        active=len(constraints),
        expiring_soon=expiring_soon,
        mandatory=sum(1 for c in constraints if c.is_mandatory),
    )


@router.get("/{constraint_id}", response_model=ConstraintResponse)
async def get_constraint(
    constraint_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific constraint by ID."""
    result = await db.execute(
        select(Constraint).where(
            Constraint.id == constraint_id,
            Constraint.tenant_id == tenant.id,
        )
    )
    constraint = result.scalar_one_or_none()

    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constraint not found",
        )

    return constraint


@router.post("", response_model=ConstraintResponse, status_code=status.HTTP_201_CREATED)
async def create_constraint(
    constraint_data: ConstraintCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new constraint."""
    constraint = Constraint(
        tenant_id=tenant.id,
        created_by=current_user.id,
        **constraint_data.model_dump(),
    )
    db.add(constraint)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="constraint",
        resource_id=constraint.id,
        resource_name=constraint.name,
        after_state=constraint_data.model_dump(mode="json"),
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(constraint)

    return constraint


@router.put("/{constraint_id}", response_model=ConstraintResponse)
async def update_constraint(
    constraint_id: UUID,
    constraint_data: ConstraintUpdate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Update a constraint."""
    result = await db.execute(
        select(Constraint).where(
            Constraint.id == constraint_id,
            Constraint.tenant_id == tenant.id,
        )
    )
    constraint = result.scalar_one_or_none()

    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constraint not found",
        )

    before_state = {
        "name": constraint.name,
        "type": constraint.type.value,
        "severity": constraint.severity.value,
        "is_active": constraint.is_active,
    }

    update_data = constraint_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(constraint, field, value)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="constraint",
        resource_id=constraint.id,
        resource_name=constraint.name,
        before_state=before_state,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(constraint)

    return constraint


@router.delete("/{constraint_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_constraint(
    constraint_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete a constraint (soft delete)."""
    result = await db.execute(
        select(Constraint).where(
            Constraint.id == constraint_id,
            Constraint.tenant_id == tenant.id,
        )
    )
    constraint = result.scalar_one_or_none()

    if not constraint:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Constraint not found",
        )

    constraint.is_active = False

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="constraint",
        resource_id=constraint.id,
        resource_name=constraint.name,
        success=True,
    )
    db.add(audit)
    await db.commit()
