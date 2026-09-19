"""Pydantic schemas for attempt and assessment operations."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

from app.models.attempt import AttemptSource
from app.models.learner import Skill


class AttemptCreate(BaseModel):
    """Schema for creating a new attempt."""

    learner_id: uuid.UUID
    skill: Skill
    task_type: str
    prompt_id: uuid.UUID | None = None
    raw_input: str | None = None
    normalized_input: str | None = None
    submitted_at: datetime
    duration_ms: int | None = None
    source: AttemptSource
    metadata_json: dict[str, Any] | None = None


class AttemptRead(BaseModel):
    """Schema for reading attempt data."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    learner_id: uuid.UUID
    skill: Skill
    task_type: str
    submitted_at: datetime
    duration_ms: int | None
    source: AttemptSource
    created_at: datetime


class CriterionScoreCreate(BaseModel):
    """Schema for creating a criterion score."""

    criterion: str
    score: float = Field(ge=0, le=9)
    confidence: float = Field(ge=0, le=1)
    evidence_json: dict[str, Any]


class AssessmentCreate(BaseModel):
    """Schema for creating an assessment."""

    attempt_id: uuid.UUID
    estimated_band: float = Field(ge=0, le=9)
    confidence: float = Field(ge=0, le=1)
    evaluator_version: str
    evidence_json: dict[str, Any]
    criterion_scores: list[CriterionScoreCreate] = []


class AssessmentRead(BaseModel):
    """Schema for reading assessment data."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    attempt_id: uuid.UUID
    estimated_band: float
    confidence: float
    evaluator_version: str
    evidence_json: dict[str, Any]
    created_at: datetime
