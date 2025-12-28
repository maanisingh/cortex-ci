"""Phase 2.5: Controlled AI Integration - Bounded intelligence models."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlalchemy import Boolean, ForeignKey, Numeric, String, Text
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.base import TenantMixin, TimestampMixin

if TYPE_CHECKING:
    from app.models.entity import Entity
    from app.models.user import User


class AIAnalysisType(str, Enum):
    """Types of AI analysis available."""

    ANOMALY = "anomaly"  # Anomaly detection
    PATTERN = "pattern"  # Pattern detection
    SUMMARY = "summary"  # Report summarization
    SCENARIO = "scenario"  # Scenario acceleration
    CLUSTERING = "clustering"  # Entity clustering


class AIAnalysisStatus(str, Enum):
    """Status of an AI analysis."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    AWAITING_APPROVAL = "awaiting_approval"
    APPROVED = "approved"
    REJECTED = "rejected"


class AIAnalysis(Base, TimestampMixin, TenantMixin):
    """AI-powered analysis with human approval gates."""

    __tablename__ = "ai_analyses"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Analysis type and status
    analysis_type: Mapped[AIAnalysisType] = mapped_column(SQLEnum(AIAnalysisType), nullable=False)
    status: Mapped[AIAnalysisStatus] = mapped_column(
        SQLEnum(AIAnalysisStatus), default=AIAnalysisStatus.PENDING
    )

    # Request info
    request_description: Mapped[str] = mapped_column(Text, nullable=False)
    requested_by_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )

    # Input data
    input_data: Mapped[dict] = mapped_column(JSONB, default=dict)
    input_entity_ids: Mapped[list] = mapped_column(JSONB, default=list)

    # Output
    output: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    output_summary: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Confidence and explainability
    confidence: Mapped[Decimal] = mapped_column(Numeric(5, 2), default=Decimal("0.00"))
    explanation: Mapped[str | None] = mapped_column(Text, nullable=True)
    model_card: Mapped[dict] = mapped_column(JSONB, default=dict)

    # Model info
    model_name: Mapped[str] = mapped_column(String(100), default="cortex-v1")
    model_version: Mapped[str] = mapped_column(String(50), default="1.0.0")

    # Human approval workflow
    requires_human_approval: Mapped[bool] = mapped_column(Boolean, default=True)
    approved_by_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    approved_at: Mapped[datetime | None] = mapped_column(nullable=True)
    approval_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Processing metrics
    processing_started_at: Mapped[datetime | None] = mapped_column(nullable=True)
    processing_completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    requested_by: Mapped[User] = relationship("User", foreign_keys=[requested_by_id])
    approved_by: Mapped[User | None] = relationship("User", foreign_keys=[approved_by_id])

    def __repr__(self) -> str:
        return f"<AIAnalysis {self.analysis_type.value} status={self.status.value}>"

    def get_model_card(self) -> dict:
        """Return model card for transparency."""
        return {
            "model_name": self.model_name,
            "model_version": self.model_version,
            "analysis_type": self.analysis_type.value,
            "capabilities": self._get_capabilities(),
            "limitations": self._get_limitations(),
            "ethical_considerations": self._get_ethical_notes(),
        }

    def _get_capabilities(self) -> list:
        """Get capabilities based on analysis type."""
        caps = {
            AIAnalysisType.ANOMALY: [
                "Detect unusual patterns in risk scores",
                "Flag entities with sudden risk changes",
                "Identify outliers in entity behavior",
            ],
            AIAnalysisType.PATTERN: [
                "Identify clusters of related entities",
                "Detect common risk factors",
                "Find hidden relationships",
            ],
            AIAnalysisType.SUMMARY: [
                "Generate natural language summaries",
                "Highlight key findings",
                "Create executive briefings",
            ],
            AIAnalysisType.SCENARIO: [
                "Accelerate scenario simulations",
                "Predict cascade effects",
                "Stress test dependencies",
            ],
            AIAnalysisType.CLUSTERING: [
                "Group similar entities",
                "Identify risk communities",
                "Segment by behavior patterns",
            ],
        }
        return caps.get(self.analysis_type, [])

    def _get_limitations(self) -> list:
        """Get known limitations."""
        return [
            "Cannot make prescriptive decisions",
            "Requires human review and approval",
            "May not capture all edge cases",
            "Performance varies with data quality",
            "Should not be used for political forecasting",
        ]

    def _get_ethical_notes(self) -> list:
        """Get ethical considerations."""
        return [
            "All outputs require human verification",
            "Not designed for autonomous decision-making",
            "Transparency is maintained via model cards",
            "Bias monitoring is ongoing",
        ]


class AnomalyDetection(Base, TimestampMixin, TenantMixin):
    """Detected anomalies for human review."""

    __tablename__ = "anomaly_detections"

    id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True, default=uuid4)

    # Source analysis
    ai_analysis_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("ai_analyses.id", ondelete="SET NULL"),
        nullable=True,
    )

    # Anomaly details
    entity_id: Mapped[UUID] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("entities.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    anomaly_type: Mapped[str] = mapped_column(String(100), nullable=False)
    anomaly_description: Mapped[str] = mapped_column(Text, nullable=False)
    anomaly_score: Mapped[Decimal] = mapped_column(Numeric(5, 2), nullable=False)  # 0-1 scale

    # Context
    baseline_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    detected_value: Mapped[str | None] = mapped_column(String(255), nullable=True)
    deviation_percentage: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    # Review status
    is_reviewed: Mapped[bool] = mapped_column(Boolean, default=False)
    reviewed_by_id: Mapped[UUID | None] = mapped_column(
        PGUUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    reviewed_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_confirmed_anomaly: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    review_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    # Relationships
    entity: Mapped[Entity] = relationship("Entity")
    ai_analysis: Mapped[AIAnalysis | None] = relationship("AIAnalysis")
    reviewed_by: Mapped[User | None] = relationship("User")

    def __repr__(self) -> str:
        return f"<AnomalyDetection {self.anomaly_type} entity={self.entity_id}>"
