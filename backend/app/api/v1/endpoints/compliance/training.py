"""Training & Awareness API Endpoints"""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.training import (
    AssignmentStatus,
    CampaignStatus,
    Course,
    CourseStatus,
    PhishingCampaign,
    PhishingResult,
    TrainingAssignment,
    TrainingCompletion,
)

router = APIRouter()


class CourseCreate(BaseModel):
    title: str
    description: str | None = None
    category: str
    duration_minutes: int = 30
    passing_score: int = 80
    is_mandatory: bool = False
    content_url: str | None = None


class CourseResponse(BaseModel):
    id: UUID
    course_ref: str
    title: str
    category: str
    status: str
    duration_minutes: int
    passing_score: int
    is_mandatory: bool

    class Config:
        from_attributes = True


class AssignmentResponse(BaseModel):
    id: UUID
    course_id: UUID
    user_id: UUID
    status: str
    assigned_at: datetime
    due_date: date | None
    completed_at: datetime | None

    class Config:
        from_attributes = True


class PhishingCampaignCreate(BaseModel):
    name: str
    template_name: str
    target_group: str
    scheduled_start: datetime | None = None


class PhishingCampaignResponse(BaseModel):
    id: UUID
    campaign_ref: str
    name: str
    status: str
    target_count: int
    emails_sent: int
    emails_opened: int
    links_clicked: int
    credentials_submitted: int
    reported_count: int

    class Config:
        from_attributes = True


