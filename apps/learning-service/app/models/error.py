"""Error event and weakness models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.models.attempt import Attempt
    from app.models.learner import Learner

from sqlalchemy import DateTime, Enum, Float, ForeignKey, String, Text, func
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ErrorCategory(str, enum.Enum):
    """Top-level error categories from the error taxonomy."""

    GRAMMAR = "grammar"
    LEXICAL = "lexical"
    COHERENCE_COHESION = "coherence_cohesion"
    TASK = "task"
    SPEAKING = "speaking"
    PRONUNCIATION = "pronunciation"


class ErrorSeverity(str, enum.Enum):
    """Error severity levels."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class WeaknessStatus(str, enum.Enum):
    """Weakness lifecycle status."""

    HYPOTHESIS = "hypothesis"
    CONFIRMED = "confirmed"
    IMPROVING = "improving"
    RESOLVED = "resolved"


class ErrorEvent(Base, UUIDPrimaryKeyMixin):
    """Individual error occurrence in an attempt."""

    __tablename__ = "error_events"

    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("attempts.id"), nullable=False)
    category: Mapped[ErrorCategory] = mapped_column(Enum(ErrorCategory), nullable=False, index=True)
    subtype: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    evidence_text: Mapped[str] = mapped_column(Text, nullable=False)
    severity: Mapped[ErrorSeverity] = mapped_column(Enum(ErrorSeverity), nullable=False)
    recurrence_group: Mapped[str | None] = mapped_column(String(200), nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    attempt: Mapped[Attempt] = relationship(back_populates="error_events")


class Weakness(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Persistent weakness record aggregated from error events."""

    __tablename__ = "weaknesses"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    category: Mapped[ErrorCategory] = mapped_column(Enum(ErrorCategory), nullable=False, index=True)
    subtype: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    status: Mapped[WeaknessStatus] = mapped_column(Enum(WeaknessStatus), default=WeaknessStatus.HYPOTHESIS)
    recurrence_rate: Mapped[float] = mapped_column(Float, default=0.0)
    impact_estimate: Mapped[float] = mapped_column(Float, default=0.0)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    priority: Mapped[float] = mapped_column(Float, default=0.0)
    first_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    last_seen_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    learner: Mapped[Learner] = relationship(back_populates="weaknesses")
