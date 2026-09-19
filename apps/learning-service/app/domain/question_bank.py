"""Domain schemas and entities for IELTS Question Bank (Phases P14, P15, P16)."""

from __future__ import annotations

import enum
import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from app.models.learner import Skill
from app.models.task import TaskDifficulty, TaskSource


class ListeningQuestionType(str, enum.Enum):
    """11 canonical IELTS Listening question types (P15)."""

    MCQ_SINGLE = "mcq_single"
    MCQ_MULTIPLE = "mcq_multiple"
    MATCHING = "matching"
    MAP_DIAGRAM_LABELLING = "map_diagram_labelling"
    FORM_COMPLETION = "form_completion"
    NOTE_COMPLETION = "note_completion"
    TABLE_COMPLETION = "table_completion"
    FLOW_CHART_COMPLETION = "flow_chart_completion"
    SUMMARY_COMPLETION = "summary_completion"
    SENTENCE_COMPLETION = "sentence_completion"
    SHORT_ANSWER = "short_answer"


class ReadingQuestionType(str, enum.Enum):
    """10 canonical IELTS Reading question types (P15)."""

    MCQ = "mcq"
    TFNG = "tfng"
    YNNG = "ynng"
    MATCHING_HEADINGS = "matching_headings"
    MATCHING_INFORMATION = "matching_information"
    MATCHING_FEATURES = "matching_features"
    SENTENCE_COMPLETION = "sentence_completion"
    SUMMARY_COMPLETION = "summary_completion"
    NOTE_TABLE_COMPLETION = "note_table_completion"
    SHORT_ANSWER = "short_answer"


class WritingTaskType(str, enum.Enum):
    """IELTS Writing tasks."""

    TASK_1 = "task_1"
    TASK_2 = "task_2"


class SpeakingPartType(str, enum.Enum):
    """IELTS Speaking parts."""

    PART_1 = "part_1"
    PART_2 = "part_2"
    PART_3 = "part_3"


class CEFRLevel(str, enum.Enum):
    """CEFR proficiency levels."""

    A2 = "A2"
    B1 = "B1"
    B2 = "B2"
    C1 = "C1"
    C2 = "C2"


class QuestionReviewStatus(str, enum.Enum):
    """Review and publishing status for questions (P17)."""

    DRAFT = "draft"
    VALIDATED = "validated"
    FLAGGED = "flagged"
    REJECTED = "rejected"


class DeliveryModality(str, enum.Enum):
    """Channel-independent delivery format (P16)."""

    TEXT = "text"
    OPTIONS = "options"
    MATCHING_PAIRS = "matching_pairs"
    AUDIO_WITH_PROMPTS = "audio_with_prompts"
    LONG_FORM = "long_form"
    VOICE_PROMPT = "voice_prompt"


class QuestionOption(BaseModel):
    """Choice or option item for MCQ and matching."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    key: str  # e.g., "A", "B", "i", "ii"
    text: str
    is_correct: bool = False


class QuestionAnswer(BaseModel):
    """Accepted answers for automatic or deterministic scoring."""

    model_config = ConfigDict(from_attributes=True)

    accepted_values: list[str] = Field(default_factory=list)
    case_sensitive: bool = False
    regex_pattern: str | None = None
    target_pair: dict[str, str] | None = None  # e.g. {"A": "Paragraph 2"}


class QuestionExplanation(BaseModel):
    """Pedagogical explanation and rubric rationale."""

    model_config = ConfigDict(from_attributes=True)

    text: str
    target_evidence: str | None = None
    common_pitfalls: list[str] = Field(default_factory=list)
    explanation_language: str = "en"


class QuestionMedia(BaseModel):
    """Associated audio, image, diagram, or reference passage chunk."""

    model_config = ConfigDict(from_attributes=True)

    media_type: str  # "audio", "image", "diagram", "passage"
    uri: str
    duration_seconds: float | None = None
    transcript: str | None = None
    timecodes: list[dict[str, Any]] = Field(default_factory=list)


class QuestionProvenance(BaseModel):
    """Full license, author, and retrieval metadata for content governance."""

    model_config = ConfigDict(from_attributes=True)

    source_id: str
    source_type: TaskSource
    publisher: str
    title: str
    license_name: str
    rights_status: str
    redistribution_allowed: bool
    version: str = "1.0.0"
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    is_generated: bool = False
    generation_model: str | None = None
    prompt_version: str | None = None


class Question(BaseModel):
    """Authoritative Question Entity satisfying P14/P15/P16 requirements."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    question_set_id: uuid.UUID | None = None
    skill: Skill
    task_type: str
    question_type: str
    difficulty: TaskDifficulty = TaskDifficulty.INTERMEDIATE
    cefr: CEFRLevel | None = None
    prompt: str
    instructions: str | None = None
    options: list[QuestionOption] = Field(default_factory=list)
    answer: QuestionAnswer
    explanation: QuestionExplanation
    media: list[QuestionMedia] = Field(default_factory=list)
    tags: list[str] = Field(default_factory=list)
    provenance: QuestionProvenance
    review_status: QuestionReviewStatus = QuestionReviewStatus.VALIDATED
    quality_score: float = 1.0
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class QuestionSet(BaseModel):
    """A collection of questions (e.g., Section 1 of Listening, Academic Reading Passage 1, Mock Exam)."""

    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    title: str
    skill: Skill
    task_type: str
    description: str | None = None
    time_limit_minutes: int | None = None
    passage_or_transcript: str | None = None
    questions: list[Question] = Field(default_factory=list)
    provenance: QuestionProvenance
    version: int = 1
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class DeliveryPayload(BaseModel):
    """Source-aware, channel-agnostic presentation payload for Telegram or API delivery (P16)."""

    model_config = ConfigDict(from_attributes=True)

    question_id: uuid.UUID
    modality: DeliveryModality
    prompt_text: str
    instructions: str | None = None
    display_options: list[dict[str, str]] = Field(default_factory=list)  # [{"key": "A", "label": "..."}]
    matching_pairs_definition: dict[str, list[str]] | None = None
    audio_uri: str | None = None
    image_uri: str | None = None
    requires_timer: bool = False
    timer_seconds: int | None = None
    requires_long_form: bool = False
    metadata: dict[str, Any] = Field(default_factory=dict)
