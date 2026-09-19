"""IELTS Writing verification and pre-assessment analysis."""

from __future__ import annotations

import re

from pydantic import BaseModel, Field

from app.analyzers.rubrics import EssayType, VisualType, WritingTaskType


class WritingPreflightResult(BaseModel):
    """Deterministic pre-assessment checks on submitted writing."""

    task_type: WritingTaskType
    word_count: int = Field(ge=0)
    is_word_count_sufficient: bool
    minimum_words_required: int
    paragraph_count: int
    has_identifiable_overview: bool | None = None  # Task 1
    has_clear_position_markers: bool | None = None  # Task 2
    detected_visual_type: VisualType | None = None
    detected_essay_type: EssayType | None = None
    warnings: list[str] = []


class WritingVerifier:
    """Performs deterministic verification and structural parsing of IELTS essays."""

    TASK1_MIN_WORDS = 150
    TASK2_MIN_WORDS = 250

    OVERVIEW_MARKERS = [
        r"\boverall\b",
        r"\bin summary\b",
        r"\bto summarize\b",
        r"\bit is clear that\b",
        r"\bit is noticeable that\b",
        r"\bit can be seen that\b",
        r"\bthe most striking feature\b",
    ]

    POSITION_MARKERS = [
        r"\bin my opinion\b",
        r"\bi believe\b",
        r"\bi strongly agree\b",
        r"\bi disagree\b",
        r"\bin my view\b",
        r"\bfrom my perspective\b",
        r"\bthis essay argues\b",
        r"\bto my mind\b",
    ]

    @classmethod
    def count_words(cls, text: str) -> int:
        """Count words using academic punctuation-aware tokenization."""
        tokens = re.findall(r"\b[A-Za-z0-9]+(?:[-'][A-Za-z0-9]+)*\b", text)
        return len(tokens)

    @classmethod
    def count_paragraphs(cls, text: str) -> int:
        """Count substantive paragraphs separated by blank lines or indentation."""
        paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
        return max(len(paragraphs), 1)

    @classmethod
    def detect_overview(cls, text: str) -> bool:
        """Detect presence of an overview statement for Task 1."""
        lower = text.lower()
        return any(re.search(marker, lower) for marker in cls.OVERVIEW_MARKERS)

    @classmethod
    def detect_position_markers(cls, text: str) -> bool:
        """Detect clear position indicators for Task 2."""
        lower = text.lower()
        return any(re.search(marker, lower) for marker in cls.POSITION_MARKERS)

    @classmethod
    def verify_task1(
        cls,
        text: str,
        visual_type: VisualType | None = None,
    ) -> WritingPreflightResult:
        """Verify Task 1 submission."""
        words = cls.count_words(text)
        paras = cls.count_paragraphs(text)
        has_overview = cls.detect_overview(text)
        warnings: list[str] = []

        if words < cls.TASK1_MIN_WORDS:
            warnings.append(
                f"Under-length: {words} words (minimum required is {cls.TASK1_MIN_WORDS}). "
                "This directly limits the Task Achievement band score."
            )

        if not has_overview:
            warnings.append(
                "Missing clear overview: Academic Task 1 requires an overview of main trends or key features. "
                "Without an overview, Task Achievement cannot exceed Band 5."
            )

        if paras < 3:
            warnings.append("Inadequate paragraphing: Recommended minimum 3-4 distinct paragraphs.")

        return WritingPreflightResult(
            task_type=WritingTaskType.TASK_1,
            word_count=words,
            is_word_count_sufficient=(words >= cls.TASK1_MIN_WORDS),
            minimum_words_required=cls.TASK1_MIN_WORDS,
            paragraph_count=paras,
            has_identifiable_overview=has_overview,
            detected_visual_type=visual_type,
            warnings=warnings,
        )

    @classmethod
    def verify_task2(
        cls,
        text: str,
        essay_type: EssayType | None = None,
    ) -> WritingPreflightResult:
        """Verify Task 2 submission."""
        words = cls.count_words(text)
        paras = cls.count_paragraphs(text)
        has_pos = cls.detect_position_markers(text)
        warnings: list[str] = []

        if words < cls.TASK2_MIN_WORDS:
            warnings.append(
                f"Under-length: {words} words (minimum required is {cls.TASK2_MIN_WORDS}). "
                "Under-length essays may be penalized under Task Response."
            )

        if paras < 4:
            warnings.append(
                "Insufficient paragraphs: A standard Task 2 essay requires 4-5 paragraphs "
                "(Introduction, 2-3 Body Paragraphs, Conclusion)."
            )

        return WritingPreflightResult(
            task_type=WritingTaskType.TASK_2,
            word_count=words,
            is_word_count_sufficient=(words >= cls.TASK2_MIN_WORDS),
            minimum_words_required=cls.TASK2_MIN_WORDS,
            paragraph_count=paras,
            has_clear_position_markers=has_pos,
            detected_essay_type=essay_type,
            warnings=warnings,
        )

    @classmethod
    def calculate_overall_writing_band(
        cls,
        task1_band: float,
        task2_band: float,
    ) -> float:
        """Compute composite IELTS Writing band score with official weighting.

        Official rule: Task 2 carries TWICE the weight of Task 1 (Task 1 = 1/3, Task 2 = 2/3).
        Final score is rounded to the nearest half or whole band:
        - fractional part < 0.25 -> round down to .0
        - fractional part >= 0.25 and < 0.75 -> round to .5
        - fractional part >= 0.75 -> round up to next .0
        """
        raw_weighted = (task1_band + 2.0 * task2_band) / 3.0
        integer_part = int(raw_weighted)
        remainder = raw_weighted - integer_part

        if remainder < 0.25:
            rounded = float(integer_part)
        elif remainder < 0.75:
            rounded = integer_part + 0.5
        else:
            rounded = float(integer_part + 1)

        return min(max(rounded, 0.0), 9.0)
