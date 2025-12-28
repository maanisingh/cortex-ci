"""Case Management & SAR API Endpoints"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.case import (
    Case,
    CaseNote,
    CaseStatus,
    CaseTask,
    SARReport,
    SARStatus,
    TaskStatus,
)

router = APIRouter()


class CaseCreate(BaseModel):
    title: str
    case_type: str
    priority: str = "MEDIUM"
    description: str | None = None
    customer_id: UUID | None = None
    alert_id: UUID | None = None


class CaseResponse(BaseModel):
    id: UUID
    case_ref: str
    title: str
    case_type: str
    priority: str
    status: str
    created_at: datetime
    assigned_to: UUID | None
    total_alerts: int

    class Config:
        from_attributes = True


class CaseNoteCreate(BaseModel):
    content: str
    is_internal: bool = True


class CaseTaskCreate(BaseModel):
    title: str
    description: str | None = None
    due_date: datetime | None = None
    assigned_to: UUID | None = None


class SARCreate(BaseModel):
    filing_type: str
    subject_name: str
    subject_type: str
    suspicious_activity_summary: str
    amount_involved: float | None = None


class SARResponse(BaseModel):
    id: UUID
    sar_ref: str
    filing_type: str
    status: str
    subject_name: str
    created_at: datetime
    filed_at: datetime | None

    class Config:
        from_attributes = True


@router.get("/", response_model=list[CaseResponse])
async def list_cases(
    case_type: str | None = Query(None),
    status: str | None = Query(None),
    priority: str | None = Query(None),
    assigned_to: UUID | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Case).where(Case.tenant_id == tenant_id)
    if case_type:
        query = query.where(Case.case_type == case_type)
    if status:
        query = query.where(Case.status == status)
    if priority:
        query = query.where(Case.priority == priority)
    if assigned_to:
        query = query.where(Case.assigned_to == assigned_to)
    result = await db.execute(query.order_by(Case.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/", response_model=CaseResponse, status_code=status.HTTP_201_CREATED)
async def create_case(
    case: CaseCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    case_id = uuid4()
    now = datetime.now(UTC)
    db_case = Case(
        id=case_id,
        tenant_id=tenant_id,
        case_ref=f"CSE-{str(case_id)[:8].upper()}",
        title=case.title,
        case_type=case.case_type,
        priority=case.priority,
        description=case.description,
        customer_id=case.customer_id,
        status=CaseStatus.OPEN,
        created_at=now,
        created_by=current_user.id,
    )
    db.add(db_case)

    # Add initial note
    note = CaseNote(
        id=uuid4(),
        tenant_id=tenant_id,
        case_id=case_id,
        content="Case created",
        created_at=now,
        created_by=current_user.id,
        is_internal=True,
    )
    db.add(note)

    await db.commit()
    await db.refresh(db_case)
    return db_case


@router.get("/{case_id}", response_model=CaseResponse)
async def get_case(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Case).where(and_(Case.id == case_id, Case.tenant_id == tenant_id))
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    return case


@router.patch("/{case_id}/assign")
async def assign_case(
    case_id: UUID,
    assigned_to: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Case).where(and_(Case.id == case_id, Case.tenant_id == tenant_id))
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.assigned_to = assigned_to
    case.assigned_at = datetime.now(UTC)
    if case.status == CaseStatus.OPEN:
        case.status = CaseStatus.IN_PROGRESS

    await db.commit()
    return {"message": "Case assigned", "assigned_to": str(assigned_to)}


@router.patch("/{case_id}/status")
async def update_case_status(
    case_id: UUID,
    new_status: str = Query(...),
    resolution: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Case).where(and_(Case.id == case_id, Case.tenant_id == tenant_id))
    )
    case = result.scalar_one_or_none()
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")

    case.status = new_status
    if new_status == "CLOSED":
        case.closed_at = datetime.now(UTC)
        case.resolution = resolution

    await db.commit()
    return {"message": "Case status updated", "new_status": new_status}


# Case Notes
@router.get("/{case_id}/notes")
async def list_case_notes(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(CaseNote)
        .where(and_(CaseNote.case_id == case_id, CaseNote.tenant_id == tenant_id))
        .order_by(CaseNote.created_at.desc())
    )
    return [
        {
            "id": str(n.id),
            "content": n.content,
            "created_at": n.created_at,
            "created_by": str(n.created_by) if n.created_by else None,
            "is_internal": n.is_internal,
        }
        for n in result.scalars().all()
    ]


@router.post("/{case_id}/notes")
async def add_case_note(
    case_id: UUID,
    note: CaseNoteCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    db_note = CaseNote(
        id=uuid4(),
        tenant_id=tenant_id,
        case_id=case_id,
        content=note.content,
        created_at=datetime.now(UTC),
        created_by=current_user.id,
        is_internal=note.is_internal,
    )
    db.add(db_note)
    await db.commit()
    return {"message": "Note added", "note_id": str(db_note.id)}


# Case Tasks
@router.get("/{case_id}/tasks")
async def list_case_tasks(
    case_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(CaseTask)
        .where(and_(CaseTask.case_id == case_id, CaseTask.tenant_id == tenant_id))
        .order_by(CaseTask.due_date)
    )
    return [
        {
            "id": str(t.id),
            "title": t.title,
            "status": t.status,
            "due_date": t.due_date,
            "assigned_to": str(t.assigned_to) if t.assigned_to else None,
        }
        for t in result.scalars().all()
    ]


@router.post("/{case_id}/tasks")
async def create_case_task(
    case_id: UUID,
    task: CaseTaskCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    db_task = CaseTask(
        id=uuid4(),
        tenant_id=tenant_id,
        case_id=case_id,
        title=task.title,
        description=task.description,
        status=TaskStatus.PENDING,
        due_date=task.due_date,
        assigned_to=task.assigned_to,
        created_at=datetime.now(UTC),
        created_by=current_user.id,
    )
    db.add(db_task)
    await db.commit()
    return {"message": "Task created", "task_id": str(db_task.id)}


@router.patch("/{case_id}/tasks/{task_id}/complete")
async def complete_case_task(
    case_id: UUID,
    task_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(CaseTask).where(
            and_(
                CaseTask.id == task_id, CaseTask.case_id == case_id, CaseTask.tenant_id == tenant_id
            )
        )
    )
    task = result.scalar_one_or_none()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    task.status = TaskStatus.COMPLETED
    task.completed_at = datetime.now(UTC)
    await db.commit()
    return {"message": "Task completed"}


# SAR Management
@router.get("/sars/", response_model=list[SARResponse])
async def list_sars(
    status: str | None = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(SARReport).where(SARReport.tenant_id == tenant_id)
    if status:
        query = query.where(SARReport.status == status)
    result = await db.execute(query.order_by(SARReport.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/sars/", response_model=SARResponse, status_code=status.HTTP_201_CREATED)
async def create_sar(
    sar: SARCreate,
    case_id: UUID = Query(...),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    sar_id = uuid4()
    db_sar = SARReport(
        id=sar_id,
        tenant_id=tenant_id,
        sar_ref=f"SAR-{str(sar_id)[:8].upper()}",
        case_id=case_id,
        filing_type=sar.filing_type,
        status=SARStatus.DRAFT,
        subject_name=sar.subject_name,
        subject_type=sar.subject_type,
        suspicious_activity_summary=sar.suspicious_activity_summary,
        amount_involved=sar.amount_involved,
        created_at=datetime.now(UTC),
        created_by=current_user.id,
    )
    db.add(db_sar)
    await db.commit()
    await db.refresh(db_sar)
    return db_sar


@router.get("/sars/{sar_id}", response_model=SARResponse)
async def get_sar(
    sar_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(SARReport).where(and_(SARReport.id == sar_id, SARReport.tenant_id == tenant_id))
    )
    sar = result.scalar_one_or_none()
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")
    return sar


@router.patch("/sars/{sar_id}/submit")
async def submit_sar(
    sar_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(SARReport).where(and_(SARReport.id == sar_id, SARReport.tenant_id == tenant_id))
    )
    sar = result.scalar_one_or_none()
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")

    sar.status = SARStatus.SUBMITTED
    sar.submitted_at = datetime.now(UTC)
    await db.commit()
    return {"message": "SAR submitted for review", "sar_id": str(sar_id)}


@router.patch("/sars/{sar_id}/file")
async def file_sar(
    sar_id: UUID,
    bsa_id: str = Query(..., description="BSA E-Filing ID"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(SARReport).where(and_(SARReport.id == sar_id, SARReport.tenant_id == tenant_id))
    )
    sar = result.scalar_one_or_none()
    if not sar:
        raise HTTPException(status_code=404, detail="SAR not found")

    sar.status = SARStatus.FILED
    sar.filed_at = datetime.now(UTC)
    sar.bsa_id = bsa_id
    await db.commit()
    return {"message": "SAR filed", "bsa_id": bsa_id}
