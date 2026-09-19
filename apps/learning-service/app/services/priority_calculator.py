"""Deterministic priority score calculator for IELTS weaknesses and learning targets."""

from __future__ import annotations

import math
from datetime import UTC, datetime

from pydantic import BaseModel, Field


class PriorityBreakdown(BaseModel):
    """Detailed breakdown of priority score components."""

    recurrence_score: float = Field(ge=0.0, le=1.0, description="Normalized recurrence frequency")
    impact_score: float = Field(ge=0.0, le=1.0, description="Estimated IELTS band score impact")
    confidence_score: float = Field(ge=0.0, le=1.0, description="Confidence in assessment/detection")
    recency_score: float = Field(ge=0.0, le=1.0, description="Recency decay factor")
    task_relevance_score: float = Field(ge=0.0, le=1.0, description="Relevance to target exam tasks")
    target_gap_score: float = Field(ge=0.0, le=1.0, description="Gap to learner target band")
    final_priority: float = Field(ge=0.0, le=1.0, description="Weighted aggregate priority [0, 1]")


class PriorityCalculator:
    """Computes deterministic priority score for weaknesses.

    Formula combines:
    - recurrence: frequency across separate attempts
    - estimated score impact: potential band deduction
    - confidence: measurement certainty
    - recency: time-decay factor (newer = higher priority)
    - task relevance: importance for the target exam modules
    - target gap: urgency relative to target band score
    """

    # Configurable component weights (sum to 1.0)
    WEIGHT_RECURRENCE = 0.25
    WEIGHT_IMPACT = 0.25
    WEIGHT_CONFIDENCE = 0.15
    WEIGHT_RECENCY = 0.15
    WEIGHT_TARGET_GAP = 0.10
    WEIGHT_TASK_RELEVANCE = 0.10

    # Half-life for recency decay in days (errors older than 14 days have lower weight)
    RECENCY_HALF_LIFE_DAYS = 14.0

    @classmethod
    def compute(
        cls,
        recurrence_count: int,
        estimated_band_impact: float,
        confidence: float,
        last_seen_at: datetime,
        current_band: float | None = None,
        target_band: float | None = None,
        task_relevance: float = 1.0,
        now: datetime | None = None,
    ) -> PriorityBreakdown:
        """Compute structured priority breakdown and final score."""
        if now is None:
            now = datetime.now(UTC)

        # 1. Recurrence score: saturates at 5 occurrences
        norm_recurrence = min(max(recurrence_count / 5.0, 0.0), 1.0)

        # 2. Score impact: IELTS bands are in 0.5 steps. 1.0 band impact = maximum urgency
        norm_impact = min(max(estimated_band_impact / 1.0, 0.0), 1.0)

        # 3. Confidence score: bounded [0, 1]
        norm_confidence = min(max(confidence, 0.0), 1.0)

        # 4. Recency decay: exponential decay based on half-life
        delta_days = max((now - last_seen_at).total_seconds() / 86400.0, 0.0)
        norm_recency = math.exp(-math.log(2) * (delta_days / cls.RECENCY_HALF_LIFE_DAYS))

        # 5. Target gap score: larger gap = higher urgency
        if target_band is not None and current_band is not None:
            gap = max(target_band - current_band, 0.0)
            norm_gap = min(gap / 2.0, 1.0)  # 2 bands gap saturates to 1.0
        else:
            norm_gap = 0.5  # Neutral default when target or current is unmeasured

        # 6. Task relevance
        norm_relevance = min(max(task_relevance, 0.0), 1.0)

        # Final weighted sum
        final = (
            cls.WEIGHT_RECURRENCE * norm_recurrence
            + cls.WEIGHT_IMPACT * norm_impact
            + cls.WEIGHT_CONFIDENCE * norm_confidence
            + cls.WEIGHT_RECENCY * norm_recency
            + cls.WEIGHT_TARGET_GAP * norm_gap
            + cls.WEIGHT_TASK_RELEVANCE * norm_relevance
        )
        final_priority = round(min(max(final, 0.0), 1.0), 4)

        return PriorityBreakdown(
            recurrence_score=round(norm_recurrence, 4),
            impact_score=round(norm_impact, 4),
            confidence_score=round(norm_confidence, 4),
            recency_score=round(norm_recency, 4),
            target_gap_score=round(norm_gap, 4),
            task_relevance_score=round(norm_relevance, 4),
            final_priority=final_priority,
        )
