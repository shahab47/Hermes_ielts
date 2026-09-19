"""SQLAlchemy models for the IELTS Learning Service."""

from app.models.attempt import Assessment, Attempt, AttemptSource, CriterionScore
from app.models.audio import AudioAsset
from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.error import ErrorCategory, ErrorEvent, ErrorSeverity, Weakness, WeaknessStatus
from app.models.event import LearnerEvent
from app.models.learner import BaselineStatus, Learner, Skill, SkillState, Trend
from app.models.learning_item import (
    ItemType,
    LearningItem,
    MasteryState,
    ReviewEvent,
    ReviewRating,
    ReviewType,
)
from app.models.task import (
    CompletionStatus,
    PracticeSession,
    Recommendation,
    RecommendationStatus,
    RecommendationType,
    Task,
    TaskDifficulty,
    TaskSource,
)

__all__ = [
    "Assessment",
    "Attempt",
    "AttemptSource",
    "AudioAsset",
    "Base",
    "BaselineStatus",
    "CompletionStatus",
    "CriterionScore",
    "ErrorCategory",
    "ErrorEvent",
    "ErrorSeverity",
    "ItemType",
    "Learner",
    "LearnerEvent",
    "LearningItem",
    "MasteryState",
    "PracticeSession",
    "Recommendation",
    "RecommendationStatus",
    "RecommendationType",
    "ReviewEvent",
    "ReviewRating",
    "ReviewType",
    "Skill",
    "SkillState",
    "Task",
    "TaskDifficulty",
    "TaskSource",
    "TimestampMixin",
    "Trend",
    "UUIDPrimaryKeyMixin",
    "Weakness",
    "WeaknessStatus",
]
