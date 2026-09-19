"""Learner and skill state models."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class BaselineStatus(str, enum.Enum):
    """Learner baseline assessment status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"


class Skill(str, enum.Enum):
    """IELTS skill categories."""
    LISTENING = "listening"
    READING = "reading"
    WRITING = "writing"
    SPEAKING = "speaking"
    VOCABULARY = "vocabulary"
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"


class Trend(str, enum.Enum):
    """Score trend direction."""
    IMPROVING = "improving"
    STABLE = "stable"
    DECLINING = "declining"
    INSUFFICIENT_DATA = "insufficient_data"


class Learner(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Core learner entity."""
    __tablename__ = "learners"

    external_user_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    target_exam: Mapped[str] = mapped_column(String(50), default="IELTS Academic")
    target_overall_band: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    exam_date: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    timezone: Mapped[str] = mapped_column(String(50), default="UTC")
    baseline_status: Mapped[BaselineStatus] = mapped_column(
        Enum(BaselineStatus), default=BaselineStatus.PENDING
    )

    # Relationships
    skill_states: Mapped[list["SkillState"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    attempts: Mapped[list["Attempt"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    weaknesses: Mapped[list["Weakness"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    learning_items: Mapped[list["LearningItem"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    practice_sessions: Mapped[list["PracticeSession"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    recommendations: Mapped[list["Recommendation"]] = relationship(back_populates="learner", cascade="all, delete-orphan")
    events: Mapped[list["LearnerEvent"]] = relationship(back_populates="learner", cascade="all, delete-orphan")


class SkillState(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Current state of a learner's skill."""
    __tablename__ = "skill_states"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    skill: Mapped[Skill] = mapped_column(Enum(Skill), nullable=False)
    estimated_band: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, default=0.0)
    recent_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    rolling_score: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    trend: Mapped[Trend] = mapped_column(Enum(Trend), default=Trend.INSUFFICIENT_DATA)
    practice_count: Mapped[int] = mapped_column(Integer, default=0)
    last_practiced_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    last_assessed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="skill_states")

    __table_args__ = (
        # Unique constraint: one skill state per learner per skill
        {"schema": None},
    )
