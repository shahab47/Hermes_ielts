"""Unit tests for the Adaptive Learning Planner (Phase 11)."""

from __future__ import annotations

import uuid

from app.analyzers import PrimaryBottleneck
from app.models.learner import Skill
from app.models.learning_item import ItemType, LearningItem, MasteryState
from app.planner import AdaptivePlanner


def test_adaptive_planner_allocates_balanced_daily_mix() -> None:
    """Planner includes bottleneck drill, spaced review, and integrated practice."""
    learner_id = uuid.uuid4()

    mock_bottleneck = PrimaryBottleneck(
        selected_skill=Skill.WRITING,
        selected_criterion="task_achievement_or_response",
        urgency_score=0.88,
        rationale="Writing Task 2 band (5.5) has a 2.0 gap to target (7.5)",
        actionable_remediation="Structure body paragraphs with clear topic sentences.",
        contributing_weaknesses=["grammar: clause_structure"],
    )

    mock_due_item = LearningItem(
        id=uuid.uuid4(),
        learner_id=learner_id,
        item_type=ItemType.VOCABULARY,
        canonical_form="substantial",
        mastery_state=MasteryState.LEARNING,
    )

    plan = AdaptivePlanner.generate_daily_plan(
        target_overall_band=7.5,
        bottleneck=mock_bottleneck,
        due_items=[mock_due_item],
        active_weaknesses=[],
        available_minutes=50,
    )

    assert plan.due_review_count == 1
    assert len(plan.activities) == 3

    types = [a.activity_type for a in plan.activities]
    assert "spaced_review" in types
    assert "bottleneck_drill" in types
    assert "integrated_practice" in types

    total_mins = plan.total_estimated_minutes
    assert 40 <= total_mins <= 60
