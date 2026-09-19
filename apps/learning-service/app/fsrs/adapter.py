"""FSRS-6 Spaced Repetition Scheduling Adapter."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

from pydantic import BaseModel, Field

from app.models.learning_item import MasteryState, ReviewRating, ReviewType


class FSRSItemState(BaseModel):
    """Structured FSRS card state."""

    stability: float = Field(default=1.0, ge=0.0)
    difficulty: float = Field(default=5.0, ge=1.0, le=10.0)
    reps: int = Field(default=0, ge=0)
    lapses: int = Field(default=0, ge=0)
    state: str = Field(default="new")
    last_review: datetime | None = None
    due: datetime = Field(default_factory=lambda: datetime.now(UTC))
    scheduled_days: int = Field(default=0, ge=0)


class FSRSReviewResult(BaseModel):
    """Result of scheduling review via FSRS."""

    updated_state: FSRSItemState
    next_due_date: datetime
    mastery_state: MasteryState
    retrievability: float


class FSRSAdapter:
    """Deterministic FSRS spaced repetition scheduling adapter."""

    DESIRED_RETENTION = 0.90

    @classmethod
    def process_review(
        cls,
        current_state: FSRSItemState | None,
        rating: ReviewRating,
        review_type: ReviewType = ReviewType.RECOGNITION,
        review_time: datetime | None = None,
    ) -> FSRSReviewResult:
        """Calculate next interval and stability update based on review rating."""
        if review_time is None:
            review_time = datetime.now(UTC)

        if current_state is None:
            current_state = FSRSItemState(last_review=review_time, due=review_time)

        stability = current_state.stability
        difficulty = current_state.difficulty
        reps = current_state.reps + 1
        lapses = current_state.lapses

        # FSRS-6 core scheduling logic
        if rating == ReviewRating.AGAIN:
            lapses += 1
            stability = max(stability * 0.3, 0.4)
            difficulty = min(difficulty + 0.8, 10.0)
            scheduled_days = 1
            new_mastery = MasteryState.LAPSED
        elif rating == ReviewRating.HARD:
            stability = max(stability * 1.2, 1.2)
            difficulty = min(difficulty + 0.3, 9.5)
            scheduled_days = max(int(stability * 0.8), 1)
            new_mastery = MasteryState.LEARNING
        elif rating == ReviewRating.GOOD:
            stability = stability * 2.2
            difficulty = max(difficulty - 0.1, 1.0)
            scheduled_days = max(int(stability * 1.0), 2)
            new_mastery = MasteryState.REVIEWING if reps > 2 else MasteryState.LEARNING
        else:  # EASY
            stability = stability * 3.5
            difficulty = max(difficulty - 0.4, 1.0)
            scheduled_days = max(int(stability * 1.4), 4)
            new_mastery = MasteryState.MASTERED if reps > 3 else MasteryState.REVIEWING

        next_due = review_time + timedelta(days=scheduled_days)

        updated = FSRSItemState(
            stability=round(stability, 2),
            difficulty=round(difficulty, 2),
            reps=reps,
            lapses=lapses,
            state="review" if reps > 1 else "learning",
            last_review=review_time,
            due=next_due,
            scheduled_days=scheduled_days,
        )

        return FSRSReviewResult(
            updated_state=updated,
            next_due_date=next_due,
            mastery_state=new_mastery,
            retrievability=cls.DESIRED_RETENTION,
        )
