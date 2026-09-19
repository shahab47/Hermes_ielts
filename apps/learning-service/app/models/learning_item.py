"""Learning item and review event models for FSRS integration."""
from __future__ import annotations

import enum
import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, Enum, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin


class ItemType(str, enum.Enum):
    """Type of learning item."""
    VOCABULARY = "vocabulary"
    COLLOCATION = "collocation"
    GRAMMAR_PATTERN = "grammar_pattern"
    PRONUNCIATION_TARGET = "pronunciation_target"
    ACADEMIC_EXPRESSION = "academic_expression"


class MasteryState(str, enum.Enum):
    """Mastery level of a learning item."""
    NEW = "new"
    LEARNING = "learning"
    REVIEWING = "reviewing"
    MASTERED = "mastered"
    LAPSED = "lapsed"


class ReviewRating(int, enum.Enum):
    """FSRS review ratings."""
    AGAIN = 1
    HARD = 2
    GOOD = 3
    EASY = 4


class ReviewType(str, enum.Enum):
    """Type of review activity."""
    RECOGNITION = "recognition"
    PRODUCTION = "production"
    CONTEXTUAL_USE = "contextual_use"


class LearningItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Vocabulary/grammar/micro-skill item tracked with FSRS."""
    __tablename__ = "learning_items"

    learner_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learners.id"), nullable=False)
    item_type: Mapped[ItemType] = mapped_column(Enum(ItemType), nullable=False, index=True)
    canonical_form: Mapped[str] = mapped_column(String(500), nullable=False)
    meaning: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    fsrs_state_json: Mapped[Optional[dict[str, Any]]] = mapped_column(JSONB, nullable=True)
    mastery_state: Mapped[MasteryState] = mapped_column(Enum(MasteryState), default=MasteryState.NEW)

    # Indexed fields for querying FSRS state
    next_review_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True, index=True)
    stability: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    difficulty: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    reps: Mapped[int] = mapped_column(Integer, default=0)
    lapses: Mapped[int] = mapped_column(Integer, default=0)

    # Relationships
    learner: Mapped["Learner"] = relationship(back_populates="learning_items")
    review_events: Mapped[list["ReviewEvent"]] = relationship(back_populates="learning_item", cascade="all, delete-orphan")


class ReviewEvent(Base, UUIDPrimaryKeyMixin):
    """Record of a review session for a learning item."""
    __tablename__ = "review_events"

    learning_item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("learning_items.id"), nullable=False)
    rating: Mapped[ReviewRating] = mapped_column(Enum(ReviewRating), nullable=False)
    review_type: Mapped[ReviewType] = mapped_column(Enum(ReviewType), nullable=False)
    response_time_ms: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, server_default=func.now()
    )

    # Relationships
    learning_item: Mapped["LearningItem"] = relationship(back_populates="review_events")
