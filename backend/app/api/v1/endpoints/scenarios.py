from typing import Optional, List
from uuid import UUID
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status, Query, BackgroundTasks
from sqlalchemy import select, func

from app.models import Scenario, ScenarioStatus, ScenarioType, AuditLog, AuditAction
from app.schemas.scenario import (
    ScenarioCreate,
    ScenarioUpdate,
    ScenarioResponse,
    ScenarioResult,
    ScenarioListResponse,
    ScenarioArchiveRequest,
)
from app.api.v1.deps import DB, CurrentUser, CurrentTenant, RequireWriter


router = APIRouter()


@router.get("", response_model=ScenarioListResponse)
async def list_scenarios(
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    status: Optional[ScenarioStatus] = None,
    type: Optional[ScenarioType] = None,
    include_archived: bool = False,
):
    """List scenarios with pagination and filtering."""
    query = select(Scenario).where(Scenario.tenant_id == tenant.id)

    if status:
        query = query.where(Scenario.status == status)

    if type:
        query = query.where(Scenario.type == type)

    if not include_archived:
        query = query.where(Scenario.archived_at.is_(None))

    # Count total
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # Paginate
    query = query.offset((page - 1) * page_size).limit(page_size)
    query = query.order_by(Scenario.created_at.desc())

    result = await db.execute(query)
    scenarios = result.scalars().all()

    return ScenarioListResponse(
        items=scenarios,
        total=total,
        page=page,
        page_size=page_size,
        pages=(total + page_size - 1) // page_size,
    )


@router.get("/{scenario_id}", response_model=ScenarioResponse)
async def get_scenario(
    scenario_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get a specific scenario by ID."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    return scenario


@router.get("/{scenario_id}/results", response_model=ScenarioResult)
async def get_scenario_results(
    scenario_id: UUID,
    db: DB,
    current_user: CurrentUser,
    tenant: CurrentTenant,
):
    """Get detailed results of a completed scenario."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    if scenario.status != ScenarioStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Scenario is not completed. Current status: {scenario.status.value}",
        )

    results = scenario.results or {}

    return ScenarioResult(
        scenario_id=scenario.id,
        status=scenario.status,
        summary=results.get("summary", ""),
        severity=results.get("severity", "MEDIUM"),
        impacted_entities=results.get("impacted_entities", []),
        risk_score_changes=results.get("risk_score_changes", {}),
        cascading_effects=scenario.cascade_results.get("effects", []) if scenario.cascade_results else [],
        recommendations=results.get("recommendations", []),
        execution_time_seconds=scenario.duration_seconds,
    )


@router.post("", response_model=ScenarioResponse, status_code=status.HTTP_201_CREATED)
async def create_scenario(
    scenario_data: ScenarioCreate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Create a new scenario."""
    scenario = Scenario(
        tenant_id=tenant.id,
        created_by=current_user.id,
        status=ScenarioStatus.DRAFT,
        **scenario_data.model_dump(),
    )
    db.add(scenario)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.CREATE,
        resource_type="scenario",
        resource_id=scenario.id,
        resource_name=scenario.name,
        after_state=scenario_data.model_dump(mode="json"),
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(scenario)

    return scenario


@router.put("/{scenario_id}", response_model=ScenarioResponse)
async def update_scenario(
    scenario_id: UUID,
    scenario_data: ScenarioUpdate,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Update a scenario (only if in DRAFT status)."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    if scenario.status != ScenarioStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only update scenarios in DRAFT status",
        )

    update_data = scenario_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(scenario, field, value)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.UPDATE,
        resource_type="scenario",
        resource_id=scenario.id,
        resource_name=scenario.name,
        after_state=update_data,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(scenario)

    return scenario


@router.post("/{scenario_id}/run", response_model=ScenarioResponse)
async def run_scenario(
    scenario_id: UUID,
    background_tasks: BackgroundTasks,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Execute a scenario simulation."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    if scenario.status not in [ScenarioStatus.DRAFT, ScenarioStatus.FAILED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Cannot run scenario in {scenario.status.value} status",
        )

    # Update status to running
    scenario.status = ScenarioStatus.RUNNING
    scenario.started_at = datetime.now(timezone.utc)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.SCENARIO_RUN,
        resource_type="scenario",
        resource_id=scenario.id,
        resource_name=scenario.name,
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(scenario)

    # Run simulation in background
    from app.services.scenario_simulator import ScenarioSimulator
    simulator = ScenarioSimulator(db, tenant)
    background_tasks.add_task(simulator.run, scenario.id)

    return scenario


@router.post("/{scenario_id}/archive", response_model=ScenarioResponse)
async def archive_scenario(
    scenario_id: UUID,
    archive_data: ScenarioArchiveRequest,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Archive a completed scenario with lessons learned (Phase 2: Institutional Memory)."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    if scenario.status != ScenarioStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only archive completed scenarios",
        )

    scenario.status = ScenarioStatus.ARCHIVED
    scenario.archived_at = datetime.now(timezone.utc)
    scenario.outcome_notes = archive_data.outcome_notes
    scenario.lessons_learned = archive_data.lessons_learned

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.SCENARIO_ARCHIVE,
        resource_type="scenario",
        resource_id=scenario.id,
        resource_name=scenario.name,
        after_state={
            "outcome_notes": archive_data.outcome_notes,
            "lessons_learned": archive_data.lessons_learned,
        },
        success=True,
    )
    db.add(audit)
    await db.commit()
    await db.refresh(scenario)

    return scenario


@router.delete("/{scenario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scenario(
    scenario_id: UUID,
    db: DB,
    current_user: RequireWriter,
    tenant: CurrentTenant,
):
    """Delete a scenario (only if in DRAFT status)."""
    result = await db.execute(
        select(Scenario).where(
            Scenario.id == scenario_id,
            Scenario.tenant_id == tenant.id,
        )
    )
    scenario = result.scalar_one_or_none()

    if not scenario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Scenario not found",
        )

    if scenario.status != ScenarioStatus.DRAFT:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only delete scenarios in DRAFT status. Use archive for completed scenarios.",
        )

    await db.delete(scenario)

    # Audit log
    audit = AuditLog(
        tenant_id=tenant.id,
        user_id=current_user.id,
        user_email=current_user.email,
        user_role=current_user.role,
        action=AuditAction.DELETE,
        resource_type="scenario",
        resource_id=scenario_id,
        resource_name=scenario.name,
        success=True,
    )
    db.add(audit)
    await db.commit()
