"""Incident Management API Endpoints"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.incident import (
    Incident,
    IncidentStatus,
    IncidentTimeline,
)

router = APIRouter()


class IncidentCreate(BaseModel):
    title: str
    description: str
    category: str
    severity: str
    detection_method: str | None = None
    affected_systems: list[str] = []


class IncidentResponseSchema(BaseModel):
    id: UUID
    incident_ref: str
    title: str
    category: str
    severity: str
    status: str
    detected_at: datetime
    is_breach: bool

    class Config:
        from_attributes = True


@router.get("/", response_model=list[IncidentResponseSchema])
async def list_incidents(
    category: str | None = Query(None),
    severity: str | None = Query(None),
    status: str | None = Query(None),
    is_breach: bool | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Incident).where(Incident.tenant_id == tenant_id)
    if category:
        query = query.where(Incident.category == category)
    if severity:
        query = query.where(Incident.severity == severity)
    if status:
        query = query.where(Incident.status == status)
    if is_breach is not None:
        query = query.where(Incident.is_breach == is_breach)
    result = await db.execute(query.order_by(Incident.detected_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/", response_model=IncidentResponseSchema, status_code=status.HTTP_201_CREATED)
async def create_incident(
    incident: IncidentCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    incident_id = uuid4()
    now = datetime.now(UTC)
    db_incident = Incident(
        id=incident_id,
        tenant_id=tenant_id,
        incident_ref=f"INC-{str(incident_id)[:8].upper()}",
        title=incident.title,
        description=incident.description,
        category=incident.category,
        severity=incident.severity,
        status=IncidentStatus.NEW,
        detected_at=now,
        reported_at=now,
        detection_method=incident.detection_method,
        affected_systems=incident.affected_systems,
        is_breach=False,
    )
    db.add(db_incident)

    # Add initial timeline entry
    timeline = IncidentTimeline(
        id=uuid4(),
        tenant_id=tenant_id,
        incident_id=incident_id,
        timestamp=now,
        entry_type="EVENT",
        title="Incident created",
        description=f"Incident reported: {incident.title}",
    )
    db.add(timeline)

    await db.commit()
    await db.refresh(db_incident)
    return db_incident


@router.get("/{incident_id}", response_model=IncidentResponseSchema)
async def get_incident(
    incident_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Incident).where(and_(Incident.id == incident_id, Incident.tenant_id == tenant_id))
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@router.patch("/{incident_id}/status")
async def update_incident_status(
    incident_id: UUID,
    new_status: str = Query(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Incident).where(and_(Incident.id == incident_id, Incident.tenant_id == tenant_id))
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    old_status = incident.status
    incident.status = new_status

    if new_status == "CONTAINMENT":
        incident.contained_at = datetime.now(UTC)
    elif new_status == "CLOSED":
        incident.closed_at = datetime.now(UTC)

    # Add timeline entry
    timeline = IncidentTimeline(
        id=uuid4(),
        tenant_id=tenant_id,
        incident_id=incident_id,
        timestamp=datetime.now(UTC),
        entry_type="STATUS_CHANGE",
        title=f"Status changed: {old_status} -> {new_status}",
    )
    db.add(timeline)

    await db.commit()
    return {"message": "Status updated", "new_status": new_status}


@router.patch("/{incident_id}/breach")
async def mark_as_breach(
    incident_id: UUID,
    is_breach: bool = Query(...),
    notes: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Incident).where(and_(Incident.id == incident_id, Incident.tenant_id == tenant_id))
    )
    incident = result.scalar_one_or_none()
    if not incident:
        raise HTTPException(status_code=404, detail="Incident not found")

    incident.is_breach = is_breach
    incident.breach_determination_notes = notes
    incident.breach_determined_at = datetime.now(UTC)

    await db.commit()
    return {"message": "Breach determination updated", "is_breach": is_breach}
