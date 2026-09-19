"""IELTS Grammar Mastery Engine (Phase P25).

Distinguishes declarative knowledge from spontaneous operational control:
- recognition (identifying error or rule in multiple choice)
- controlled_production (gap-fill / sentence transformation)
- free_production (generating original complex sentences)
- IELTS_transfer (using correctly under real timed essay/speaking conditions)
"""

from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel, Field


class GrammarDimension(str, enum.Enum):
    """Four pedagogical stages of grammatical acquisition."""

    RECOGNITION = "recognition"
    CONTROLLED_PRODUCTION = "controlled_production"
    FREE_PRODUCTION = "free_production"
    IELTS_TRANSFER = "ielts_transfer"


class GrammarPoint(BaseModel):
    """Target grammatical structure or error pattern."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    structure_name: str
    category: str  # e.g. "conditionals", "inversion", "complex_sentence", "articles"
    rule_explanation: str
    target_band: float = 7.0
    dimension_scores: dict[GrammarDimension, float] = Field(
        default_factory=lambda: {dim: 0.0 for dim in GrammarDimension}
    )
    attempt_counts: dict[GrammarDimension, int] = Field(
        default_factory=lambda: {dim: 0 for dim in GrammarDimension}
    )


class GrammarService:
    """Evaluates and tracks grammar mastery across acquisition stages."""

    @classmethod
    def record_attempt(
        cls,
        point: GrammarPoint,
        dimension: GrammarDimension,
        success: bool,
    ) -> GrammarPoint:
        """Records practice attempt and adjusts score for specific stage."""
        current = point.dimension_scores.get(dimension, 0.0)
        point.attempt_counts[dimension] = point.attempt_counts.get(dimension, 0) + 1

        delta = 0.20 if success else -0.25
        new_score = max(0.0, min(1.0, current + delta))
        point.dimension_scores[dimension] = round(new_score, 2)
        return point

    @classmethod
    def calculate_operational_mastery(cls, point: GrammarPoint) -> float:
        """Calculates true spontaneous mastery, weighting transfer and production far above recognition."""
        # Knowing the rule (recognition) != spontaneous mastery (transfer)
        weights = {
            GrammarDimension.RECOGNITION: 0.10,
            GrammarDimension.CONTROLLED_PRODUCTION: 0.20,
            GrammarDimension.FREE_PRODUCTION: 0.35,
            GrammarDimension.IELTS_TRANSFER: 0.35,
        }
        score = sum(point.dimension_scores.get(dim, 0.0) * w for dim, w in weights.items())
        return round(score, 2)

    @classmethod
    def is_spontaneously_controlled(cls, point: GrammarPoint) -> bool:
        """Returns True only if the learner has demonstrated reliability in real IELTS transfer."""
        transfer_score = point.dimension_scores.get(GrammarDimension.IELTS_TRANSFER, 0.0)
        free_score = point.dimension_scores.get(GrammarDimension.FREE_PRODUCTION, 0.0)
        return transfer_score >= 0.75 and free_score >= 0.70
