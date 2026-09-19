"""Tests for SQLAlchemy models."""
from __future__ import annotations

from app.models import (
    Learner, SkillState, Attempt, Assessment, CriterionScore,
    ErrorEvent, Weakness, LearningItem, ReviewEvent,
    Task, PracticeSession, Recommendation, AudioAsset, LearnerEvent,
    Skill, Trend, BaselineStatus, AttemptSource,
    ErrorCategory, ErrorSeverity, WeaknessStatus,
    ItemType, MasteryState, ReviewRating, ReviewType,
    TaskDifficulty, TaskSource, CompletionStatus,
    RecommendationType, RecommendationStatus,
)
from app.models.base import Base


def test_all_models_importable() -> None:
    """All models can be imported without errors."""
    assert Learner.__tablename__ == "learners"
    assert SkillState.__tablename__ == "skill_states"
    assert Attempt.__tablename__ == "attempts"
    assert Assessment.__tablename__ == "assessments"
    assert CriterionScore.__tablename__ == "criterion_scores"
    assert ErrorEvent.__tablename__ == "error_events"
    assert Weakness.__tablename__ == "weaknesses"
    assert LearningItem.__tablename__ == "learning_items"
    assert ReviewEvent.__tablename__ == "review_events"
    assert Task.__tablename__ == "tasks"
    assert PracticeSession.__tablename__ == "practice_sessions"
    assert Recommendation.__tablename__ == "recommendations"
    assert AudioAsset.__tablename__ == "audio_assets"
    assert LearnerEvent.__tablename__ == "learner_events"


def test_base_metadata_has_tables() -> None:
    """All tables are registered in Base metadata."""
    table_names = set(Base.metadata.tables.keys())
    expected = {
        "learners", "skill_states", "attempts", "assessments",
        "criterion_scores", "error_events", "weaknesses",
        "learning_items", "review_events", "tasks",
        "practice_sessions", "recommendations", "audio_assets",
        "learner_events",
    }
    assert expected.issubset(table_names)


def test_skill_enum_values() -> None:
    """Skill enum has all required values."""
    skills = {s.value for s in Skill}
    assert skills == {"listening", "reading", "writing", "speaking", "vocabulary", "grammar", "pronunciation"}


def test_error_category_enum() -> None:
    """Error category enum covers all taxonomy categories."""
    categories = {c.value for c in ErrorCategory}
    assert categories == {"grammar", "lexical", "coherence_cohesion", "task", "speaking", "pronunciation"}


def test_review_rating_values() -> None:
    """FSRS review ratings match expected values."""
    assert ReviewRating.AGAIN.value == 1
    assert ReviewRating.HARD.value == 2
    assert ReviewRating.GOOD.value == 3
    assert ReviewRating.EASY.value == 4
