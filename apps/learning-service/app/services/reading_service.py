"""IELTS Reading practice, speed metrics (WPM), and scoring engine (Phase P19).

Computes reading speed, deterministic band scaling for Academic Reading,
question-type breakdowns, and adaptive diagnostic recommendations.
"""

from __future__ import annotations

import re
import uuid

from pydantic import BaseModel, Field

from app.domain.question_bank import Question, QuestionSet, ReadingQuestionType


class ReadingSubmission(BaseModel):
    """User submitted answers for a reading passage."""

    question_id: uuid.UUID
    user_answer: str


class ReadingQuestionResult(BaseModel):
    """Result of grading a single reading question."""

    question_id: uuid.UUID
    question_type: str
    user_answer: str
    is_correct: bool
    accepted_answers: list[str]
    explanation: str
    target_evidence: str | None = None


class ReadingSessionResult(BaseModel):
    """Comprehensive evaluation of a reading passage or section."""

    total_questions: int
    correct_count: int
    raw_score: int
    band_score: float = Field(ge=0.0, le=9.0)
    reading_speed_wpm: float = Field(ge=0.0)
    question_type_accuracy: dict[str, float]
    weakest_question_type: str | None = None
    recommended_drill: str | None = None
    results: list[ReadingQuestionResult]


class ReadingService:
    """Core domain service for IELTS Academic Reading."""

    # Public official IELTS Academic Reading raw score to band conversion table
    BAND_TABLE_ACADEMIC_READING: list[tuple[int, float]] = [
        (39, 9.0),
        (37, 8.5),
        (35, 8.0),
        (33, 7.5),
        (30, 7.0),
        (27, 6.5),
        (23, 6.0),
        (19, 5.5),
        (15, 5.0),
        (13, 4.5),
        (10, 4.0),
        (8, 3.5),
        (6, 3.0),
        (0, 2.5),
    ]

    @classmethod
    def normalize_answer(cls, answer: str, question_type: str | None = None) -> str:
        """Standardizes user answers, converting abbreviations (T/F/NG, Y/N) to canonical forms."""
        cleaned = answer.strip().lower()
        cleaned = re.sub(r"[\.,;:!?]+$", "", cleaned)
        cleaned = re.sub(r"\s+", " ", cleaned)

        # Normalize TFNG
        if question_type == ReadingQuestionType.TFNG:
            if cleaned in ("t", "true"):
                return "true"
            if cleaned in ("f", "false"):
                return "false"
            if cleaned in ("ng", "not given", "notgiven"):
                return "not given"

        # Normalize YNNG
        if question_type == ReadingQuestionType.YNNG:
            if cleaned in ("y", "yes"):
                return "yes"
            if cleaned in ("n", "no"):
                return "no"
            if cleaned in ("ng", "not given", "notgiven"):
                return "not given"

        # Strip leading articles
        tokens = cleaned.split()
        if len(tokens) > 1 and tokens[0] in ("a", "an", "the"):
            tokens = tokens[1:]
        return " ".join(tokens)

    @classmethod
    def calculate_reading_speed(cls, passage_text: str, duration_seconds: float) -> float:
        """Calculates reading speed in Words Per Minute (WPM)."""
        if duration_seconds <= 0 or not passage_text.strip():
            return 0.0
        word_count = len(passage_text.split())
        minutes = duration_seconds / 60.0
        return round(word_count / minutes, 1)

    @classmethod
    def calculate_band(cls, correct_count: int, total_questions: int = 40) -> float:
        """Scales raw score out of total_questions to IELTS Academic Reading band."""
        if total_questions <= 0 or correct_count <= 0:
            return 0.0

        scaled_raw = round((correct_count / total_questions) * 40)
        for min_raw, band in cls.BAND_TABLE_ACADEMIC_READING:
            if scaled_raw >= min_raw:
                return band
        return 2.5

    @classmethod
    def grade_question(cls, question: Question, user_answer: str) -> ReadingQuestionResult:
        """Grades a reading question deterministically."""
        norm_user = cls.normalize_answer(user_answer, question.question_type)
        is_correct = False

        for accepted in question.answer.accepted_values:
            norm_accepted = cls.normalize_answer(accepted, question.question_type)
            if norm_user == norm_accepted:
                is_correct = True
                break

        return ReadingQuestionResult(
            question_id=question.id,
            question_type=question.question_type,
            user_answer=user_answer,
            is_correct=is_correct,
            accepted_answers=question.answer.accepted_values,
            explanation=question.explanation.text,
            target_evidence=question.explanation.target_evidence,
        )

    @classmethod
    def evaluate_session(
        cls,
        question_set: QuestionSet,
        submissions: list[ReadingSubmission],
        elapsed_seconds: float = 1200.0,  # default 20 mins for 1 passage
    ) -> ReadingSessionResult:
        """Evaluates session, calculates WPM, detects question-type weaknesses, and proposes drills."""
        sub_map = {s.question_id: s.user_answer for s in submissions}
        results: list[ReadingQuestionResult] = []
        type_totals: dict[str, int] = {}
        type_correct: dict[str, int] = {}

        for q in question_set.questions:
            user_ans = sub_map.get(q.id, "")
            res = cls.grade_question(q, user_ans)
            results.append(res)

            q_type = q.question_type
            type_totals[q_type] = type_totals.get(q_type, 0) + 1
            if res.is_correct:
                type_correct[q_type] = type_correct.get(q_type, 0) + 1

        correct_count = sum(1 for r in results if r.is_correct)
        total_questions = len(question_set.questions)
        band = cls.calculate_band(correct_count, total_questions)

        # WPM
        passage_text = question_set.passage_or_transcript or ""
        wpm = cls.calculate_reading_speed(passage_text, elapsed_seconds)

        # Question type analytics
        type_accuracy = {
            t: round(type_correct.get(t, 0) / count, 2)
            for t, count in type_totals.items()
        }

        # Find weakest type
        weakest_type = None
        lowest_acc = 1.0
        for t, acc in type_accuracy.items():
            if acc < lowest_acc:
                lowest_acc = acc
                weakest_type = t

        recommended_drill = None
        if weakest_type and lowest_acc < 0.7:
            recommended_drill = f"5-item focused drill on {weakest_type}"

        return ReadingSessionResult(
            total_questions=total_questions,
            correct_count=correct_count,
            raw_score=correct_count,
            band_score=band,
            reading_speed_wpm=wpm,
            question_type_accuracy=type_accuracy,
            weakest_question_type=weakest_type,
            recommended_drill=recommended_drill,
            results=results,
        )
