"""SQLAlchemy ORM models for IELTS Question Bank (Phase P14)."""

from __future__ import annotations

import uuid
from typing import Any

from sqlalchemy import Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.learner import Skill
from app.models.task import TaskDifficulty


class QuestionSetModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Collection of related IELTS questions (Listening section, Reading passage, or complete Mock)."""

    __tablename__ = "question_sets"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    skill: Mapped[Skill] = mapped_column(String(50), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    time_limit_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    passage_or_transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    provenance_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    questions: Mapped[list[QuestionModel]] = relationship(
        back_populates="question_set",
        cascade="all, delete-orphan",
        order_by="QuestionModel.created_at",
    )


class QuestionModel(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Individual question entity supporting 11 Listening and 10 Reading types."""

    __tablename__ = "questions"

    question_set_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("question_sets.id"),
        nullable=True,
        index=True,
    )
    skill: Mapped[Skill] = mapped_column(String(50), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    question_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(
        String(50), default=TaskDifficulty.INTERMEDIATE, nullable=False
    )
    cefr: Mapped[str | None] = mapped_column(String(20), nullable=True)
    prompt: Mapped[str] = mapped_column(Text, nullable=False)
    instructions: Mapped[str | None] = mapped_column(Text, nullable=True)
    options_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    answer_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    explanation_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    media_json: Mapped[list[dict[str, Any]] | None] = mapped_column(JSONB, nullable=True)
    tags: Mapped[list[str] | None] = mapped_column(JSONB, nullable=True)
    provenance_json: Mapped[dict[str, Any]] = mapped_column(JSONB, nullable=False)
    review_status: Mapped[str] = mapped_column(String(50), default="validated", nullable=False)
    quality_score: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    version: Mapped[int] = mapped_column(Integer, default=1, nullable=False)

    question_set: Mapped[QuestionSetModel | None] = relationship(back_populates="questions")
