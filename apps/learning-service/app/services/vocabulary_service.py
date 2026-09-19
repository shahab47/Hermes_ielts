"""IELTS Vocabulary Engine tracking multi-dimensional lexical mastery (Phase P23).

Separately tracks:
- recognition
- production
- contextual_use
- collocation
- register
- spelling
- pronunciation
"""

from __future__ import annotations

import enum
import uuid

from pydantic import BaseModel, Field

from app.domain.question_bank import CEFRLevel


class VocabularyDimension(str, enum.Enum):
    """The 7 distinct dimensions of vocabulary mastery required by Phase P23."""

    RECOGNITION = "recognition"
    PRODUCTION = "production"
    CONTEXTUAL_USE = "contextual_use"
    COLLOCATION = "collocation"
    REGISTER = "register"
    SPELLING = "spelling"
    PRONUNCIATION = "pronunciation"


class VocabularyItem(BaseModel):
    """Rich domain representation of a lexical item."""

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    term: str
    part_of_speech: str = "noun"
    cefr: CEFRLevel = CEFRLevel.B2
    is_academic: bool = True
    awl_sublist: int | None = None
    definition: str
    collocations: list[str] = Field(default_factory=list)
    register_level: str = "academic"  # academic, formal, neutral, informal
    example_sentences: list[str] = Field(default_factory=list)
    dimension_scores: dict[VocabularyDimension, float] = Field(
        default_factory=lambda: {dim: 0.0 for dim in VocabularyDimension}
    )
    attempt_counts: dict[VocabularyDimension, int] = Field(
        default_factory=lambda: {dim: 0 for dim in VocabularyDimension}
    )


class VocabularyService:
    """Core domain service for tracking and drills across vocabulary dimensions."""

    @classmethod
    def record_dimension_attempt(
        cls,
        item: VocabularyItem,
        dimension: VocabularyDimension,
        success: bool,
    ) -> VocabularyItem:
        """Updates specific dimension mastery using an exponential moving average."""
        current_score = item.dimension_scores.get(dimension, 0.0)
        item.attempt_counts[dimension] = item.attempt_counts.get(dimension, 0) + 1

        delta = 0.25 if success else -0.30
        new_score = max(0.0, min(1.0, current_score + delta))
        item.dimension_scores[dimension] = round(new_score, 2)
        return item

    @classmethod
    def check_spelling(cls, item: VocabularyItem, user_spelling: str) -> tuple[bool, str]:
        """Validates exact spelling match (case-insensitive) and updates spelling dimension."""
        correct = item.term.strip().lower() == user_spelling.strip().lower()
        cls.record_dimension_attempt(item, VocabularyDimension.SPELLING, correct)
        feedback = "Correct spelling." if correct else f"Incorrect. Correct spelling is '{item.term}'."
        return correct, feedback

    @classmethod
    def check_collocation(
        cls,
        item: VocabularyItem,
        user_collocation: str,
    ) -> tuple[bool, str]:
        """Validates whether user produced an authentic natural academic collocation."""
        user_clean = user_collocation.strip().lower()
        matched = False
        for col in item.collocations:
            if col.lower() in user_clean or user_clean in col.lower():
                matched = True
                break

        cls.record_dimension_attempt(item, VocabularyDimension.COLLOCATION, matched)
        if matched:
            return True, f"Strong academic collocation for '{item.term}'."
        collocations_sample = ", ".join(item.collocations[:3])
        return False, f"Uncommon collocation. Typical academic collocations include: {collocations_sample}."

    @classmethod
    def calculate_overall_mastery(cls, item: VocabularyItem) -> float:
        """Weighted arithmetic average across all 7 dimensions."""
        weights = {
            VocabularyDimension.RECOGNITION: 0.10,
            VocabularyDimension.PRODUCTION: 0.20,
            VocabularyDimension.CONTEXTUAL_USE: 0.20,
            VocabularyDimension.COLLOCATION: 0.20,
            VocabularyDimension.REGISTER: 0.10,
            VocabularyDimension.SPELLING: 0.10,
            VocabularyDimension.PRONUNCIATION: 0.10,
        }
        total = sum(item.dimension_scores.get(dim, 0.0) * w for dim, w in weights.items())
        return round(total, 2)
