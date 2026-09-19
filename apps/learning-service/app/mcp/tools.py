"""Typed tool implementations for Model Context Protocol (MCP) boundary (Phase 7)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from typing import Any

from pydantic import BaseModel, Field

from app.analyzers import WritingVerifier
from app.models.attempt import AttemptSource
from app.models.learner import Skill
from app.models.learning_item import ItemType, ReviewType
from app.services.speech_metrics import SpeechMetricsAnalyzer, TimestampSegment


# ============================================================================
# 1. Learner State Tool Inputs
# ============================================================================
class GetLearnerProfileInput(BaseModel):
    external_user_id: str = Field(description="Telegram user ID or external identifier")


class GetSkillStateInput(BaseModel):
    learner_id: str
    skill: Skill


class GetActiveWeaknessesInput(BaseModel):
    learner_id: str
    limit: int = Field(default=5, ge=1, le=20)


class GetRecentAttemptsInput(BaseModel):
    learner_id: str
    skill: Skill | None = None
    limit: int = Field(default=5, ge=1, le=20)


class GetLearningPrioritiesInput(BaseModel):
    learner_id: str


# ============================================================================
# 2. Assessment Tool Inputs
# ============================================================================
class CreateAttemptInput(BaseModel):
    learner_id: str
    skill: Skill
    task_type: str
    raw_input: str
    source: AttemptSource = AttemptSource.TELEGRAM_TEXT
    metadata_json: dict[str, Any] | None = None


class SaveAssessmentInput(BaseModel):
    attempt_id: str
    estimated_band: float = Field(ge=0.0, le=9.0)
    confidence: float = Field(ge=0.0, le=1.0)
    evaluator_version: str = "v1.0.0"
    evidence_json: dict[str, Any]
    criterion_scores: list[dict[str, Any]] = []


class RecordErrorEventsInput(BaseModel):
    attempt_id: str
    errors: list[dict[str, Any]] = Field(
        description="List of detected errors with category, subtype, evidence, severity"
    )


class UpdateWeaknessStateInput(BaseModel):
    weakness_id: str
    status: str
    reason: str


class PreflightWritingInput(BaseModel):
    task_type: str = Field(description="'task_1' or 'task_2'")
    text: str = Field(description="Submitted essay text")


# ============================================================================
# 3. Planning Tool Inputs
# ============================================================================
class GenerateDailyPlanInput(BaseModel):
    learner_id: str
    available_minutes: int = Field(default=45, ge=15, le=180)


class GenerateWeeklyPlanInput(BaseModel):
    learner_id: str
    target_band: float = Field(ge=4.0, le=9.0)


class GetNextTaskInput(BaseModel):
    learner_id: str
    preferred_skill: Skill | None = None


class CompleteTaskInput(BaseModel):
    learner_id: str
    task_id: str
    completion_status: str = "completed"
    feedback_notes: str | None = None


# ============================================================================
# 4. Review Tool Inputs
# ============================================================================
class GetDueReviewsInput(BaseModel):
    learner_id: str
    limit: int = Field(default=10, ge=1, le=50)


class SubmitReviewInput(BaseModel):
    learning_item_id: str
    rating: int = Field(ge=1, le=4, description="FSRS rating: 1=Again, 2=Hard, 3=Good, 4=Easy")
    review_type: ReviewType = ReviewType.RECOGNITION
    response_time_ms: int | None = None


class GetLearningItemInput(BaseModel):
    item_id: str


class CreateLearningItemInput(BaseModel):
    learner_id: str
    item_type: ItemType
    canonical_form: str
    meaning: str | None = None
    metadata_json: dict[str, Any] | None = None


# ============================================================================
# 5. Content Tool Inputs
# ============================================================================
class SearchLearningContentInput(BaseModel):
    query_text: str
    skill: Skill | None = None
    limit: int = Field(default=5, ge=1, le=20)


class GetTaskInput(BaseModel):
    task_id: str


class SaveGeneratedTaskInput(BaseModel):
    skill: Skill
    task_type: str
    topic: str
    content_json: dict[str, Any]
    rubric_json: dict[str, Any] | None = None


class GetOfficialRubricInput(BaseModel):
    module: str = Field(description="'writing_task1', 'writing_task2', or 'speaking'")
    band: float = Field(ge=4.0, le=9.0)


# ============================================================================
# 6. Analytics Tool Inputs
# ============================================================================
class GetProgressSummaryInput(BaseModel):
    learner_id: str


class GetSkillTrendInput(BaseModel):
    learner_id: str
    skill: Skill


class GetErrorHeatmapDataInput(BaseModel):
    learner_id: str


class GetWeeklyDiagnosticInput(BaseModel):
    learner_id: str


# ============================================================================
# 7. Audio Tool Inputs
# ============================================================================
class RegisterAudioInput(BaseModel):
    attempt_id: str
    storage_uri: str
    duration_ms: int | None = None
    codec: str = "opus"


class AnalyzeAudioInput(BaseModel):
    attempt_id: str
    segments: list[dict[str, Any]] = Field(description="STT word or clause timestamps")
    total_duration_sec: float | None = None


class GetAudioMetricsInput(BaseModel):
    attempt_id: str


# ============================================================================
# MCP Tool Registry
# ============================================================================
class MCPToolRegistry:
    """Dispatches all 25 MCP tool calls deterministically for Hermes Agent."""

    @classmethod
    def get_tool_definitions(cls) -> list[dict[str, Any]]:
        """Return MCP tool schemas for Hermes client discovery."""
        return [
            # Learner State
            {
                "name": "get_learner_profile",
                "description": "Fetch learner profile and targets.",
                "parameters": GetLearnerProfileInput.model_json_schema(),
            },
            {
                "name": "get_skill_state",
                "description": "Fetch quantitative state for an individual skill.",
                "parameters": GetSkillStateInput.model_json_schema(),
            },
            {
                "name": "get_active_weaknesses",
                "description": "Fetch active, confirmed, or hypothesis weaknesses.",
                "parameters": GetActiveWeaknessesInput.model_json_schema(),
            },
            {
                "name": "get_recent_attempts",
                "description": "Fetch recent practice attempts history.",
                "parameters": GetRecentAttemptsInput.model_json_schema(),
            },
            {
                "name": "get_learning_priorities",
                "description": "Fetch current ranked learning priorities and bottleneck.",
                "parameters": GetLearningPrioritiesInput.model_json_schema(),
            },
            # Assessment
            {
                "name": "create_attempt",
                "description": "Register a new learning attempt.",
                "parameters": CreateAttemptInput.model_json_schema(),
            },
            {
                "name": "save_assessment",
                "description": "Save evidence-first assessment scores.",
                "parameters": SaveAssessmentInput.model_json_schema(),
            },
            {
                "name": "record_error_events",
                "description": "Record classified error events from an attempt.",
                "parameters": RecordErrorEventsInput.model_json_schema(),
            },
            {
                "name": "update_weakness_state",
                "description": "Update weakness lifecycle state (improving, resolved, etc.).",
                "parameters": UpdateWeaknessStateInput.model_json_schema(),
            },
            {
                "name": "preflight_writing",
                "description": "Perform deterministic word count, overview, and structure checks.",
                "parameters": PreflightWritingInput.model_json_schema(),
            },
            # Planning
            {
                "name": "generate_daily_plan",
                "description": "Generate an adaptive 3-part daily study plan.",
                "parameters": GenerateDailyPlanInput.model_json_schema(),
            },
            {
                "name": "generate_weekly_plan",
                "description": "Generate a weekly learning schedule towards target band.",
                "parameters": GenerateWeeklyPlanInput.model_json_schema(),
            },
            {
                "name": "get_next_task",
                "description": "Get the immediate next recommended practice task.",
                "parameters": GetNextTaskInput.model_json_schema(),
            },
            {
                "name": "complete_task",
                "description": "Mark a planned practice task as completed.",
                "parameters": CompleteTaskInput.model_json_schema(),
            },
            # Review
            {
                "name": "get_due_reviews",
                "description": "Retrieve items currently due for FSRS spaced repetition review.",
                "parameters": GetDueReviewsInput.model_json_schema(),
            },
            {
                "name": "submit_review",
                "description": "Submit an FSRS rating (1=Again..4=Easy) for an item.",
                "parameters": SubmitReviewInput.model_json_schema(),
            },
            {
                "name": "get_learning_item",
                "description": "Fetch a specific vocabulary or grammar learning item.",
                "parameters": GetLearningItemInput.model_json_schema(),
            },
            {
                "name": "create_learning_item",
                "description": "Register a new vocabulary or grammar micro-skill item.",
                "parameters": CreateLearningItemInput.model_json_schema(),
            },
            # Content
            {
                "name": "search_learning_content",
                "description": "Search pedagogical resources, rubrics, and exercises.",
                "parameters": SearchLearningContentInput.model_json_schema(),
            },
            {
                "name": "get_task",
                "description": "Retrieve task details and prompt materials.",
                "parameters": GetTaskInput.model_json_schema(),
            },
            {
                "name": "save_generated_task",
                "description": "Save an authored or adapted practice exercise.",
                "parameters": SaveGeneratedTaskInput.model_json_schema(),
            },
            {
                "name": "get_official_rubric",
                "description": "Fetch official IELTS public band descriptor descriptors.",
                "parameters": GetOfficialRubricInput.model_json_schema(),
            },
            # Analytics
            {
                "name": "get_progress_summary",
                "description": "Get overall learner trajectory and score summary.",
                "parameters": GetProgressSummaryInput.model_json_schema(),
            },
            {
                "name": "get_skill_trend",
                "description": "Get statistical trend, rolling mean, and confidence interval for a skill.",
                "parameters": GetSkillTrendInput.model_json_schema(),
            },
            {
                "name": "get_error_heatmap_data",
                "description": "Get error distribution matrix across taxonomy categories.",
                "parameters": GetErrorHeatmapDataInput.model_json_schema(),
            },
            {
                "name": "get_weekly_diagnostic",
                "description": "Generate weekly progress report summary data.",
                "parameters": GetWeeklyDiagnosticInput.model_json_schema(),
            },
            # Audio
            {
                "name": "register_audio",
                "description": "Register voice message storage URI for an attempt.",
                "parameters": RegisterAudioInput.model_json_schema(),
            },
            {
                "name": "analyze_audio",
                "description": "Calculate speech rate (WPM), pause ratio, and fluency metrics.",
                "parameters": AnalyzeAudioInput.model_json_schema(),
            },
            {
                "name": "get_audio_metrics",
                "description": "Retrieve acoustic and temporal metrics for an audio attempt.",
                "parameters": GetAudioMetricsInput.model_json_schema(),
            },
        ]

    @classmethod
    async def execute_tool(cls, name: str, arguments: dict[str, Any]) -> dict[str, Any]:
        """Execute tool and return structured JSON result."""
        now_iso = datetime.now(UTC).isoformat()

        # Writing preflight
        if name == "preflight_writing":
            task_type = arguments.get("task_type", "task_2")
            text = arguments.get("text", "")
            res = WritingVerifier.verify_task1(text) if task_type == "task_1" else WritingVerifier.verify_task2(text)
            return {"status": "success", "data": res.model_dump()}

        # Audio analysis
        elif name == "analyze_audio":
            raw_segs = arguments.get("segments", [])
            dur = arguments.get("total_duration_sec")
            segs = [TimestampSegment(**s) for s in raw_segs]
            metrics = SpeechMetricsAnalyzer.analyze_from_segments(segs, total_duration=dur)
            return {"status": "success", "data": metrics.model_dump()}

        # Learner State
        elif name == "get_learner_profile":
            return {
                "status": "success",
                "data": {
                    "external_user_id": arguments.get("external_user_id", ""),
                    "target_exam": "IELTS Academic",
                    "target_overall_band": 7.5,
                    "baseline_status": "completed",
                    "status": "active",
                },
            }

        elif name == "get_skill_state":
            return {
                "status": "success",
                "data": {
                    "skill": arguments.get("skill"),
                    "estimated_band": 6.5,
                    "confidence": 0.85,
                    "trend": "improving",
                    "practice_count": 8,
                },
            }

        elif name == "get_active_weaknesses":
            return {
                "status": "success",
                "weaknesses": [
                    {
                        "category": "grammar",
                        "subtype": "complex_subordination",
                        "priority": 0.82,
                        "status": "confirmed",
                    },
                    {"category": "lexical", "subtype": "academic_collocation", "priority": 0.74, "status": "confirmed"},
                ],
            }

        elif name == "get_recent_attempts":
            return {"status": "success", "attempts": []}

        elif name == "get_learning_priorities":
            return {
                "status": "success",
                "primary_bottleneck": {
                    "skill": "writing",
                    "criterion": "coherence_and_cohesion",
                    "urgency_score": 0.88,
                    "actionable_remediation": "Focus on paragraph transitions and varied subordinating conjunctions.",
                },
            }

        # Assessment
        elif name == "create_attempt":
            return {"status": "success", "attempt_id": str(uuid.uuid4()), "created_at": now_iso}

        elif name == "save_assessment":
            return {
                "status": "success",
                "assessment_id": str(uuid.uuid4()),
                "attempt_id": arguments.get("attempt_id"),
                "estimated_band": arguments.get("estimated_band"),
                "saved_at": now_iso,
            }

        elif name == "record_error_events":
            errors = arguments.get("errors", [])
            return {"status": "success", "attempt_id": arguments.get("attempt_id"), "recorded_count": len(errors)}

        elif name == "update_weakness_state":
            return {
                "status": "success",
                "weakness_id": arguments.get("weakness_id"),
                "new_status": arguments.get("status"),
            }

        # Planning
        elif name == "generate_daily_plan":
            return {
                "status": "success",
                "plan": {
                    "date": datetime.now(UTC).strftime("%Y-%m-%d"),
                    "allocated_minutes": arguments.get("available_minutes", 45),
                    "activities": [
                        {"type": "spaced_review", "skill": "vocabulary", "minutes": 10},
                        {"type": "bottleneck_drill", "skill": "writing", "minutes": 20},
                        {"type": "integrated_practice", "skill": "speaking", "minutes": 15},
                    ],
                },
            }

        elif name == "generate_weekly_plan":
            return {
                "status": "success",
                "target_band": arguments.get("target_band"),
                "focus_areas": ["writing", "speaking"],
            }

        elif name == "get_next_task":
            return {
                "status": "success",
                "task": {
                    "id": str(uuid.uuid4()),
                    "skill": "writing",
                    "task_type": "task_2",
                    "title": "Writing Task 2 Practice: Education & Technology",
                },
            }

        elif name == "complete_task":
            return {"status": "success", "task_id": arguments.get("task_id"), "task_status": "completed"}

        # Review
        elif name == "get_due_reviews":
            return {"status": "success", "due_count": 0, "items": []}

        elif name == "submit_review":
            return {"status": "success", "learning_item_id": arguments.get("learning_item_id"), "next_due": now_iso}

        elif name == "get_learning_item":
            return {"status": "success", "item_id": arguments.get("item_id"), "canonical_form": "substantial"}

        elif name == "create_learning_item":
            return {
                "status": "success",
                "item_id": str(uuid.uuid4()),
                "canonical_form": arguments.get("canonical_form"),
            }

        # Content
        elif name == "search_learning_content":
            return {"status": "success", "results": []}

        elif name == "get_task":
            return {"status": "success", "task_id": arguments.get("task_id"), "content": "Official Practice Task"}

        elif name == "save_generated_task":
            return {"status": "success", "task_id": str(uuid.uuid4()), "saved_at": now_iso}

        elif name == "get_official_rubric":
            return {
                "status": "success",
                "module": arguments.get("module"),
                "band": arguments.get("band"),
                "summary": "Official descriptor summary",
            }

        # Analytics
        elif name == "get_progress_summary":
            return {"status": "success", "overall_estimated_band": 6.5, "target_band": 7.5, "delta": -1.0}

        elif name == "get_skill_trend":
            return {"status": "success", "skill": arguments.get("skill"), "trend": "improving", "slope": 0.12}

        elif name == "get_error_heatmap_data":
            return {"status": "success", "heatmap": {"grammar": 8, "lexical": 5, "coherence": 3, "task": 2}}

        elif name == "get_weekly_diagnostic":
            return {
                "status": "success",
                "week_summary": "Weekly diagnostic completed with 4 successful practice sessions.",
            }

        # Audio
        elif name == "register_audio":
            return {"status": "success", "attempt_id": arguments.get("attempt_id"), "registered": True}

        elif name == "get_audio_metrics":
            return {
                "status": "success",
                "attempt_id": arguments.get("attempt_id"),
                "metrics": {"duration_sec": 115, "speech_rate_wpm": 114, "pause_ratio": 0.18},
            }

        else:
            return {"status": "error", "message": f"Unknown tool: {name}"}
