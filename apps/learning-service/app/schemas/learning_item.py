"""Pydantic schemas for learning items and reviews."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel

from app.models.learning_item import ItemType, MasteryState, ReviewRating, ReviewType


class LearningItemCreate(BaseModel):
    """Schema for creating a learning item."""

    learner_id: uuid.UUID
    item_type: ItemType
    canonical_form: str
    meaning: str | None = None
    metadata_json: dict[str, Any] | None = None


class LearningItemRead(BaseModel):
    """Schema for reading a learning item."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    learner_id: uuid.UUID
    item_type: ItemType
    canonical_form: str
    meaning: str | None
    mastery_state: MasteryState
    next_review_at: datetime | None
    stability: float | None
    difficulty: float | None
    reps: int
    lapses: int
    created_at: datetime


class ReviewSubmit(BaseModel):
    """Schema for submitting a review."""

    learning_item_id: uuid.UUID
    rating: ReviewRating
    review_type: ReviewType
    response_time_ms: int | None = None
