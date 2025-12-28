"""
Screening Models
Sanctions, PEP, adverse media, and watchlist screening
Integrates with OpenSanctions, OFAC, EU, UN, and other lists
"""

from datetime import datetime
from enum import Enum
from uuid import UUID, uuid4

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin


class ScreeningType(str, Enum):
    """Type of screening performed."""

    SANCTIONS = "SANCTIONS"
    PEP = "PEP"
    ADVERSE_MEDIA = "ADVERSE_MEDIA"
    WATCHLIST = "WATCHLIST"
    LAW_ENFORCEMENT = "LAW_ENFORCEMENT"
    INTERNAL_LIST = "INTERNAL_LIST"
    COMPREHENSIVE = "COMPREHENSIVE"


class ScreeningStatus(str, Enum):
    """Screening result status."""

    PENDING = "PENDING"
    CLEAR = "CLEAR"
    POTENTIAL_MATCH = "POTENTIAL_MATCH"
    CONFIRMED_MATCH = "CONFIRMED_MATCH"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    ESCALATED = "ESCALATED"
    ERROR = "ERROR"


class MatchDisposition(str, Enum):
    """Disposition of a screening match."""

    PENDING_REVIEW = "PENDING_REVIEW"
    TRUE_POSITIVE = "TRUE_POSITIVE"
    FALSE_POSITIVE = "FALSE_POSITIVE"
    INCONCLUSIVE = "INCONCLUSIVE"
    ESCALATED = "ESCALATED"


class WatchlistSource(str, Enum):
    """Sources of watchlist data."""

    OPENSANCTIONS = "OPENSANCTIONS"
    OFAC_SDN = "OFAC_SDN"
    OFAC_CONS = "OFAC_CONS"
    EU_CONSOLIDATED = "EU_CONSOLIDATED"
    UN_SANCTIONS = "UN_SANCTIONS"
    UK_SANCTIONS = "UK_SANCTIONS"
    FATF_HIGH_RISK = "FATF_HIGH_RISK"
    INTERPOL = "INTERPOL"
    FBI_WANTED = "FBI_WANTED"
    WORLD_BANK_DEBARRED = "WORLD_BANK_DEBARRED"
    PEP_INTERNATIONAL = "PEP_INTERNATIONAL"
    PEP_DOMESTIC = "PEP_DOMESTIC"
    ADVERSE_MEDIA = "ADVERSE_MEDIA"
    INTERNAL = "INTERNAL"
    CUSTOM = "CUSTOM"


class ScreeningResult(Base, TimestampMixin, TenantMixin):
    """Screening result for a customer or entity."""

    __tablename__ = "screening_results"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # What was screened
    customer_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )
    entity_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    # Screening details
    screening_type: Mapped[ScreeningType] = mapped_column(String(50), nullable=False, index=True)
    status: Mapped[ScreeningStatus] = mapped_column(
        String(50), default=ScreeningStatus.PENDING, index=True
    )

    # What was searched
    search_name: Mapped[str] = mapped_column(String(500), nullable=False)
    search_aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    search_dob: Mapped[str | None] = mapped_column(String(20), nullable=True)
    search_country: Mapped[str | None] = mapped_column(String(3), nullable=True)
    search_id_number: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Results summary
    total_matches: Mapped[int] = mapped_column(Integer, default=0)
    highest_score: Mapped[float] = mapped_column(Float, default=0.0)

    # Lists checked
    lists_checked: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Timestamps
    screened_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    reviewed_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Review
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_disposition: Mapped[MatchDisposition | None] = mapped_column(String(50), nullable=True)

    # Trigger for re-screening
    is_scheduled: Mapped[bool] = mapped_column(Boolean, default=False)
    trigger_event: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Raw API response
    api_response: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    customer = relationship("Customer", back_populates="screening_results")
    matches = relationship(
        "ScreeningMatch", back_populates="screening_result", cascade="all, delete-orphan"
    )


class ScreeningMatch(Base, TimestampMixin, TenantMixin):
    """Individual match from screening."""

    __tablename__ = "screening_matches"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)
    screening_result_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("screening_results.id", ondelete="CASCADE"), index=True
    )

    # Match source
    source: Mapped[WatchlistSource] = mapped_column(String(50), nullable=False)
    source_list: Mapped[str] = mapped_column(String(255), nullable=False)

    # Matched entity info
    matched_entity_id: Mapped[str] = mapped_column(String(255), nullable=False)
    matched_name: Mapped[str] = mapped_column(String(500), nullable=False)
    matched_aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    matched_type: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Match scoring
    match_score: Mapped[float] = mapped_column(Float, nullable=False)
    name_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    dob_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    country_score: Mapped[float | None] = mapped_column(Float, nullable=True)

    # Why it matched
    match_reasons: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Matched entity details
    matched_dob: Mapped[str | None] = mapped_column(String(20), nullable=True)
    matched_nationality: Mapped[str | None] = mapped_column(String(3), nullable=True)
    matched_country: Mapped[str | None] = mapped_column(String(3), nullable=True)
    matched_address: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Sanction details
    sanction_programs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    sanction_start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sanction_end_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sanction_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PEP details
    pep_position: Mapped[str | None] = mapped_column(String(500), nullable=True)
    pep_country: Mapped[str | None] = mapped_column(String(3), nullable=True)
    pep_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Disposition
    disposition: Mapped[MatchDisposition] = mapped_column(
        String(50), default=MatchDisposition.PENDING_REVIEW
    )
    disposition_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    disposition_by: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )
    disposition_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Full matched entity data
    matched_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    screening_result = relationship("ScreeningResult", back_populates="matches")


class WatchlistEntity(Base, TimestampMixin, TenantMixin):
    """Local copy of watchlist entities for fast matching."""

    __tablename__ = "watchlist_entities"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Source info
    source: Mapped[WatchlistSource] = mapped_column(String(50), nullable=False, index=True)
    source_id: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    source_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    # Entity type
    entity_type: Mapped[str] = mapped_column(
        String(50), nullable=False, index=True
    )  # person, organization, vessel, aircraft

    # Names
    primary_name: Mapped[str] = mapped_column(String(500), nullable=False, index=True)
    aliases: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    name_variations: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Identification
    date_of_birth: Mapped[str | None] = mapped_column(String(20), nullable=True)
    place_of_birth: Mapped[str | None] = mapped_column(String(255), nullable=True)
    nationalities: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    countries: Mapped[list[str]] = mapped_column(ARRAY(String), default=list, index=True)

    # Additional identifiers
    passport_numbers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    national_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    tax_ids: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    registration_numbers: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)

    # Address
    addresses: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Sanction info
    sanction_programs: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    sanction_types: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    listed_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    delisted_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    sanction_basis: Mapped[str | None] = mapped_column(Text, nullable=True)

    # PEP info
    is_pep: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    pep_positions: Mapped[list[str]] = mapped_column(ARRAY(String), default=list)
    pep_level: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    last_updated: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Full data
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Search optimization - trigram indexes would be added via Alembic
    search_text: Mapped[str | None] = mapped_column(Text, nullable=True)
