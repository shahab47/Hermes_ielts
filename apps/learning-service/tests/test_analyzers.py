"""Unit tests for IELTS analyzers and evaluation protocols (Phase 5)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime

from app.analyzers import (
    BottleneckDetector,
    CriterionEvaluation,
    SpeakingAssessmentResult,
    VisualType,
    WritingVerifier,
)
from app.models.error import ErrorCategory, Weakness, WeaknessStatus
from app.models.learner import Skill, SkillState


def test_writing_verifier_task1_underlength_and_overview() -> None:
    """Test Task 1 preflight checks."""
    short_text = "The graph shows sales from 2010 to 2020. Sales increased sharply."
    res1 = WritingVerifier.verify_task1(short_text, visual_type=VisualType.LINE_GRAPH)

    assert not res1.is_word_count_sufficient
    assert res1.word_count < 150
    assert not res1.has_identifiable_overview
    assert len(res1.warnings) >= 2

    # With overview and proper length (> 150 words)
    proper_text = (
        "The line graph illustrates the consumption of fish and different kinds of meat in a European country between 1979 and 2004.\n\n"
        "Overall, it is clear that the consumption of beef, lamb and fish showed downward trends over the period, "
        "whereas the figure for chicken saw a dramatic increase throughout the entire timeframe.\n\n"
        "In 1979, beef was by far the most popular meat, with around 220 grams per person per week, followed by lamb at 150 grams. "
        "Over the next 25 years, beef consumption fluctuated and declined significantly to roughly 100 grams in 2004.\n\n"
        "In contrast, chicken consumption stood at nearly 150 grams in 1979 and rose steadily to reach a peak of approximately 250 grams in 2004, "
        "overtaking beef in 1989 as the most widely consumed meat.\n\n"
        "Finally, fish consumption remained the lowest throughout the given timeline, declining gently from just over 50 grams to approximately 45 grams per week."
    )
    res2 = WritingVerifier.verify_task1(proper_text, visual_type=VisualType.LINE_GRAPH)
    assert res2.is_word_count_sufficient
    assert res2.has_identifiable_overview
    assert res2.paragraph_count >= 3
    assert len(res2.warnings) == 0


def test_writing_verifier_task2_preflight() -> None:
    """Test Task 2 preflight checks and position marker detection."""
    essay_snippet = (
        "Some people believe that university education should be free for all students.\n\n"
        "In my opinion, higher education brings immense benefits to society as a whole. "
        "First and foremost, educated citizens contribute more tax revenue...\n\n"
        "Furthermore, free tuition promotes social mobility...\n\n"
        "In conclusion, I strongly agree that government funding for universities is a worthwhile investment."
    )
    res = WritingVerifier.verify_task2(essay_snippet)
    assert res.has_clear_position_markers
    assert res.paragraph_count == 4


def test_overall_writing_band_calculation_weighting() -> None:
    """Test 1/3 Task 1 and 2/3 Task 2 official weighting and band rounding."""
    # Task 1: 6.0, Task 2: 7.0 -> (6.0 + 14.0) / 3 = 20/3 = 6.666... -> rounds to 6.5
    res1 = WritingVerifier.calculate_overall_writing_band(6.0, 7.0)
    assert res1 == 6.5

    # Task 1: 7.0, Task 2: 7.0 -> 7.0
    res2 = WritingVerifier.calculate_overall_writing_band(7.0, 7.0)
    assert res2 == 7.0

    # Task 1: 6.5, Task 2: 7.5 -> (6.5 + 15.0) / 3 = 21.5/3 = 7.166... -> rounds to 7.0
    res3 = WritingVerifier.calculate_overall_writing_band(6.5, 7.5)
    assert res3 == 7.0

    # Task 1: 7.0, Task 2: 8.0 -> (7.0 + 16.0) / 3 = 23/3 = 7.666... -> rounds to 7.5
    res4 = WritingVerifier.calculate_overall_writing_band(7.0, 8.0)
    assert res4 == 7.5


def test_bottleneck_detector_selects_highest_impact_skill() -> None:
    """Test bottleneck detector prioritizes skill with largest gap and recurrence."""
    now = datetime.now(UTC)
    learner_id = uuid.uuid4()

    # Learner targets 7.5. Writing is 5.5, Speaking is 7.0
    writing_state = SkillState(
        id=uuid.uuid4(),
        learner_id=learner_id,
        skill=Skill.WRITING,
        estimated_band=5.5,
        confidence=0.85,
    )
    speaking_state = SkillState(
        id=uuid.uuid4(),
        learner_id=learner_id,
        skill=Skill.SPEAKING,
        estimated_band=7.0,
        confidence=0.80,
    )

    writing_weakness = Weakness(
        id=uuid.uuid4(),
        learner_id=learner_id,
        category=ErrorCategory.GRAMMAR,
        subtype="clause_structure",
        status=WeaknessStatus.CONFIRMED,
        priority=0.82,
        first_seen_at=now,
        last_seen_at=now,
    )

    bottleneck = BottleneckDetector.detect_primary_bottleneck(
        target_overall_band=7.5,
        skill_states=[writing_state, speaking_state],
        active_weaknesses=[writing_weakness],
    )

    assert bottleneck is not None
    assert bottleneck.selected_skill == Skill.WRITING
    assert bottleneck.urgency_score > 0.5


def test_speaking_transcript_only_pronunciation_policy() -> None:
    """Enforce non-negotiable rule: Pronunciation must be unassessed in transcript-only mode."""
    crit_fc = CriterionEvaluation(
        criterion_name="fluency_and_coherence",
        band_score=6.5,
        confidence=0.8,
        positive_evidence=["Spoke at length without noticeable effort"],
        limiting_evidence=["Occasional hesitation searching for words"],
        descriptor_justification="Matches public Band 6 descriptor",
    )
    crit_lr = CriterionEvaluation(
        criterion_name="lexical_resource",
        band_score=6.5,
        confidence=0.8,
        positive_evidence=["Wide vocabulary used with flexibility"],
        limiting_evidence=["Some inaccurate collocations"],
        descriptor_justification="Matches public Band 6 descriptor",
    )
    crit_gra = CriterionEvaluation(
        criterion_name="grammatical_range_and_accuracy",
        band_score=6.0,
        confidence=0.8,
        positive_evidence=["Mix of simple and complex sentence forms"],
        limiting_evidence=["Frequent errors in complex structures"],
        descriptor_justification="Matches public Band 6 descriptor",
    )

    res = SpeakingAssessmentResult(
        overall_band=6.5,
        overall_confidence=0.8,
        evaluator_model="claude-3-5-sonnet",
        evaluator_version="v1.0.0",
        fluency_and_coherence=crit_fc,
        lexical_resource=crit_lr,
        grammatical_range_and_accuracy=crit_gra,
        is_transcript_only=True,
    )

    assert res.pronunciation is None
    assert "transcript only" in res.pronunciation_status
