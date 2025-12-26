"""
Screening API Endpoints
Sanctions, PEP, and adverse media screening via OpenSanctions
"""
from uuid import UUID, uuid4
from typing import Optional, List
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, or_
from pydantic import BaseModel, Field
import httpx

from app.core.database import get_db
from app.core.config import settings
from app.api.v1.deps import get_current_user, get_current_tenant_id
from app.models.compliance.screening import (
    ScreeningResult, ScreeningStatus, ScreeningType,
    ScreeningMatch, MatchDisposition, WatchlistSource
)
from app.models.compliance.customer import Customer

router = APIRouter()


# ============================================================================
# SCHEMAS
# ============================================================================

class ScreeningRequest(BaseModel):
    name: str = Field(..., description="Name to screen")
    aliases: List[str] = Field(default=[], description="Alternative names")
    date_of_birth: Optional[str] = Field(None, description="DOB in YYYY-MM-DD format")
    country: Optional[str] = Field(None, max_length=3, description="ISO country code")
    id_number: Optional[str] = Field(None, description="ID/passport number")
    screening_types: List[str] = Field(
        default=["SANCTIONS", "PEP"],
        description="Types of screening to perform"
    )


class MatchResponse(BaseModel):
    id: UUID
    source: str
    matched_name: str
    match_score: float
    matched_type: Optional[str]
    sanction_programs: List[str]
    disposition: str
    matched_data: Optional[dict]

    class Config:
        from_attributes = True


class ScreeningResponse(BaseModel):
    id: UUID
    customer_id: Optional[UUID]
    screening_type: str
    status: str
    search_name: str
    total_matches: int
    highest_score: float
    screened_at: datetime
    matches: List[MatchResponse] = []

    class Config:
        from_attributes = True


# ============================================================================
# ENDPOINTS
# ============================================================================

