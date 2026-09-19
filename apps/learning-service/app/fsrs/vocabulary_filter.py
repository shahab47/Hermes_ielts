"""Vocabulary and grammar micro-skill eligibility filter and 2D mastery."""

from __future__ import annotations

import enum

from pydantic import BaseModel

from app.models.learning_item import ItemType


class ReviewEligibilityReason(str, enum.Enum):
    """Why an item was accepted into the spaced repetition system."""

    REPEATED_ERROR = "repeated_error"
    ACADEMIC_COLLOCATION = "academic_collocation"
    USER_REQUEST = "user_request"
    HIGH_TASK_VALUE = "high_task_value"


class ItemCandidate(BaseModel):
    """Candidate vocabulary or grammar pattern under evaluation."""

    canonical_form: str
    item_type: ItemType
    occurrence_count: int = 1
    has_learner_error: bool = False
    is_explicit_request: bool = False
    is_academic_word_list: bool = False
    meaning: str | None = None


class ItemFilterDecision(BaseModel):
    """Decision on whether a candidate becomes a tracked learning item."""

    canonical_form: str
    is_accepted: bool
    reason: ReviewEligibilityReason | None = None
    rationale: str


class VocabularyFilter:
    """Enforces non-negotiable rule: Never automatically add every word the LLM sees."""

    @classmethod
    def evaluate_candidate(cls, candidate: ItemCandidate) -> ItemFilterDecision:
        """Decide if a candidate item is worthy of spaced repetition review."""
        # Rule 1: Explicit learner request -> always accept
        if candidate.is_explicit_request:
            return ItemFilterDecision(
                canonical_form=candidate.canonical_form,
                is_accepted=True,
                reason=ReviewEligibilityReason.USER_REQUEST,
                rationale="Explicitly requested by the learner for study.",
            )

        # Rule 2: Learner error -> accept to remediate weakness
        if candidate.has_learner_error:
            return ItemFilterDecision(
                canonical_form=candidate.canonical_form,
                is_accepted=True,
                reason=ReviewEligibilityReason.REPEATED_ERROR,
                rationale="Identified in learner output with an associated lexical or grammatical error.",
            )

        # Rule 3: Academic word list / high task value with repeat occurrence
        if candidate.is_academic_word_list and candidate.occurrence_count >= 2:
            return ItemFilterDecision(
                canonical_form=candidate.canonical_form,
                is_accepted=True,
                reason=ReviewEligibilityReason.ACADEMIC_COLLOCATION,
                rationale="High-yield Academic Word List item observed across multiple practice opportunities.",
            )

        # Default rejection: incidental word without pedagogical justification
        return ItemFilterDecision(
            canonical_form=candidate.canonical_form,
            is_accepted=False,
            rationale="Incidental vocabulary; does not meet recurrence, error, or academic value thresholds.",
        )
