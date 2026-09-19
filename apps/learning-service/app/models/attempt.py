"""Attempt and assessment models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.audio import AudioAsset
    from app.models.error import ErrorEvent
    from app.models.learner import Learner

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.learner import Skill


class AttemptSource(str, enum.Enum):
    """Source of the attempt."""

    TELEGRAM_TEXT = "telegram_text"
    TELEGRAM_VOICE = "telegram_voice"
    TELEGRAM_FILE = "telegram_file"
    SYSTEM_GENERATED = "system_generated"
    DIAGNOSTIC = "diagnostic"


class Attempt(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """A learner's attempt at a task."""

    __tablename__ = "attempts"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    skill: Mapped[Skill] = mapped_column(Enum(Skill), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "writing_task2", "speaking_part2"
    prompt_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("tasks.id"), nullable=True)
    raw_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    normalized_input: Mapped[str | None] = mapped_column(Text, nullable=True)
    submitted_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    source: Mapped[AttemptSource] = mapped_column(Enum(AttemptSource), nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    learner: Mapped[Learner] = relationship(back_populates="attempts")
    assessments: Mapped[list[Assessment]] = relationship(back_populates="attempt", cascade="all, delete-orphan")
    error_events: Mapped[list[ErrorEvent]] = relationship(back_populates="attempt", cascade="all, delete-orphan")
    audio_asset: Mapped[AudioAsset | None] = relationship(back_populates="attempt", uselist=False)


class Assessment(Base, UUIDPrimaryKeyMixin):
    """Assessment of a learner's attempt."""

    __tablename__ = "assessments"

    attempt_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("attempts.id"), nullable=False)
    estimated_band: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evaluator_version: Mapped[str] = mapped_column(String(100), nullable=False)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    attempt: Mapped[Attempt] = relationship(back_populates="assessments")
    criterion_scores: Mapped[list[CriterionScore]] = relationship(
        back_populates="assessment", cascade="all, delete-orphan"
    )


class CriterionScore(Base, UUIDPrimaryKeyMixin):
    """Score for a specific assessment criterion."""

    __tablename__ = "criterion_scores"

    assessment_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("assessments.id"), nullable=False)
    criterion: Mapped[str] = mapped_column(String(100), nullable=False)  # e.g., "task_achievement", "lexical_resource"
    score: Mapped[float] = mapped_column(Float, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    evidence_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)

    # Relationships
    assessment: Mapped[Assessment] = relationship(back_populates="criterion_scores")