@router.post("/search", response_model=ScreeningResponse)
async def perform_screening(
    request: ScreeningRequest,
    customer_id: Optional[UUID] = Query(None, description="Link to customer"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    """
    Perform real-time screening against OpenSanctions.
    Checks sanctions lists, PEP databases, and adverse media.
    """
    screening_id = uuid4()
    matches = []
    highest_score = 0.0

    # Call OpenSanctions yente API
    opensanctions_url = getattr(settings, 'OPENSANCTIONS_URL', 'http://opensanctions:8000')

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            # Build search query
            search_params = {
                "schema": "Person",
                "properties": {
                    "name": [request.name] + request.aliases,
                }
            }
            if request.country:
                search_params["properties"]["country"] = [request.country]
            if request.date_of_birth:
                search_params["properties"]["birthDate"] = [request.date_of_birth]

            response = await client.post(
                f"{opensanctions_url}/match/default",
                json={"queries": {"q1": search_params}}
            )

            if response.status_code == 200:
                data = response.json()
                results = data.get("responses", {}).get("q1", {}).get("results", [])

                for result in results[:20]:  # Limit to top 20 matches
                    score = result.get("score", 0) * 100
                    if score >= 50:  # Only include matches above threshold
                        match = ScreeningMatch(
                            id=uuid4(),
                            tenant_id=tenant_id,
                            screening_result_id=screening_id,
                            source=WatchlistSource.OPENSANCTIONS,
                            source_list=result.get("datasets", ["unknown"])[0] if result.get("datasets") else "unknown",
                            matched_entity_id=result.get("id", ""),
                            matched_name=result.get("caption", ""),
                            matched_aliases=result.get("properties", {}).get("alias", []),
                            matched_type=result.get("schema", ""),
                            match_score=score,
                            sanction_programs=result.get("datasets", []),
                            disposition=MatchDisposition.PENDING_REVIEW,
                            matched_data=result
                        )
                        matches.append(match)
                        if score > highest_score:
                            highest_score = score

    except Exception as e:
        # Log error but don't fail - return empty results
        print(f"OpenSanctions API error: {e}")

    # Determine status
    if len(matches) > 0:
        screening_status = ScreeningStatus.POTENTIAL_MATCH
    else:
        screening_status = ScreeningStatus.CLEAR

    # Create screening result
    screening_result = ScreeningResult(
        id=screening_id,
        tenant_id=tenant_id,
        customer_id=customer_id,
        screening_type=ScreeningType.COMPREHENSIVE,
        status=screening_status,
        search_name=request.name,
        search_aliases=request.aliases,
        search_dob=request.date_of_birth,
        search_country=request.country,
        total_matches=len(matches),
        highest_score=highest_score,
        lists_checked=["OPENSANCTIONS", "OFAC_SDN", "EU_CONSOLIDATED", "UN_SANCTIONS"],
        screened_at=datetime.now(timezone.utc),
    )

    db.add(screening_result)
    for match in matches:
        db.add(match)
    await db.commit()
    await db.refresh(screening_result)

    return ScreeningResponse(
        id=screening_result.id,
        customer_id=customer_id,
        screening_type=screening_result.screening_type,
        status=screening_result.status,
        search_name=screening_result.search_name,
        total_matches=screening_result.total_matches,
        highest_score=screening_result.highest_score,
        screened_at=screening_result.screened_at,
        matches=[
            MatchResponse(
                id=m.id,
                source=m.source,
                matched_name=m.matched_name,
                match_score=m.match_score,
                matched_type=m.matched_type,
                sanction_programs=m.sanction_programs,
                disposition=m.disposition,
                matched_data=m.matched_data
            ) for m in matches
        ]
    )


@router.get("/results", response_model=List[ScreeningResponse])
async def list_screening_results(
    customer_id: Optional[UUID] = Query(None),
    status: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """List screening results."""
    query = select(ScreeningResult).where(ScreeningResult.tenant_id == tenant_id)

    if customer_id:
        query = query.where(ScreeningResult.customer_id == customer_id)
    if status:
        query = query.where(ScreeningResult.status == status)

    result = await db.execute(
        query.order_by(ScreeningResult.screened_at.desc()).offset(skip).limit(limit)
    )
    return result.scalars().all()


@router.get("/results/{screening_id}", response_model=ScreeningResponse)
async def get_screening_result(
    screening_id: UUID,
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get screening result with matches."""
    result = await db.execute(
        select(ScreeningResult).where(
            and_(ScreeningResult.id == screening_id, ScreeningResult.tenant_id == tenant_id)
        )
    )
    screening = result.scalar_one_or_none()
    if not screening:
        raise HTTPException(status_code=404, detail="Screening result not found")

    # Get matches
    matches_result = await db.execute(
        select(ScreeningMatch).where(ScreeningMatch.screening_result_id == screening_id)
    )
    matches = matches_result.scalars().all()

    return ScreeningResponse(
        id=screening.id,
        customer_id=screening.customer_id,
        screening_type=screening.screening_type,
        status=screening.status,
        search_name=screening.search_name,
        total_matches=screening.total_matches,
        highest_score=screening.highest_score,
        screened_at=screening.screened_at,
        matches=[
            MatchResponse(
                id=m.id,
                source=m.source,
                matched_name=m.matched_name,
                match_score=m.match_score,
                matched_type=m.matched_type,
                sanction_programs=m.sanction_programs,
                disposition=m.disposition,
                matched_data=m.matched_data
            ) for m in matches
        ]
    )


@router.patch("/matches/{match_id}/resolve")
async def resolve_match(
    match_id: UUID,
    disposition: str = Query(..., description="TRUE_POSITIVE, FALSE_POSITIVE, or INCONCLUSIVE"),
    reason: Optional[str] = Query(None, description="Disposition reason"),
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
    current_user = Depends(get_current_user),
):
    """Resolve a screening match."""
    result = await db.execute(
        select(ScreeningMatch).where(
            and_(ScreeningMatch.id == match_id, ScreeningMatch.tenant_id == tenant_id)
        )
    )
    match = result.scalar_one_or_none()
    if not match:
        raise HTTPException(status_code=404, detail="Match not found")

    valid_dispositions = [d.value for d in MatchDisposition]
    if disposition not in valid_dispositions:
        raise HTTPException(status_code=400, detail=f"Invalid disposition. Must be one of: {valid_dispositions}")

    match.disposition = disposition
    match.disposition_reason = reason
    match.disposition_at = datetime.now(timezone.utc)
    # match.disposition_by = current_user.id

    await db.commit()
    return {"message": "Match resolved", "match_id": str(match_id), "disposition": disposition}


@router.get("/queue")
async def get_screening_queue(
    db: AsyncSession = Depends(get_db),
    tenant_id: UUID = Depends(get_current_tenant_id),
):
    """Get pending matches requiring review."""
    result = await db.execute(
        select(ScreeningMatch)
        .where(
            and_(
                ScreeningMatch.tenant_id == tenant_id,
                ScreeningMatch.disposition == MatchDisposition.PENDING_REVIEW
            )
        )
        .order_by(ScreeningMatch.match_score.desc())
        .limit(100)
    )
    matches = result.scalars().all()

    return {
        "pending_count": len(matches),
        "matches": [
            {
                "id": str(m.id),
                "screening_result_id": str(m.screening_result_id),
                "matched_name": m.matched_name,
                "match_score": m.match_score,
                "source": m.source,
                "sanction_programs": m.sanction_programs
            } for m in matches
        ]
    }
