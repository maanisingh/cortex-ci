"""
EGRUL (ЕГРЮЛ) - Russian Company Registry Models
For caching company data scraped from public sources like Rusprofile.ru
"""

from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base
from app.models.base import TimestampMixin


class CompanyStatus(str, Enum):
    """Company registration status in EGRUL."""

    ACTIVE = "active"  # Действующая
    LIQUIDATING = "liquidating"  # В процессе ликвидации
    LIQUIDATED = "liquidated"  # Ликвидирована
    BANKRUPT = "bankrupt"  # Банкротство
    REORGANIZING = "reorganizing"  # Реорганизация
    UNKNOWN = "unknown"


class DataSource(str, Enum):
    """Source of company data."""

    RUSPROFILE = "rusprofile"  # rusprofile.ru
    FNS = "fns"  # nalog.ru / egrul.nalog.ru
    SPARK = "spark"  # spark-interfax.ru
    MANUAL = "manual"  # Manually entered
    API = "api"  # Official API


class EGRULCompany(Base, TimestampMixin):
    """
    Cached company data from EGRUL/EGRIP registry.
    Primary key is INN to ensure uniqueness.
    """

    __tablename__ = "egrul_companies"

    # Primary identifier
    inn: Mapped[str] = mapped_column(String(12), primary_key=True, index=True)

    # Registration identifiers
    ogrn: Mapped[str | None] = mapped_column(String(15), nullable=True, index=True)
    kpp: Mapped[str | None] = mapped_column(String(9), nullable=True)
    okpo: Mapped[str | None] = mapped_column(String(14), nullable=True)

    # Company names
    full_name: Mapped[str] = mapped_column(String(500), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(200), nullable=True)

    # Legal form (ООО, АО, ИП, etc.)
    legal_form: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Addresses
    legal_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    actual_address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    region: Mapped[str | None] = mapped_column(String(100), nullable=True)

    # Registration dates
    registration_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    registration_authority: Mapped[str | None] = mapped_column(String(300), nullable=True)

    # Director / CEO
    director_name: Mapped[str | None] = mapped_column(String(200), nullable=True)
    director_position: Mapped[str | None] = mapped_column(String(100), nullable=True)
    director_inn: Mapped[str | None] = mapped_column(String(12), nullable=True)

    # Founders (stored as JSON array)
    founders: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # OKVED (economic activity codes)
    okved_main: Mapped[str | None] = mapped_column(String(10), nullable=True)
    okved_main_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    okved_additional: Mapped[list | None] = mapped_column(JSONB, nullable=True)

    # Financial info
    authorized_capital: Mapped[int | None] = mapped_column(Integer, nullable=True)  # in rubles
    authorized_capital_currency: Mapped[str] = mapped_column(String(3), default="RUB")

    # Size indicators
    employee_count: Mapped[str | None] = mapped_column(String(50), nullable=True)  # e.g., "до 15", "16-100"
    revenue_category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    # Status
    status: Mapped[str] = mapped_column(String(50), default=CompanyStatus.ACTIVE.value)
    status_detail: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Contact info (if available)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(255), nullable=True)
    website: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # Tax regime
    tax_regime: Mapped[str | None] = mapped_column(String(50), nullable=True)  # УСН, ОСНО, etc.

    # Additional structured data
    raw_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    # Data source and freshness
    source: Mapped[str] = mapped_column(String(50), default=DataSource.RUSPROFILE.value)
    source_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    last_fetched: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    last_updated_at_source: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    # Cache management
    is_stale: Mapped[bool] = mapped_column(Boolean, default=False)
    fetch_attempts: Mapped[int] = mapped_column(Integer, default=0)
    last_error: Mapped[str | None] = mapped_column(Text, nullable=True)

    def __repr__(self) -> str:
        return f"<EGRULCompany INN={self.inn} name={self.short_name or self.full_name[:50]}>"

    @property
    def display_name(self) -> str:
        """Return best display name."""
        return self.short_name or self.full_name

    @property
    def is_individual_entrepreneur(self) -> bool:
        """Check if this is an individual entrepreneur (ИП)."""
        return self.legal_form == "ИП" or (self.inn and len(self.inn) == 12)

    @property
    def is_legal_entity(self) -> bool:
        """Check if this is a legal entity (юрлицо)."""
        return self.inn and len(self.inn) == 10

    @property
    def needs_refresh(self) -> bool:
        """Check if data is stale and needs refresh."""
        if self.is_stale:
            return True
        if not self.last_fetched:
            return True
        # Consider stale after 7 days
        from datetime import timedelta

        return (datetime.utcnow() - self.last_fetched) > timedelta(days=7)


class EGRULFetchLog(Base, TimestampMixin):
    """Log of EGRUL fetch operations for auditing and debugging."""

    __tablename__ = "egrul_fetch_log"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    # What was fetched
    inn: Mapped[str] = mapped_column(String(12), index=True)
    source: Mapped[str] = mapped_column(String(50))

    # Result
    success: Mapped[bool] = mapped_column(Boolean)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Response details
    response_code: Mapped[int | None] = mapped_column(Integer, nullable=True)
    response_time_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)

    # What was found
    company_found: Mapped[bool] = mapped_column(Boolean, default=False)
    company_name: Mapped[str | None] = mapped_column(String(500), nullable=True)

    def __repr__(self) -> str:
        status = "OK" if self.success else "FAILED"
        return f"<EGRULFetchLog {self.inn} {self.source} {status}>"
