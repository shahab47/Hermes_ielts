"""Initial diagnostic and learner onboarding endpoints (Phase 14)."""

from __future__ import annotations

import uuid
from datetime import datetime

from fastapi import APIRouter
from pydantic import BaseModel, Field

from app.models.learner import BaselineStatus
from app.planner.adaptive_planner import AdaptivePlanner, DailyStudyPlan

router = APIRouter(prefix="/diagnostic", tags=["diagnostic"])


class OnboardingProfileInput(BaseModel):
    """Initial learner information collected during onboarding."""

    external_user_id: str
    target_exam: str = "IELTS Academic"
    target_overall_band: float = Field(ge=4.0, le=9.0)
    exam_date: datetime | None = None
    available_daily_minutes: int = Field(default=45, ge=15, le=180)
    explanation_language: str = "fa"
    prior_overall_score: float | None = None


class DiagnosticBaselineResult(BaseModel):
    """Result of initial diagnostic test ingestion."""

    learner_id: uuid.UUID
    baseline_status: BaselineStatus
    initial_estimated_band: float
    detected_bottleneck_hypothesis: str
    first_week_plan: DailyStudyPlan


@router.post("/onboard", response_model=DiagnosticBaselineResult)
async def onboard_learner(profile: OnboardingProfileInput) -> DiagnosticBaselineResult:
    """Initialize learner baseline profile and generate the first study plan."""
    learner_id = uuid.uuid4()
    base_band = profile.prior_overall_score if profile.prior_overall_score is not None else 5.5

    # Generate initial 7-day starting plan
    first_plan = AdaptivePlanner.generate_daily_plan(
        target_overall_band=profile.target_overall_band,
        bottleneck=None,
        due_items=[],
        active_weaknesses=[],
        available_minutes=profile.available_daily_minutes,
        exam_date=profile.exam_date,
    )

    return DiagnosticBaselineResult(
        learner_id=learner_id,
        baseline_status=BaselineStatus.COMPLETED,
        initial_estimated_band=base_band,
        detected_bottleneck_hypothesis="Hypothesis: Task 2 structure and cohesive device variety (pending test confirmation)",
        first_week_plan=first_plan,
    )