@router.get("/courses", response_model=list[CourseResponse])
async def list_courses(
    category: str | None = Query(None),
    status: str | None = Query(None),
    is_mandatory: bool | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(Course).where(Course.tenant_id == tenant_id)
    if category:
        query = query.where(Course.category == category)
    if status:
        query = query.where(Course.status == status)
    if is_mandatory is not None:
        query = query.where(Course.is_mandatory == is_mandatory)
    result = await db.execute(query.order_by(Course.title))
    return result.scalars().all()


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    course: CourseCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    course_id = uuid4()
    db_course = Course(
        id=course_id,
        tenant_id=tenant_id,
        course_ref=f"CRS-{str(course_id)[:8].upper()}",
        title=course.title,
        description=course.description,
        category=course.category,
        duration_minutes=course.duration_minutes,
        passing_score=course.passing_score,
        is_mandatory=course.is_mandatory,
        content_url=course.content_url,
        status=CourseStatus.DRAFT,
    )
    db.add(db_course)
    await db.commit()
    await db.refresh(db_course)
    return db_course


@router.post("/courses/{course_id}/publish")
async def publish_course(
    course_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(Course).where(and_(Course.id == course_id, Course.tenant_id == tenant_id))
    )
    course = result.scalar_one_or_none()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    course.status = CourseStatus.PUBLISHED
    await db.commit()
    return {"message": "Course published", "course_id": str(course_id)}


@router.post("/courses/{course_id}/assign", response_model=AssignmentResponse)
async def assign_course(
    course_id: UUID,
    user_id: UUID = Query(...),
    due_date: date | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    assignment = TrainingAssignment(
        id=uuid4(),
        tenant_id=tenant_id,
        course_id=course_id,
        user_id=user_id,
        assigned_at=datetime.now(UTC),
        due_date=due_date,
        status=AssignmentStatus.ASSIGNED,
    )
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


@router.get("/assignments", response_model=list[AssignmentResponse])
async def list_my_assignments(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    query = select(TrainingAssignment).where(
        and_(
            TrainingAssignment.tenant_id == tenant_id, TrainingAssignment.user_id == current_user.id
        )
    )
    if status:
        query = query.where(TrainingAssignment.status == status)
    result = await db.execute(query.order_by(TrainingAssignment.due_date))
    return result.scalars().all()


@router.post("/assignments/{assignment_id}/complete")
async def complete_assignment(
    assignment_id: UUID,
    score: int = Query(..., ge=0, le=100),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    result = await db.execute(
        select(TrainingAssignment).where(
            and_(TrainingAssignment.id == assignment_id, TrainingAssignment.tenant_id == tenant_id)
        )
    )
    assignment = result.scalar_one_or_none()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Get course passing score
    course_result = await db.execute(select(Course).where(Course.id == assignment.course_id))
    course = course_result.scalar_one_or_none()
    passing_score = course.passing_score if course else 80

    passed = score >= passing_score
    now = datetime.now(UTC)

    assignment.status = AssignmentStatus.COMPLETED if passed else AssignmentStatus.FAILED
    assignment.completed_at = now

    completion = TrainingCompletion(
        id=uuid4(),
        tenant_id=tenant_id,
        assignment_id=assignment_id,
        user_id=current_user.id,
        course_id=assignment.course_id,
        completed_at=now,
        score=score,
        passed=passed,
        time_spent_minutes=course.duration_minutes if course else 30,
    )
    db.add(completion)

    await db.commit()
    return {"message": "Assignment completed", "passed": passed, "score": score}


# Phishing Campaigns
@router.get("/phishing/campaigns", response_model=list[PhishingCampaignResponse])
async def list_phishing_campaigns(
    status: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    query = select(PhishingCampaign).where(PhishingCampaign.tenant_id == tenant_id)
    if status:
        query = query.where(PhishingCampaign.status == status)
    result = await db.execute(query.order_by(PhishingCampaign.created_at.desc()))
    return result.scalars().all()


@router.post(
    "/phishing/campaigns",
    response_model=PhishingCampaignResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_phishing_campaign(
    campaign: PhishingCampaignCreate,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    campaign_id = uuid4()
    db_campaign = PhishingCampaign(
        id=campaign_id,
        tenant_id=tenant_id,
        campaign_ref=f"PHI-{str(campaign_id)[:8].upper()}",
        name=campaign.name,
        template_name=campaign.template_name,
        target_group=campaign.target_group,
        status=CampaignStatus.DRAFT,
        scheduled_start=campaign.scheduled_start,
    )
    db.add(db_campaign)
    await db.commit()
    await db.refresh(db_campaign)
    return db_campaign


@router.post("/phishing/campaigns/{campaign_id}/launch")
async def launch_phishing_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(PhishingCampaign).where(
            and_(PhishingCampaign.id == campaign_id, PhishingCampaign.tenant_id == tenant_id)
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    campaign.status = CampaignStatus.ACTIVE
    campaign.actual_start = datetime.now(UTC)
    await db.commit()

    # In production, this would trigger GoPhish API
    return {"message": "Campaign launched", "campaign_id": str(campaign_id)}


@router.get("/phishing/campaigns/{campaign_id}/results")
async def get_campaign_results(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    result = await db.execute(
        select(PhishingCampaign).where(
            and_(PhishingCampaign.id == campaign_id, PhishingCampaign.tenant_id == tenant_id)
        )
    )
    campaign = result.scalar_one_or_none()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")

    results = await db.execute(
        select(PhishingResult).where(PhishingResult.campaign_id == campaign_id)
    )

    return {
        "campaign": {
            "id": str(campaign.id),
            "name": campaign.name,
            "status": campaign.status,
            "target_count": campaign.target_count,
            "emails_sent": campaign.emails_sent,
            "emails_opened": campaign.emails_opened,
            "links_clicked": campaign.links_clicked,
            "credentials_submitted": campaign.credentials_submitted,
            "reported_count": campaign.reported_count,
        },
        "results": [
            {
                "user_id": str(r.user_id),
                "email_sent": r.email_sent,
                "email_opened": r.email_opened,
                "link_clicked": r.link_clicked,
                "credentials_submitted": r.credentials_submitted,
                "reported": r.reported,
            }
            for r in results.scalars().all()
        ],
    }


@router.get("/compliance-rate")
async def get_training_compliance_rate(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get overall training compliance metrics"""
    # Total mandatory assignments
    total_query = select(func.count(TrainingAssignment.id)).where(
        TrainingAssignment.tenant_id == tenant_id
    )
    total_result = await db.execute(total_query)
    total = total_result.scalar() or 0

    # Completed assignments
    completed_query = select(func.count(TrainingAssignment.id)).where(
        and_(
            TrainingAssignment.tenant_id == tenant_id,
            TrainingAssignment.status == AssignmentStatus.COMPLETED,
        )
    )
    completed_result = await db.execute(completed_query)
    completed = completed_result.scalar() or 0

    # Overdue assignments
    overdue_query = select(func.count(TrainingAssignment.id)).where(
        and_(
            TrainingAssignment.tenant_id == tenant_id,
            TrainingAssignment.status.in_(
                [AssignmentStatus.ASSIGNED, AssignmentStatus.IN_PROGRESS]
            ),
            TrainingAssignment.due_date < date.today(),
        )
    )
    overdue_result = await db.execute(overdue_query)
    overdue = overdue_result.scalar() or 0

    compliance_rate = (completed / total * 100) if total > 0 else 0

    return {
        "total_assignments": total,
        "completed": completed,
        "overdue": overdue,
        "compliance_rate": round(compliance_rate, 1),
    }
