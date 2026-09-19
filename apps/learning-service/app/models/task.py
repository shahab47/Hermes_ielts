"""Task, practice session, and recommendation models."""

from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.learner import Learner

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.learner import Skill


class TaskDifficulty(str, enum.Enum):
    """Task difficulty level."""

    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    UPPER_INTERMEDIATE = "upper_intermediate"
    ADVANCED = "advanced"


class TaskSource(str, enum.Enum):
    """Provenance of a task."""

    OFFICIAL_PUBLIC = "official_public"
    GENERATED = "generated"
    USER_PROVIDED = "user_provided"
    OPEN_EDUCATIONAL = "open_educational"


class CompletionStatus(str, enum.Enum):
    """Practice session completion status."""

    PLANNED = "planned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    ABANDONED = "abandoned"
    SKIPPED = "skipped"


class RecommendationType(str, enum.Enum):
    """Type of recommendation."""

    PRACTICE_TASK = "practice_task"
    REVIEW_SESSION = "skill_focus"
    SKILL_FOCUS = "skill_focus"
    STRATEGY_CHANGE = "strategy_change"
    REST = "rest"


class RecommendationStatus(str, enum.Enum):
    """Recommendation lifecycle status."""

    ACTIVE = "active"
    ACCEPTED = "accepted"
    COMPLETED = "completed"
    DECLINED = "declined"
    EXPIRED = "expired"


class Task(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """IELTS practice task / exercise."""

    __tablename__ = "tasks"

    skill: Mapped[Skill] = mapped_column(Enum(Skill), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(Enum(TaskDifficulty), nullable=False)
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source: Mapped[TaskSource] = mapped_column(Enum(TaskSource), nullable=False)
    provenance: Mapped[str | None] = mapped_column(Text, nullable=True)
    content_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    answer_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    rubric_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)


class PracticeSession(Base, UUIDPrimaryKeyMixin):
    """A practice session grouping multiple activities."""

    __tablename__ = "practice_sessions"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    planned_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    actual_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    objectives_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    completion_status: Mapped[CompletionStatus] = mapped_column(
        Enum(CompletionStatus), default=CompletionStatus.PLANNED
    )

    # Relationships
    learner: Mapped[Learner] = relationship(back_populates="practice_sessions")


class Recommendation(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """System recommendation for the learner."""

    __tablename__ = "recommendations"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    recommendation_type: Mapped[RecommendationType] = mapped_column(Enum(RecommendationType), nullable=False)
    rationale: Mapped[str] = mapped_column(Text, nullable=False)
    priority: Mapped[float] = mapped_column(Float, default=0.0)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    status: Mapped[RecommendationStatus] = mapped_column(
        Enum(RecommendationStatus), default=RecommendationStatus.ACTIVE
    )

    # Relationships
    learner: Mapped[Learner] = relationship(back_populates="recommendations")
