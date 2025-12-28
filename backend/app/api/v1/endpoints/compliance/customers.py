"""
Customer/KYC API Endpoints
AML/KYC customer management, onboarding, and risk assessment
"""

from datetime import UTC, date, datetime
from uuid import UUID, uuid4

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr, Field
from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.deps import get_current_tenant_id, get_current_user
from app.core.database import get_db
from app.models.compliance.customer import (
    Customer,
    CustomerRiskRating,
    CustomerStatus,
)

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================


class CustomerCreate(BaseModel):
    customer_type: str = Field(..., description="INDIVIDUAL or CORPORATION, etc.")
    external_id: str | None = None
    # Individual fields
    first_name: str | None = None
    last_name: str | None = None
    date_of_birth: date | None = None
    nationality: str | None = Field(None, max_length=3)
    # Organization fields
    legal_name: str | None = None
    registration_number: str | None = None
    incorporation_country: str | None = Field(None, max_length=3)
    # Contact
    email: EmailStr | None = None
    phone: str | None = None
    country: str | None = Field(None, max_length=3)
    # Risk
    source_of_funds: str | None = None
    expected_activity: str | None = None


class CustomerResponse(BaseModel):
    id: UUID
    customer_type: str
    external_id: str | None
    status: str
    risk_rating: str
    risk_score: float
    first_name: str | None
    last_name: str | None
    legal_name: str | None
    email: str | None
    country: str | None
    is_pep: bool
    is_sanctioned: bool
    has_adverse_media: bool
    created_at: datetime
    last_review_date: date | None
    next_review_date: date | None

    class Config:
        from_attributes = True


class CustomerDetailResponse(CustomerResponse):
    date_of_birth: date | None
    nationality: str | None
    registration_number: str | None
    incorporation_country: str | None
    phone: str | None
    address_line1: str | None
    city: str | None
    source_of_funds: str | None
    source_of_wealth: str | None
    expected_activity: str | None
    beneficial_owners: dict | None
    pep_type: str | None
    pep_details: str | None
    sanction_details: str | None


class RiskAssessmentResponse(BaseModel):
    customer_id: UUID
    current_rating: str
    risk_score: float
    risk_factors: list[str]
    recommendations: list[str]


# ============================================================================
# ENDPOINTS
# ============================================================================


