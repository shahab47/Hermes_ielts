"""IELTS Full Mock Exam Engine (Phase P30).

Simulates standard IELTS exam sequence:
- Listening (30 mins + 10 mins transfer simulation)
- Reading (60 mins)
- Writing (60 mins)
- Speaking (11-14 mins)

Features feedback isolation during simulation and official IELTS overall band rounding.
"""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field


class MockExamMode(str, enum.Enum):
    """Exam simulation mode."""

    PRACTICE = "practice"
    SPRINT_TIMED = "sprint_timed"
    FULL_MOCK = "full_mock"


class MockSectionResult(BaseModel):
    """Result of an individual exam section."""

    section: str  # "listening", "reading", "writing", "speaking"
    raw_score: float | None = None
    band_score: float = Field(ge=0.0, le=9.0)
    time_spent_seconds: float
    completed_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    section_summary: dict[str, Any] = Field(default_factory=dict)


class MockExamSession(BaseModel):
    """Full IELTS mock examination state and score record."""

    mock_exam_id: uuid.UUID = Field(default_factory=uuid.uuid4)
    mode: MockExamMode
    is_completed: bool = False
    feedback_isolated: bool = True
    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    completed_at: datetime | None = None

    # Section bands
    listening_band: float | None = None
    reading_band: float | None = None
    writing_band: float | None = None
    speaking_band: float | None = None
    overall_band: float | None = None

    section_results: dict[str, MockSectionResult] = Field(default_factory=dict)


class MockExamService:
    """Orchestrates mock exam sessions and official scoring."""

    @classmethod
    def calculate_official_overall_band(
        cls,
        listening: float,
        reading: float,
        writing: float,
        speaking: float,
    ) -> float:
        """Calculates official IELTS overall band score with the authoritative rounding rule:

        Average ending in >= 0.25 and < 0.75 rounds to .5
        Average ending in >= 0.75 rounds up to next whole band
        Average ending in < 0.25 rounds down to current whole band
        """
        mean = (listening + reading + writing + speaking) / 4.0
        int_part = int(mean)
        decimal = mean - int_part

        if decimal < 0.25:
            return float(int_part)
        elif decimal < 0.75:
            return float(int_part) + 0.5
        else:
            return float(int_part + 1)

    @classmethod
    def start_exam(cls, mode: MockExamMode = MockExamMode.FULL_MOCK) -> MockExamSession:
        """Initializes a new mock exam session."""
        return MockExamSession(
            mode=mode,
            feedback_isolated=(mode == MockExamMode.FULL_MOCK),
        )

    @classmethod
    def record_section(
        cls,
        session: MockExamSession,
        section: str,
        band_score: float,
        time_spent_seconds: float,
        raw_score: float | None = None,
        summary: dict[str, Any] | None = None,
    ) -> MockExamSession:
        """Records section completion."""
        sec_name = section.lower()
        res = MockSectionResult(
            section=sec_name,
            raw_score=raw_score,
            band_score=band_score,
            time_spent_seconds=time_spent_seconds,
            section_summary=summary or {},
        )
        session.section_results[sec_name] = res

        if sec_name == "listening":
            session.listening_band = band_score
        elif sec_name == "reading":
            session.reading_band = band_score
        elif sec_name == "writing":
            session.writing_band = band_score
        elif sec_name == "speaking":
            session.speaking_band = band_score

        return session

    @classmethod
    def finalize_exam(cls, session: MockExamSession) -> MockExamSession:
        """Finalizes exam, lifts feedback isolation, and computes overall band."""
        if (
            session.listening_band is not None
            and session.reading_band is not None
            and session.writing_band is not None
            and session.speaking_band is not None
        ):
            session.overall_band = cls.calculate_official_overall_band(
                session.listening_band,
                session.reading_band,
                session.writing_band,
                session.speaking_band,
            )

        session.is_completed = True
        session.feedback_isolated = False
        session.completed_at = datetime.now(UTC)
        return session
