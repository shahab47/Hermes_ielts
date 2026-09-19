"""Pydantic schemas for learner-related API operations."""

from __future__ import annotations

import uuid
from datetime import datetime

from pydantic import BaseModel

from app.models.learner import BaselineStatus, Skill, Trend


class LearnerCreate(BaseModel):
    """Schema for creating a new learner."""

    external_user_id: str
    target_exam: str = "IELTS Academic"
    target_overall_band: float | None = None
    exam_date: datetime | None = None
    timezone: str = "UTC"


class LearnerRead(BaseModel):
    """Schema for reading learner data."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    external_user_id: str
    target_exam: str
    target_overall_band: float | None
    exam_date: datetime | None
    timezone: str
    baseline_status: BaselineStatus
    created_at: datetime
    updated_at: datetime


class SkillStateRead(BaseModel):
    """Schema for reading skill state."""

    model_config = {"from_attributes": True}

    id: uuid.UUID
    skill: Skill
    estimated_band: float | None
    confidence: float
    recent_score: float | None
    rolling_score: float | None
    trend: Trend
    practice_count: int
    last_practiced_at: datetime | None
    last_assessed_at: datetime | None


class LearnerProfile(BaseModel):
    """Complete learner profile with skill states."""

    learner: LearnerRead
    skill_states: list[SkillStateRead] = []
