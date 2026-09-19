"""Unit tests for Four Skill Engines, Vocabulary, Grammar, and Mock Exam (Phases P18-P30)."""

from __future__ import annotations

import pytest

from app.domain.question_bank import (
    ListeningQuestionType,
    Question,
    QuestionAnswer,
    QuestionExplanation,
    QuestionProvenance,
    QuestionSet,
    ReadingQuestionType,
    SpeakingPartType,
)
from app.models.learner import Skill
from app.models.task import TaskSource
from app.services.grammar_service import GrammarDimension, GrammarPoint, GrammarService
from app.services.listening_service import ListeningService, ListeningSubmission
from app.services.mock_exam_service import MockExamMode, MockExamService
from app.services.reading_service import ReadingService, ReadingSubmission
from app.services.speaking_service import SpeakingEvaluationInput, SpeakingService
from app.services.speech_metrics import TimestampSegment
from app.services.vocabulary_service import VocabularyDimension, VocabularyItem, VocabularyService


@pytest.fixture
def sample_provenance() -> QuestionProvenance:
    return QuestionProvenance(
        source_id="test_suite",
        source_type=TaskSource.GENERATED,
        publisher="Test Suite",
        title="IELTS Test Exercises",
        license_name="CC-BY-4.0",
        rights_status="authorized",
        redistribution_allowed=True,
    )


# --- Phase P18: Listening Engine Tests ---


def test_listening_answer_normalization() -> None:
    assert ListeningService.normalize_answer("  The library  ") == "library"
    assert ListeningService.normalize_answer("a book.") == "book"
    assert ListeningService.normalize_answer("an apple!") == "apple"
    assert ListeningService.normalize_answer("14th September,") == "14th september"


def test_listening_band_calculation() -> None:
    assert ListeningService.calculate_band(39, 40) == 9.0
    assert ListeningService.calculate_band(30, 40) == 7.0
    assert ListeningService.calculate_band(23, 40) == 6.0
    assert ListeningService.calculate_band(16, 40) == 5.0


def test_listening_session_evaluation(sample_provenance: QuestionProvenance) -> None:
    q1 = Question(
        skill=Skill.LISTENING,
        task_type="section_1",
        question_type=ListeningQuestionType.FORM_COMPLETION.value,
        prompt="Address: 42 [1] ________ Street",
        answer=QuestionAnswer(accepted_values=["Highland"]),
        explanation=QuestionExplanation(text="Speaker clearly says 42 Highland Street."),
        provenance=sample_provenance,
    )
    qset = QuestionSet(
        title="Listening Sec 1",
        skill=Skill.LISTENING,
        task_type="section_1",
        questions=[q1],
        passage_or_transcript="Full secret transcript.",
        provenance=sample_provenance,
    )

    subs = [ListeningSubmission(question_id=q1.id, user_answer="highland")]
    res = ListeningService.evaluate_session(qset, subs, reveal_transcript=True)

    assert res.total_questions == 1
    assert res.correct_count == 1
    assert res.revealed_transcript == "Full secret transcript."
    assert res.results[0].is_correct is True


# --- Phase P19: Reading Engine Tests ---


def test_reading_normalization() -> None:
    assert ReadingService.normalize_answer("T", ReadingQuestionType.TFNG) == "true"
    assert ReadingService.normalize_answer("False", ReadingQuestionType.TFNG) == "false"
    assert ReadingService.normalize_answer("NG", ReadingQuestionType.TFNG) == "not given"
    assert ReadingService.normalize_answer("Y", ReadingQuestionType.YNNG) == "yes"
    assert ReadingService.normalize_answer("No", ReadingQuestionType.YNNG) == "no"


def test_reading_speed_wpm() -> None:
    passage = "word " * 600  # 600 words
    # 600 words in 180 seconds (3 mins) -> 200 WPM
    wpm = ReadingService.calculate_reading_speed(passage, 180.0)
    assert wpm == 200.0


def test_reading_session_adaptive_weakness(sample_provenance: QuestionProvenance) -> None:
    q1 = Question(
        skill=Skill.READING,
        task_type="academic_reading",
        question_type=ReadingQuestionType.TFNG.value,
        prompt="Climate changes occurred rapidly.",
        answer=QuestionAnswer(accepted_values=["TRUE"]),
        explanation=QuestionExplanation(text="Paragraph 1 confirms rapid shifts."),
        provenance=sample_provenance,
    )
    qset = QuestionSet(
        title="Reading Passage 1",
        skill=Skill.READING,
        task_type="academic_reading",
        questions=[q1],
        passage_or_transcript="The climate changes occurred rapidly across the northern hemisphere.",
        provenance=sample_provenance,
    )
    # Learner submits wrong answer
    subs = [ReadingSubmission(question_id=q1.id, user_answer="FALSE")]
    res = ReadingService.evaluate_session(qset, subs, elapsed_seconds=60.0)

    assert res.correct_count == 0
    assert res.weakest_question_type == "tfng"
    assert res.recommended_drill is not None
    assert "tfng" in res.recommended_drill


# --- Phase P21 & P22: Speaking & Acoustic Pronunciation Tests ---


