"""Official IELTS public band descriptors and rubric data models."""

from __future__ import annotations

import enum

from pydantic import BaseModel, Field


class WritingTaskType(str, enum.Enum):
    """IELTS Academic writing task types."""

    TASK_1 = "task_1"
    TASK_2 = "task_2"


class VisualType(str, enum.Enum):
    """Academic Task 1 visual stimulus types."""

    LINE_GRAPH = "line_graph"
    BAR_CHART = "bar_chart"
    PIE_CHART = "pie_chart"
    TABLE = "table"
    MAP = "map"
    PROCESS_DIAGRAM = "process_diagram"
    MULTIPLE_GRAPHS = "multiple_graphs"


class EssayType(str, enum.Enum):
    """Academic Task 2 essay prompt types."""

    OPINION = "agree_disagree"
    DISCUSSION = "discuss_both_views"
    ADVANTAGES_DISADVANTAGES = "advantages_disadvantages"
    PROBLEM_SOLUTION = "causes_solutions"
    TWO_PART_QUESTION = "direct_questions"


class WritingCriterion(str, enum.Enum):
    """Official IELTS Writing criteria."""

    TASK_ACHIEVEMENT_RESPONSE = "task_achievement_or_response"
    COHERENCE_COHESION = "coherence_and_cohesion"
    LEXICAL_RESOURCE = "lexical_resource"
    GRAMMATICAL_RANGE_ACCURACY = "grammatical_range_and_accuracy"


class SpeakingCriterion(str, enum.Enum):
    """Official IELTS Speaking criteria."""

    FLUENCY_COHERENCE = "fluency_and_coherence"
    LEXICAL_RESOURCE = "lexical_resource"
    GRAMMATICAL_RANGE_ACCURACY = "grammatical_range_and_accuracy"
    PRONUNCIATION = "pronunciation"


class DescriptorLevel(BaseModel):
    """Official public descriptor statement for a specific band and criterion."""

    band: float = Field(ge=0.0, le=9.0)
    key_features: list[str]
    positive_indicators: list[str]
    limiting_indicators: list[str]


# Public descriptor summaries for reference and calibration
WRITING_BAND_DESCRIPTORS_SUMMARY: dict[float, dict[WritingCriterion, str]] = {
    9.0: {
        WritingCriterion.TASK_ACHIEVEMENT_RESPONSE: "Fully addresses all parts of the task with a fully developed position.",
        WritingCriterion.COHERENCE_COHESION: "Uses cohesion in such a way that it attracts no attention. Skillfully manages paragraphing.",
        WritingCriterion.LEXICAL_RESOURCE: "Uses a wide range of vocabulary with very natural and sophisticated control of lexical features.",
        WritingCriterion.GRAMMATICAL_RANGE_ACCURACY: "Uses a wide range of structures with full flexibility and accuracy; rare minor errors occur only as 'slips'.",
    },
    7.0: {
        WritingCriterion.TASK_ACHIEVEMENT_RESPONSE: "Covers the requirements of the task. Presents a clear position throughout. Main ideas extended and supported.",
        WritingCriterion.COHERENCE_COHESION: "Logically organises information and ideas; clear progression throughout. Uses a range of cohesive devices appropriately.",
        WritingCriterion.LEXICAL_RESOURCE: "Uses a sufficient range of vocabulary to allow some flexibility and precision. Uses less common lexical items with some awareness of style and collocation.",
        WritingCriterion.GRAMMATICAL_RANGE_ACCURACY: "Uses a variety of complex structures. Produces frequent error-free sentences. Has good control of grammar and punctuation.",
    },
    6.0: {
        WritingCriterion.TASK_ACHIEVEMENT_RESPONSE: "Addresses all parts of the task although some parts may be more fully covered than others. Presents a relevant position.",
        WritingCriterion.COHERENCE_COHESION: "Arranges information and ideas coherently with a clear overall progression. Uses cohesive devices effectively, but cohesion may be faulty or mechanical.",
        WritingCriterion.LEXICAL_RESOURCE: "Uses an adequate range of vocabulary for the task. Attempts to use less common vocabulary but with some inaccuracy.",
        WritingCriterion.GRAMMATICAL_RANGE_ACCURACY: "Uses a mix of simple and complex sentence forms. Makes some errors in grammar and punctuation but they rarely reduce communication.",
    },
    5.0: {
        WritingCriterion.TASK_ACHIEVEMENT_RESPONSE: "Addresses the task only partially; the format may be in parts inappropriate. Expresses a position but the development is not always clear.",
        WritingCriterion.COHERENCE_COHESION: "Presents information with some organisation but there may be a lack of overall progression. Makes inadequate, inaccurate or over use of cohesive devices.",
        WritingCriterion.LEXICAL_RESOURCE: "Uses a limited range of vocabulary, but this is minimally adequate for the task. May make noticeable errors in spelling and/or word formation.",
        WritingCriterion.GRAMMATICAL_RANGE_ACCURACY: "Uses only a limited range of structures. Attempts complex sentences but these tend to be less accurate than simple sentences.",
    },
}
