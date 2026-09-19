"""Deterministic Adaptive Learning Planner for IELTS preparation (Phase 11)."""

from __future__ import annotations

from collections.abc import Sequence
from datetime import UTC, datetime

from pydantic import BaseModel, Field

from app.analyzers import PrimaryBottleneck
from app.models.error import Weakness
from app.models.learner import Skill
from app.models.learning_item import LearningItem


class PlannedActivity(BaseModel):
    """An individual activity within a daily or weekly plan."""

    activity_type: str = Field(description="'bottleneck_drill', 'spaced_review', or 'integrated_practice'")
    skill: Skill
    title: str
    description: str
    target_weakness: str | None = None
    estimated_minutes: int
    content_reference_id: str | None = None


class DailyStudyPlan(BaseModel):
    """Adaptive daily plan tailored to the learner's current bottlenecks and reviews."""

    plan_date: str
    primary_objective: str
    rationale: str
    total_estimated_minutes: int
    activities: list[PlannedActivity] = []
    due_review_count: int
    assessment_checkpoint: str | None = None


class AdaptivePlanner:
    """Generates deterministic study plans balancing bottleneck remediation, spaced review, and full task transfer."""

    DEFAULT_DAILY_MINUTES = 45

    @classmethod
    def generate_daily_plan(
        cls,
        target_overall_band: float,
        bottleneck: PrimaryBottleneck | None,
        due_items: Sequence[LearningItem],
        active_weaknesses: Sequence[Weakness],
        available_minutes: int = DEFAULT_DAILY_MINUTES,
        exam_date: datetime | None = None,
    ) -> DailyStudyPlan:
        """Create a balanced daily plan: ~40% bottleneck, ~30% spaced review, ~30% integrated practice."""
        today_str = datetime.now(UTC).strftime("%Y-%m-%d")
        activities: list[PlannedActivity] = []

        # 1. Spaced Review (FSRS due items)
        due_count = len(due_items)
        if due_count > 0:
            review_mins = min(max(int(available_minutes * 0.30), 10), 20)
            activities.append(
                PlannedActivity(
                    activity_type="spaced_review",
                    skill=Skill.VOCABULARY,
                    title="Spaced Repetition Review (FSRS)",
                    description=f"Complete active recall review for {min(due_count, 15)} vocabulary & grammar cards.",
                    estimated_minutes=review_mins,
                )
            )

        # 2. Targeted Bottleneck Work (highest priority)
        if bottleneck is not None:
            bottleneck_mins = max(int(available_minutes * 0.40), 15)
            activities.append(
                PlannedActivity(
                    activity_type="bottleneck_drill",
                    skill=bottleneck.selected_skill,
                    title=f"Targeted Remediative Drill ({bottleneck.selected_skill.value.capitalize()})",
                    description=f"Address primary bottleneck: {bottleneck.rationale}. {bottleneck.actionable_remediation}",
                    target_weakness=bottleneck.selected_criterion,
                    estimated_minutes=bottleneck_mins,
                )
            )
            primary_obj = f"Remediate primary bottleneck in {bottleneck.selected_skill.value.capitalize()} ({bottleneck.selected_criterion})"
            rationale = bottleneck.rationale
        else:
            primary_obj = "Balanced skill maintenance and diagnostic practice"
            rationale = "No single critical bottleneck detected. Focusing on holistic skill transfer."
            activities.append(
                PlannedActivity(
                    activity_type="diagnostic_evaluation",
                    skill=Skill.WRITING,
                    title="Diagnostic Baseline Task",
                    description="Complete a short baseline writing or speaking prompt to diagnose current strengths and weaknesses.",
                    estimated_minutes=max(int(available_minutes * 0.50), 20),
                )
            )

        # 3. Integrated Practice (Skill transfer)
        remaining_mins = max(available_minutes - sum(a.estimated_minutes for a in activities), 15)
        activities.append(
            PlannedActivity(
                activity_type="integrated_practice",
                skill=Skill.WRITING if (bottleneck and bottleneck.selected_skill != Skill.WRITING) else Skill.SPEAKING,
                title="Timed Integrated Task Practice",
                description="Complete one timed task under test-like conditions to build transfer and endurance.",
                estimated_minutes=remaining_mins,
            )
        )

        checkpoint = "Check for error recurrence in the targeted skill area."

        return DailyStudyPlan(
            plan_date=today_str,
            primary_objective=primary_obj,
            rationale=rationale,
            total_estimated_minutes=sum(a.estimated_minutes for a in activities),
            activities=activities,
            due_review_count=due_count,
            assessment_checkpoint=checkpoint,
        )