def test_speaking_cue_card_generation() -> None:
    card = SpeakingService.generate_cue_card(
        topic="A Historic Monument",
        prompt="Describe a historic building you visited.",
        cue_points=["Where it is", "When you went", "Why it is historic"],
    )
    assert card.part_type == SpeakingPartType.PART_2
    assert card.prep_timer_seconds == 60
    assert len(card.cue_points) == 3


def test_speaking_strict_transcript_only_pronunciation_policy() -> None:
    # Rule: Never score pronunciation from transcript alone
    eval_input = SpeakingEvaluationInput(
        part_type=SpeakingPartType.PART_2,
        prompt_text="Describe a journey.",
        transcript="I took a long journey across the mountains last year.",
        is_transcript_only=True,
    )
    result = SpeakingService.evaluate_response(eval_input)
    assert result.is_transcript_only is True
    assert result.pronunciation is None
    assert "unassessed" in result.pronunciation_status.lower()


def test_speaking_with_acoustic_metrics() -> None:
    segments = [
        TimestampSegment(text="I", start=0.0, end=0.2),
        TimestampSegment(text="took", start=0.2, end=0.5),
        TimestampSegment(text="a", start=0.5, end=0.6),
        TimestampSegment(text="train", start=0.6, end=1.0),
    ]
    eval_input = SpeakingEvaluationInput(
        part_type=SpeakingPartType.PART_1,
        prompt_text="Do you prefer trains or buses?",
        transcript="I took a train.",
        segments=segments,
        audio_duration_seconds=1.2,
        is_transcript_only=False,
        pronunciation_score=7.0,
    )
    result = SpeakingService.evaluate_response(eval_input)
    assert result.pronunciation is not None
    assert result.pronunciation.band_score == 7.0
    assert result.overall_band >= 6.0


# --- Phase P23: Vocabulary Engine Tests ---


def test_vocabulary_multi_dimension_tracking() -> None:
    item = VocabularyItem(
        term="ubiquitous",
        definition="Present, appearing, or found everywhere.",
        collocations=["ubiquitous computing", "ubiquitous influence"],
    )
    assert VocabularyService.calculate_overall_mastery(item) == 0.0

    # Test spelling check
    ok, _ = VocabularyService.check_spelling(item, "ubiquitous")
    assert ok is True
    assert item.dimension_scores[VocabularyDimension.SPELLING] > 0.0

    # Test collocation check
    ok_col, _ = VocabularyService.check_collocation(item, "ubiquitous influence")
    assert ok_col is True
    assert item.dimension_scores[VocabularyDimension.COLLOCATION] > 0.0

    assert VocabularyService.calculate_overall_mastery(item) > 0.0


# --- Phase P25: Grammar Engine Tests ---


def test_grammar_mastery_requires_transfer() -> None:
    point = GrammarPoint(
        structure_name="Inversion with negative adverbials",
        category="inversion",
        rule_explanation="Seldom / Rarely + auxiliary + subject",
    )
    # Only recognition mastered
    point.dimension_scores[GrammarDimension.RECOGNITION] = 1.0
    assert not GrammarService.is_spontaneously_controlled(point)

    # Master transfer and free production
    point.dimension_scores[GrammarDimension.CONTROLLED_PRODUCTION] = 0.80
    point.dimension_scores[GrammarDimension.FREE_PRODUCTION] = 0.85
    point.dimension_scores[GrammarDimension.IELTS_TRANSFER] = 0.80
    assert GrammarService.is_spontaneously_controlled(point)
    assert GrammarService.calculate_operational_mastery(point) >= 0.70


# --- Phase P30: Mock Exam Engine Tests ---


def test_official_ielts_rounding_rules() -> None:
    calc = MockExamService.calculate_official_overall_band

    # Average 6.25 -> 6.5
    assert calc(6.5, 6.5, 6.0, 6.0) == 6.5

    # Average 6.75 -> 7.0
    assert calc(7.0, 7.0, 6.5, 6.5) == 7.0

    # Average 6.125 -> 6.0
    assert calc(6.5, 6.0, 6.0, 6.0) == 6.0

    # Average 6.375 -> 6.5
    assert calc(6.5, 6.5, 6.5, 6.0) == 6.5

    # Average 6.875 -> 7.0
    assert calc(7.0, 7.0, 7.0, 6.5) == 7.0


def test_full_mock_exam_lifecycle() -> None:
    exam = MockExamService.start_exam(mode=MockExamMode.FULL_MOCK)
    assert exam.feedback_isolated is True
    assert exam.is_completed is False

    MockExamService.record_section(exam, "listening", band_score=7.5, time_spent_seconds=1800.0)
    MockExamService.record_section(exam, "reading", band_score=7.0, time_spent_seconds=3600.0)
    MockExamService.record_section(exam, "writing", band_score=6.5, time_spent_seconds=3600.0)
    MockExamService.record_section(exam, "speaking", band_score=7.0, time_spent_seconds=720.0)

    final = MockExamService.finalize_exam(exam)
    assert final.is_completed is True
    assert final.feedback_isolated is False
    # Mean of 7.5, 7.0, 6.5, 7.0 is 28/4 = 7.0
    assert final.overall_band == 7.0
