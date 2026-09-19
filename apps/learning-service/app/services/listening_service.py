"""IELTS Listening practice and scoring engine (Phase P18).

Provides audio exercise selection, deterministic answer normalization,
band scaling (out of 40), question-type analytics, and transcript reveal.
"""

from __future__ import annotations

import re
import uuid

from pydantic import BaseModel, Field

from app.domain.question_bank import Question, QuestionSet


class ListeningSubmission(BaseModel):
    """User submitted answers for a listening exercise."""

    question_id: uuid.UUID
    user_answer: str


class ListeningQuestionResult(BaseModel):
    """Result of grading a single listening question."""

    question_id: uuid.UUID
    question_type: str
    user_answer: str
    is_correct: bool
    accepted_answers: list[str]
    explanation: str
    target_evidence: str | None = None


class ListeningSessionResult(BaseModel):
    """Comprehensive evaluation of a completed listening section or full test."""

    total_questions: int
    correct_count: int
    raw_score: int
    band_score: float = Field(ge=0.0, le=9.0)
    question_type_accuracy: dict[str, float]
    results: list[ListeningQuestionResult]
    revealed_transcript: str | None = None


class ListeningService:
    """Core domain service for IELTS Listening practice sessions."""

    # Public official IELTS Listening raw score to band score conversion table
    BAND_TABLE_LISTENING: list[tuple[int, float]] = [
        (39, 9.0),
        (37, 8.5),
        (35, 8.0),
        (32, 7.5),
        (30, 7.0),
        (26, 6.5),
        (23, 6.0),
        (18, 5.5),
        (16, 5.0),
        (13, 4.5),
        (10, 4.0),
        (6, 3.5),
        (4, 3.0),
        (0, 2.5),
    ]

    @classmethod
    def normalize_answer(cls, answer: str) -> str:
        """Normalizes user response: lowercase, strip punctuation and superfluous articles."""
        cleaned = answer.strip().lower()
        # Remove trailing period or comma
        cleaned = re.sub(r"[\.,;:!?]+$", "", cleaned)
        # Collapse multiple spaces
        cleaned = re.sub(r"\s+", " ", cleaned)
        # Strip leading articles 'a ', 'an ', 'the ' for single-word / noun answers
        tokens = cleaned.split()
        if len(tokens) > 1 and tokens[0] in ("a", "an", "the"):
            tokens = tokens[1:]
        return " ".join(tokens)

    @classmethod
    def calculate_band(cls, correct_count: int, total_questions: int = 40) -> float:
        """Scales raw score out of total_questions to standard IELTS 0-9 band scale."""
        if total_questions <= 0 or correct_count <= 0:
            return 0.0

        # Scale to 40-question equivalent
        scaled_raw = round((correct_count / total_questions) * 40)
        for min_raw, band in cls.BAND_TABLE_LISTENING:
            if scaled_raw >= min_raw:
                return band
        return 2.5

    @classmethod
    def grade_question(cls, question: Question, user_answer: str) -> ListeningQuestionResult:
        """Grades a single question deterministically against accepted values."""
        norm_user = cls.normalize_answer(user_answer)
        is_correct = False

        for accepted in question.answer.accepted_values:
            norm_accepted = cls.normalize_answer(accepted)
            if norm_user == norm_accepted:
                is_correct = True
                break
            # Check pattern if specified
            if question.answer.regex_pattern and re.match(question.answer.regex_pattern, user_answer.strip()):
                is_correct = True
                break

        return ListeningQuestionResult(
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
        submissions: list[ListeningSubmission],
        reveal_transcript: bool = False,
    ) -> ListeningSessionResult:
        """Evaluates all submissions in a session and computes question-type analytics."""
        sub_map = {s.question_id: s.user_answer for s in submissions}
        results: list[ListeningQuestionResult] = []
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

        type_accuracy = {
            t: round(type_correct.get(t, 0) / count, 2)
            for t, count in type_totals.items()
        }

        revealed = question_set.passage_or_transcript if reveal_transcript else None

        return ListeningSessionResult(
            total_questions=total_questions,
            correct_count=correct_count,
            raw_score=correct_count,
            band_score=band,
            question_type_accuracy=type_accuracy,
            results=results,
            revealed_transcript=revealed,
        )
