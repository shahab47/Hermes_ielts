"""Tests for Pydantic schemas."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from app.schemas.learner import LearnerCreate, LearnerRead
from app.schemas.attempt import AttemptCreate, AssessmentCreate, CriterionScoreCreate
from app.schemas.error import ErrorEventCreate
from app.schemas.learning_item import LearningItemCreate, ReviewSubmit
from app.models.learner import Skill
from app.models.attempt import AttemptSource
from app.models.error import ErrorCategory, ErrorSeverity
from app.models.learning_item import ItemType, ReviewRating, ReviewType


def test_learner_create_defaults() -> None:
    """LearnerCreate uses correct defaults."""
    lc = LearnerCreate(external_user_id="tg_123456")
    assert lc.target_exam == "IELTS Academic"
    assert lc.timezone == "UTC"
    assert lc.target_overall_band is None


def test_attempt_create_validation() -> None:
    """AttemptCreate validates fields correctly."""
    ac = AttemptCreate(
        learner_id=uuid.uuid4(),
        skill=Skill.WRITING,
        task_type="writing_task2",
        submitted_at=datetime.now(timezone.utc),
        source=AttemptSource.TELEGRAM_TEXT,
        raw_input="This is a test essay...",
    )
    assert ac.skill == Skill.WRITING
    assert ac.source == AttemptSource.TELEGRAM_TEXT


def test_assessment_create_with_criteria() -> None:
    """AssessmentCreate accepts criterion scores."""
    ac = AssessmentCreate(
        attempt_id=uuid.uuid4(),
        estimated_band=6.5,
        confidence=0.8,
        evaluator_version="v0.1.0",
        evidence_json={"summary": "Good overall structure"},
        criterion_scores=[
            CriterionScoreCreate(
                criterion="task_achievement",
                score=7.0,
                confidence=0.85,
                evidence_json={"positive": ["Clear position"], "limiting": ["Underdeveloped conclusion"]},
            ),
        ],
    )
    assert ac.estimated_band == 6.5
    assert len(ac.criterion_scores) == 1


def test_error_event_create() -> None:
    """ErrorEventCreate validates error taxonomy fields."""
    ee = ErrorEventCreate(
        attempt_id=uuid.uuid4(),
        category=ErrorCategory.GRAMMAR,
        subtype="article",
        evidence_text="'the' missing before 'environment'",
        severity=ErrorSeverity.MEDIUM,
        confidence=0.9,
    )
    assert ee.category == ErrorCategory.GRAMMAR
    assert ee.subtype == "article"


def test_review_submit() -> None:
    """ReviewSubmit validates FSRS rating."""
    rs = ReviewSubmit(
        learning_item_id=uuid.uuid4(),
        rating=ReviewRating.GOOD,
        review_type=ReviewType.RECOGNITION,
    )
    assert rs.rating == ReviewRating.GOOD