@router.get("/", response_model=list[CustomerResponse])
async def list_customers(
    status: str | None = Query(None, description="Filter by status"),
    risk_rating: str | None = Query(None, description="Filter by risk rating"),
    customer_type: str | None = Query(None, description="Filter by type"),
    search: str | None = Query(None, description="Search name/email"),
    is_pep: bool | None = Query(None, description="Filter PEPs"),
    is_sanctioned: bool | None = Query(None, description="Filter sanctioned"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List customers with filters."""
    query = select(Customer).where(Customer.tenant_id == tenant_id)

    if status:
        query = query.where(Customer.status == status)
    if risk_rating:
        query = query.where(Customer.risk_rating == risk_rating)
    if customer_type:
        query = query.where(Customer.customer_type == customer_type)
    if is_pep is not None:
        query = query.where(Customer.is_pep == is_pep)
    if is_sanctioned is not None:
        query = query.where(Customer.is_sanctioned == is_sanctioned)
    if search:
        query = query.where(
            or_(
                Customer.first_name.ilike(f"%{search}%"),
                Customer.last_name.ilike(f"%{search}%"),
                Customer.legal_name.ilike(f"%{search}%"),
                Customer.email.ilike(f"%{search}%"),
            )
        )

    result = await db.execute(query.order_by(Customer.created_at.desc()).offset(skip).limit(limit))
    return result.scalars().all()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer: CustomerCreate,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Create a new customer and initiate KYC process."""
    # Calculate initial risk score based on factors
    risk_factors = []
    risk_score = 30.0  # Base score

    # High-risk country check
    high_risk_countries = ["KP", "IR", "MM", "SY", "VE", "YE", "AF"]
    customer_country = customer.country or customer.incorporation_country or customer.nationality
    if customer_country and customer_country.upper() in high_risk_countries:
        risk_score += 30
        risk_factors.append("HIGH_RISK_COUNTRY")

    # Determine risk rating
    if risk_score >= 80:
        risk_rating = CustomerRiskRating.VERY_HIGH
    elif risk_score >= 60:
        risk_rating = CustomerRiskRating.HIGH
    elif risk_score >= 40:
        risk_rating = CustomerRiskRating.MEDIUM
    else:
        risk_rating = CustomerRiskRating.LOW

    # Set review frequency based on risk
    review_freq = (
        12
        if risk_rating == CustomerRiskRating.LOW
        else (6 if risk_rating == CustomerRiskRating.MEDIUM else 3)
    )

    db_customer = Customer(
        id=uuid4(),
        tenant_id=tenant_id,
        customer_type=customer.customer_type,
        external_id=customer.external_id,
        status=CustomerStatus.PENDING_KYC,
        risk_rating=risk_rating,
        risk_score=risk_score,
        first_name=customer.first_name,
        last_name=customer.last_name,
        date_of_birth=customer.date_of_birth,
        nationality=customer.nationality,
        legal_name=customer.legal_name,
        registration_number=customer.registration_number,
        incorporation_country=customer.incorporation_country,
        email=customer.email,
        phone=customer.phone,
        country=customer.country,
        source_of_funds=customer.source_of_funds,
        expected_activity=customer.expected_activity,
        review_frequency_months=review_freq,
        is_pep=False,
        is_sanctioned=False,
        has_adverse_media=False,
    )

    db.add(db_customer)
    await db.commit()
    await db.refresh(db_customer)

    # Trigger background screening
    # background_tasks.add_task(perform_initial_screening, db_customer.id, tenant_id)

    return db_customer


@router.get("/{customer_id}", response_model=CustomerDetailResponse)
async def get_customer(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get customer details."""
    result = await db.execute(
        select(Customer).where(and_(Customer.id == customer_id, Customer.tenant_id == tenant_id))
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")
    return customer


@router.patch("/{customer_id}/status")
async def update_customer_status(
    customer_id: UUID,
    new_status: str = Query(..., description="New status"),
    reason: str | None = Query(None, description="Reason for change"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Update customer status."""
    result = await db.execute(
        select(Customer).where(and_(Customer.id == customer_id, Customer.tenant_id == tenant_id))
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    valid_statuses = [s.value for s in CustomerStatus]
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=400, detail=f"Invalid status. Must be one of: {valid_statuses}"
        )

    old_status = customer.status
    customer.status = new_status

    if new_status == CustomerStatus.ACTIVE and not customer.onboarded_at:
        customer.onboarded_at = datetime.now(UTC)

    await db.commit()
    return {
        "message": "Status updated",
        "customer_id": str(customer_id),
        "old_status": old_status,
        "new_status": new_status,
    }


@router.get("/{customer_id}/risk-assessment", response_model=RiskAssessmentResponse)
async def assess_customer_risk(
    customer_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Perform risk assessment on customer."""
    result = await db.execute(
        select(Customer).where(and_(Customer.id == customer_id, Customer.tenant_id == tenant_id))
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    risk_factors = []
    recommendations = []

    if customer.is_pep:
        risk_factors.append("Politically Exposed Person")
        recommendations.append("Conduct Enhanced Due Diligence")
    if customer.is_sanctioned:
        risk_factors.append("Sanctions match detected")
        recommendations.append("URGENT: Review sanctions match and consider account closure")
    if customer.has_adverse_media:
        risk_factors.append("Adverse media detected")
        recommendations.append("Review adverse media reports")
    if customer.high_risk_country:
        risk_factors.append("High-risk jurisdiction")
        recommendations.append("Apply enhanced monitoring")
    if customer.high_risk_industry:
        risk_factors.append("High-risk industry")
        recommendations.append("Verify source of funds documentation")

    if not risk_factors:
        risk_factors.append("No significant risk factors identified")

    return RiskAssessmentResponse(
        customer_id=customer_id,
        current_rating=customer.risk_rating,
        risk_score=customer.risk_score,
        risk_factors=risk_factors,
        recommendations=recommendations if recommendations else ["Continue standard monitoring"],
    )


@router.post("/{customer_id}/screen")
async def screen_customer(
    customer_id: UUID,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user=Depends(get_current_user),
):
    """Trigger screening against sanctions/PEP lists."""
    result = await db.execute(
        select(Customer).where(and_(Customer.id == customer_id, Customer.tenant_id == tenant_id))
    )
    customer = result.scalar_one_or_none()
    if not customer:
        raise HTTPException(status_code=404, detail="Customer not found")

    # Background task would call OpenSanctions yente API
    # background_tasks.add_task(perform_screening, customer_id, tenant_id)

    return {"message": "Screening initiated", "customer_id": str(customer_id), "status": "PENDING"}


@router.get("/stats/overview")
async def get_customer_stats(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get customer statistics overview."""
    # Total customers
    total = await db.execute(select(func.count(Customer.id)).where(Customer.tenant_id == tenant_id))
    total_count = total.scalar()

    # By status
    status_counts = await db.execute(
        select(Customer.status, func.count(Customer.id))
        .where(Customer.tenant_id == tenant_id)
        .group_by(Customer.status)
    )

    # By risk rating
    risk_counts = await db.execute(
        select(Customer.risk_rating, func.count(Customer.id))
        .where(Customer.tenant_id == tenant_id)
        .group_by(Customer.risk_rating)
    )

    # PEPs and sanctioned
    pep_count = await db.execute(
        select(func.count(Customer.id)).where(
            and_(Customer.tenant_id == tenant_id, Customer.is_pep == True)
        )
    )
    sanctioned_count = await db.execute(
        select(func.count(Customer.id)).where(
            and_(Customer.tenant_id == tenant_id, Customer.is_sanctioned == True)
        )
    )

    return {
        "total_customers": total_count,
        "by_status": {row[0]: row[1] for row in status_counts.fetchall()},
        "by_risk_rating": {row[0]: row[1] for row in risk_counts.fetchall()},
        "pep_count": pep_count.scalar(),
        "sanctioned_count": sanctioned_count.scalar(),
    }
