"""Unit and validation tests for Question Bank, Delivery, and Generator (Phases P14, P15, P16, P17)."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.domain.question_bank import (
    CEFRLevel,
    DeliveryModality,
    ListeningQuestionType,
    Question,
    QuestionAnswer,
    QuestionExplanation,
    QuestionMedia,
    QuestionOption,
    QuestionProvenance,
    QuestionReviewStatus,
    QuestionSet,
    ReadingQuestionType,
    SpeakingPartType,
    WritingTaskType,
)
from app.models.learner import Skill
from app.models.task import TaskDifficulty, TaskSource
from app.repositories.question_repo import QuestionRepository
from app.services.question_delivery import QuestionDeliveryService
from app.services.question_generator import QuestionGeneratorService


@pytest.fixture
def sample_provenance() -> QuestionProvenance:
    return QuestionProvenance(
        source_id="test_source_01",
        source_type=TaskSource.GENERATED,
        publisher="IELTS Tutor Engine",
        title="Listening Practice Test 1",
        license_name="CC-BY-4.0",
        rights_status="authorized",
        redistribution_allowed=True,
        is_generated=True,
        generation_model="hermes-auto",
        prompt_version="1.0.0",
    )


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    session.get = AsyncMock()
    session.execute = AsyncMock()
    return session


# --- Phase P14 & P15: Question Types & Domain Model ---


def test_question_domain_model_creation(sample_provenance: QuestionProvenance) -> None:
    q = Question(
        skill=Skill.READING,
        task_type="academic_reading",
        question_type=ReadingQuestionType.TFNG.value,
        difficulty=TaskDifficulty.INTERMEDIATE,
        cefr=CEFRLevel.B2,
        prompt="The discovery was made in the late nineteenth century.",
        answer=QuestionAnswer(accepted_values=["TRUE"]),
        explanation=QuestionExplanation(
            text="Paragraph 2 states the excavation began in 1888.",
            target_evidence="in 1888, the team unearthed...",
        ),
        provenance=sample_provenance,
    )
    assert q.skill == Skill.READING
    assert q.question_type == "tfng"
    assert q.review_status == QuestionReviewStatus.VALIDATED
    assert q.cefr == CEFRLevel.B2


def test_question_set_with_multiple_types(sample_provenance: QuestionProvenance) -> None:
    q1 = Question(
        skill=Skill.LISTENING,
        task_type="section_1",
        question_type=ListeningQuestionType.FORM_COMPLETION.value,
        prompt="Customer surname: [1] ________",
        answer=QuestionAnswer(accepted_values=["Thompson"]),
        explanation=QuestionExplanation(text="The speaker spells T-H-O-M-P-S-O-N."),
        provenance=sample_provenance,
    )
    q2 = Question(
        skill=Skill.LISTENING,
        task_type="section_1",
        question_type=ListeningQuestionType.MCQ_SINGLE.value,
        prompt="The preferred delivery time is:",
        options=[
            QuestionOption(key="A", text="Morning"),
            QuestionOption(key="B", text="Afternoon", is_correct=True),
        ],
        answer=QuestionAnswer(accepted_values=["B"]),
        explanation=QuestionExplanation(text="He requests between 2 PM and 5 PM."),
        provenance=sample_provenance,
    )

    qset = QuestionSet(
        title="Listening Section 1: Customer Order",
        skill=Skill.LISTENING,
        task_type="section_1",
        time_limit_minutes=10,
        questions=[q1, q2],
        provenance=sample_provenance,
    )
    assert len(qset.questions) == 2
    assert qset.questions[0].question_type == "form_completion"
    assert qset.questions[1].question_type == "mcq_single"


# --- Phase P16: Source-Aware Question Delivery ---


def test_delivery_for_speaking_part_2(sample_provenance: QuestionProvenance) -> None:
    q = Question(
        skill=Skill.SPEAKING,
        task_type="part_2",
        question_type=SpeakingPartType.PART_2.value,
        prompt="Describe a memorable journey you took.",
        answer=QuestionAnswer(accepted_values=[]),
        explanation=QuestionExplanation(text="Fluency and coherence are evaluated over 2 minutes."),
        provenance=sample_provenance,
    )
    payload = QuestionDeliveryService.format_for_delivery(q)
    assert payload.modality == DeliveryModality.VOICE_PROMPT
    assert payload.requires_timer is True
    assert payload.timer_seconds == 60  # 1 min prep

    rendered = QuestionDeliveryService.render_telegram_message(payload)
    assert "*Preparation Time:* 60 seconds" in rendered["text"]
    assert "voice message" in rendered["text"].lower()


def test_delivery_for_reading_tfng(sample_provenance: QuestionProvenance) -> None:
    q = Question(
        skill=Skill.READING,
        task_type="academic_reading",
        question_type=ReadingQuestionType.TFNG.value,
        prompt="Solar energy is now cheaper than coal in all regions.",
        answer=QuestionAnswer(accepted_values=["FALSE"]),
        explanation=QuestionExplanation(text="Paragraph 3 mentions coal is still cheaper in certain remote basins."),
        provenance=sample_provenance,
    )
    payload = QuestionDeliveryService.format_for_delivery(q)
    assert payload.modality == DeliveryModality.OPTIONS
    assert len(payload.display_options) == 3
    assert payload.display_options[0]["key"] == "TRUE"

    rendered = QuestionDeliveryService.render_telegram_message(payload)
    assert rendered["reply_markup"] is not None
    assert len(rendered["reply_markup"]["inline_keyboard"]) == 3


def test_delivery_for_writing_task_2(sample_provenance: QuestionProvenance) -> None:
    q = Question(
        skill=Skill.WRITING,
        task_type="task_2",
        question_type=WritingTaskType.TASK_2.value,
        prompt="Some people believe university education should be free. Discuss both views.",
        answer=QuestionAnswer(accepted_values=[]),
        explanation=QuestionExplanation(text="Standard IELTS Task 2 argumentative rubric."),
        provenance=sample_provenance,
    )
    payload = QuestionDeliveryService.format_for_delivery(q)
    assert payload.modality == DeliveryModality.LONG_FORM
    assert payload.requires_long_form is True
    assert payload.timer_seconds == 2400  # 40 minutes


def test_delivery_for_listening_audio(sample_provenance: QuestionProvenance) -> None:
    q = Question(
        skill=Skill.LISTENING,
        task_type="section_2",
        question_type=ListeningQuestionType.MCQ_SINGLE.value,
        prompt="What is the main topic of the tour?",
        options=[
            QuestionOption(key="A", text="Architecture"),
            QuestionOption(key="B", text="Local Wildlife"),
        ],
        answer=QuestionAnswer(accepted_values=["A"]),
        explanation=QuestionExplanation(text="The speaker introduces the cathedral and old town hall."),
        media=[QuestionMedia(media_type="audio", uri="https://example.com/audio/sec2.mp3", duration_seconds=180.0)],
        provenance=sample_provenance,
    )
    payload = QuestionDeliveryService.format_for_delivery(q)
    assert payload.modality == DeliveryModality.AUDIO_WITH_PROMPTS
    assert payload.audio_uri == "https://example.com/audio/sec2.mp3"


# --- Phase P17: Anti-Hallucination & Quality Verification ---


def test_rejection_on_false_official_attribution(sample_provenance: QuestionProvenance) -> None:
    candidate = {
        "skill": "reading",
        "task_type": "academic_reading",
        "question_type": "mcq",
        "prompt": "What is the primary conclusion?",
        "options": [{"key": "A", "text": "Option A"}, {"key": "B", "text": "Option B"}],
        "answer": {"accepted_values": ["A"]},
        "explanation": {"text": "Detailed explanation of why Option A is correct."},
        "provenance": {
            "source_id": "fake_official",
            "source_type": "generated",
            "publisher": "Cambridge Official IELTS Exam Board",
            "title": "Stolen official test",
            "license_name": "Proprietary",
            "rights_status": "claimed",
            "redistribution_allowed": False,
            "is_generated": True,
        },
    }
    valid, errors, _ = QuestionGeneratorService.validate_and_build(candidate)
    assert not valid
    assert any("falsely claims official provenance" in err for err in errors)


def test_rejection_on_answer_leakage() -> None:
    candidate = {
        "skill": "reading",
        "task_type": "academic_reading",
        "question_type": "short_answer",
        "prompt": "The discovery was made in (1888) during the summer.",
        "answer": {"accepted_values": ["1888"]},
        "explanation": {"text": "The answer is clearly 1888 as stated in the text."},
        "provenance": {
            "source_id": "gen_01",
            "source_type": "generated",
            "publisher": "AI Generator",
            "title": "Passage Drill",
            "license_name": "CC-BY",
            "rights_status": "open",
            "redistribution_allowed": True,
            "is_generated": True,
        },
    }
    valid, errors, _ = QuestionGeneratorService.validate_and_build(candidate)
    assert not valid
    assert any("answer leakage" in err for err in errors)


def test_rejection_on_unanswerable_from_passage() -> None:
    passage = "The ancient aqueduct was built entirely from local limestone and timber."
    candidate = {
        "skill": "reading",
        "task_type": "academic_reading",
        "question_type": "short_answer",
        "prompt": "What metal was used in the aqueduct pipes?",
        "answer": {"accepted_values": ["copper"]},
        "explanation": {"text": "Copper was commonly used in Roman times."},
        "provenance": {
            "source_id": "gen_02",
            "source_type": "generated",
            "publisher": "AI Generator",
            "title": "Aqueduct drill",
            "license_name": "CC-BY",
            "rights_status": "open",
            "redistribution_allowed": True,
            "is_generated": True,
        },
    }
    valid, errors, _ = QuestionGeneratorService.validate_and_build(candidate, passage_context=passage)
    assert not valid
    assert any("grounded in or inferred from" in err for err in errors)


def test_rejection_on_duplicate_options() -> None:
    candidate = {
        "skill": "reading",
        "task_type": "academic_reading",
        "question_type": "mcq",
        "prompt": "What was the result of the experiment?",
        "options": [
            {"key": "A", "text": "Rapid cooling"},
            {"key": "B", "text": "rapid cooling"},
        ],
        "answer": {"accepted_values": ["A"]},
        "explanation": {"text": "Rapid cooling was observed immediately."},
        "provenance": {
            "source_id": "gen_03",
            "source_type": "generated",
            "publisher": "AI Generator",
            "title": "Experiment drill",
            "license_name": "CC-BY",
            "rights_status": "open",
            "redistribution_allowed": True,
            "is_generated": True,
        },
    }
    valid, errors, _ = QuestionGeneratorService.validate_and_build(candidate)
    assert not valid
    assert any("Duplicate option text" in err for err in errors)


def test_valid_generated_question_passes_quality_gate() -> None:
    passage = "The northern population of arctic foxes migrated eastward during the harsh winter of 1923."
    candidate = {
        "skill": "reading",
        "task_type": "academic_reading",
        "question_type": "sentence_completion",
        "prompt": "The foxes moved in an [1] ________ direction in 1923.",
        "answer": {"accepted_values": ["eastward"]},
        "explanation": {
            "text": "The passage confirms they migrated eastward during the 1923 winter.",
            "target_evidence": "migrated eastward during the harsh winter",
        },
        "tags": ["reading", "completion", "wildlife"],
        "provenance": {
            "source_id": "gen_04",
            "source_type": "generated",
            "publisher": "AI Learning Service",
            "title": "Arctic wildlife drill",
            "license_name": "CC-BY",
            "rights_status": "open",
            "redistribution_allowed": True,
            "is_generated": True,
        },
    }
    valid, errors, q = QuestionGeneratorService.validate_and_build(candidate, passage_context=passage)
    assert valid
    assert len(errors) == 0
    assert q is not None
    assert q.review_status == QuestionReviewStatus.VALIDATED
    assert q.quality_score >= 0.8


# --- Repository Tests ---


@pytest.mark.asyncio
async def test_question_repository_save(mock_session: AsyncMock, sample_provenance: QuestionProvenance) -> None:
    repo = QuestionRepository(mock_session)
    q = Question(
        skill=Skill.READING,
        task_type="academic_reading",
        question_type="tfng",
        prompt="Test prompt",
        answer=QuestionAnswer(accepted_values=["TRUE"]),
        explanation=QuestionExplanation(text="Test explanation for valid question"),
        provenance=sample_provenance,
    )
    model = await repo.save_question(q)
    assert model.id == q.id
    assert model.skill == Skill.READING
    mock_session.add.assert_called_once_with(model)
    mock_session.flush.assert_awaited_once()
