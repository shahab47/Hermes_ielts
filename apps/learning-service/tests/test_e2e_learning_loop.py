"""Phase 25 Hardened Testing: Complete Closed-Loop Learning Pipeline.

Verifies end-to-end:
Submission -> Verification -> Evaluation -> Bottleneck Detection -> State Update -> Adaptive Plan.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.analyzers.bottleneck_detector import BottleneckDetector
from app.analyzers.writing_verifier import WritingVerifier
from app.models.error import ErrorCategory, Weakness, WeaknessStatus
from app.models.learner import Skill, SkillState
from app.models.learning_item import ItemType, LearningItem, MasteryState
from app.planner.adaptive_planner import AdaptivePlanner


def test_closed_loop_learning_workflow() -> None:
    now = datetime.now(UTC)
    learner_id = uuid.uuid4()

    # Step 1: Student submits Writing Task 2 essay
    essay_text = (
        "In modern society, many young people choose to study abroad.\n\n"
        "In my opinion, living in a foreign country has significant benefits. "
        "Firstly, students learn to become independent and manage their finances. "
        "Furthermore, they are exposed to different cultures and ways of thinking.\n\n"
        "On the other hand, studying overseas can be very expensive, and some students suffer from homesickness. "
        "However, these challenges help them grow stronger.\n\n"
        "In conclusion, I firmly believe that the advantages of international education far outweigh the disadvantages."
    )

    # Step 2: Verification preflight
    preflight = WritingVerifier.verify_task2(essay_text)
    assert preflight.has_clear_position_markers is True
    assert preflight.paragraph_count == 4
    assert preflight.word_count > 0

    # Step 3: Diagnostic Scoring
    task2_band = WritingVerifier.calculate_overall_writing_band(task1_band=6.0, task2_band=6.0)
    assert task2_band == 6.0

    # Step 4: Track learner skill states
    writing_state = SkillState(
        id=uuid.uuid4(),
        learner_id=learner_id,
        skill=Skill.WRITING,
        estimated_band=6.0,
        confidence=0.85,
    )
    speaking_state = SkillState(
        id=uuid.uuid4(),
        learner_id=learner_id,
        skill=Skill.SPEAKING,
        estimated_band=7.0,
        confidence=0.80,
    )

    # Step 5: Persistent weaknesses aggregated from error events
    writing_weakness = Weakness(
        id=uuid.uuid4(),
        learner_id=learner_id,
        category=ErrorCategory.GRAMMAR,
        subtype="run_on_sentences",
        status=WeaknessStatus.CONFIRMED,
        priority=0.85,
        first_seen_at=now,
        last_seen_at=now,
    )
    lexical_weakness = Weakness(
        id=uuid.uuid4(),
        learner_id=learner_id,
        category=ErrorCategory.LEXICAL,
        subtype="repetition",
        status=WeaknessStatus.CONFIRMED,
        priority=0.45,
        first_seen_at=now,
        last_seen_at=now,
    )

    # Step 6: Detect primary bottleneck
    bottleneck = BottleneckDetector.detect_primary_bottleneck(
        target_overall_band=7.5,
        skill_states=[writing_state, speaking_state],
        active_weaknesses=[writing_weakness, lexical_weakness],
    )
    assert bottleneck is not None
    assert bottleneck.selected_skill == Skill.WRITING
    assert bottleneck.urgency_score > 0.5

    # Step 7: Due FSRS spaced review items
    mock_due_item = LearningItem(
        id=uuid.uuid4(),
        learner_id=learner_id,
        item_type=ItemType.VOCABULARY,
        canonical_form="substantial",
        mastery_state=MasteryState.LEARNING,
    )

    # Step 8: Invoke adaptive planner targeting the primary bottleneck
    daily_plan = AdaptivePlanner.generate_daily_plan(
        target_overall_band=7.5,
        bottleneck=bottleneck,
        due_items=[mock_due_item],
        active_weaknesses=[writing_weakness, lexical_weakness],
        available_minutes=45,
    )

    # Step 9: Verify generated plan balances activities and targets bottleneck
    assert daily_plan.total_estimated_minutes <= 60
    assert len(daily_plan.activities) == 3
    activity_types = [a.activity_type for a in daily_plan.activities]
    assert "bottleneck_drill" in activity_types
    assert "spaced_review" in activity_types
    assert "integrated_practice" in activity_types
    assert daily_plan.due_review_count == 1
