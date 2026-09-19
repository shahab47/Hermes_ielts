"""Weakness lifecycle and recurrence engine."""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel

from app.models.error import WeaknessStatus
from app.services.priority_calculator import PriorityBreakdown, PriorityCalculator


class WeaknessTransitionDecision(BaseModel):
    """Decision on whether a weakness changes status, with rationale."""

    previous_status: WeaknessStatus
    new_status: WeaknessStatus
    reason: str
    is_status_changed: bool
    priority_breakdown: PriorityBreakdown


class WeaknessLifecycleService:
    """Manages promotion, tracking, and resolution of learner weaknesses."""

    # Recurrence rules
    MIN_OCCURRENCES_FOR_CONFIRMATION = 3
    MIN_ATTEMPTS_FOR_CONFIRMATION = 2
    CONFIDENCE_THRESHOLD = 0.60

    # Resolution rules
    CONSECUTIVE_SUCCESS_FOR_IMPROVING = 2
    CONSECUTIVE_SUCCESS_FOR_RESOLUTION = 3

    @classmethod
    def evaluate_weakness_lifecycle(
        cls,
        current_status: WeaknessStatus,
        total_occurrences: int,
        distinct_attempt_count: int,
        consecutive_clean_attempts: int,
        confidence: float,
        last_seen_at: datetime,
        estimated_band_impact: float = 0.5,
        current_band: float | None = None,
        target_band: float | None = None,
        now: datetime | None = None,
    ) -> WeaknessTransitionDecision:
        """Evaluate if a weakness should change state based on deterministic rules."""
        if now is None:
            now = datetime.now(UTC)

        # Calculate updated priority
        priority_breakdown = PriorityCalculator.compute(
            recurrence_count=total_occurrences,
            estimated_band_impact=estimated_band_impact,
            confidence=confidence,
            last_seen_at=last_seen_at,
            current_band=current_band,
            target_band=target_band,
            now=now,
        )

        new_status = current_status
        reason = "Status unchanged"

        # Case 1: Status is HYPOTHESIS
        if current_status == WeaknessStatus.HYPOTHESIS:
            if (
                total_occurrences >= cls.MIN_OCCURRENCES_FOR_CONFIRMATION
                and distinct_attempt_count >= cls.MIN_ATTEMPTS_FOR_CONFIRMATION
                and confidence >= cls.CONFIDENCE_THRESHOLD
            ):
                new_status = WeaknessStatus.CONFIRMED
                reason = (
                    f"Promoted to CONFIRMED: {total_occurrences} occurrences across "
                    f"{distinct_attempt_count} attempts with confidence {confidence:.2f}"
                )
            else:
                reason = "Remains HYPOTHESIS: insufficient recurrence or low confidence"

        # Case 2: Status is CONFIRMED or IMPROVING -> Resolution check
        elif current_status in (WeaknessStatus.CONFIRMED, WeaknessStatus.IMPROVING):
            if consecutive_clean_attempts >= cls.CONSECUTIVE_SUCCESS_FOR_RESOLUTION:
                new_status = WeaknessStatus.RESOLVED
                reason = f"Resolved: {consecutive_clean_attempts} consecutive attempts without error recurrence"
            elif (
                consecutive_clean_attempts >= cls.CONSECUTIVE_SUCCESS_FOR_IMPROVING
                and current_status == WeaknessStatus.CONFIRMED
            ):
                new_status = WeaknessStatus.IMPROVING
                reason = f"Upgraded to IMPROVING: {consecutive_clean_attempts} consecutive clean attempts"

        # Case 3: Status is RESOLVED, but a new recurrence is observed (clean attempts drops to 0)
        elif current_status == WeaknessStatus.RESOLVED and consecutive_clean_attempts == 0:
            new_status = WeaknessStatus.CONFIRMED
            reason = "Regression detected: error recurred after previous resolution"

        return WeaknessTransitionDecision(
            previous_status=current_status,
            new_status=new_status,
            reason=reason,
            is_status_changed=(new_status != current_status),
            priority_breakdown=priority_breakdown,
        )
