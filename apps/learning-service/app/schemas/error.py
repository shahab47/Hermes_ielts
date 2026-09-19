"""Pydantic schemas for error events and weaknesses."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.error import ErrorCategory, ErrorSeverity, WeaknessStatus


class ErrorEventCreate(BaseModel):
    """Schema for recording an error event."""
    attempt_id: uuid.UUID
    category: ErrorCategory
    subtype: str
    evidence_text: str
    severity: ErrorSeverity
    recurrence_group: Optional[str] = None
    confidence: float = Field(ge=0, le=1)


class ErrorEventRead(BaseModel):
    """Schema for reading an error event."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    attempt_id: uuid.UUID
    category: ErrorCategory
    subtype: str
    evidence_text: str
    severity: ErrorSeverity
    confidence: float
    created_at: datetime


class WeaknessRead(BaseModel):
    """Schema for reading a weakness."""
    model_config = {"from_attributes": True}

    id: uuid.UUID
    learner_id: uuid.UUID
    category: ErrorCategory
    subtype: str
    status: WeaknessStatus
    recurrence_rate: float
    impact_estimate: float
    confidence: float
    priority: float
    first_seen_at: datetime
    last_seen_at: datetime
    resolved_at: Optional[datetime]
