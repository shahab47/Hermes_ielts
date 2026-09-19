"""Comprehensive unit tests for the deterministic learner-state engine (Phase 4)."""

from __future__ import annotations

import uuid
from datetime import UTC, datetime, timedelta

from app.models.error import ErrorCategory, ErrorSeverity, WeaknessStatus
from app.models.learner import Trend
from app.schemas.error import ErrorEventCreate
from app.services import (
    ErrorAggregationService,
    PriorityCalculator,
    TrendCalculator,
    WeaknessLifecycleService,
)


def test_priority_calculator_bounds_and_weights() -> None:
    """Test that priority calculator outputs valid normalized scores."""
    now = datetime.now(UTC)
    one_day_ago = now - timedelta(days=1)

    breakdown = PriorityCalculator.compute(
        recurrence_count=4,
        estimated_band_impact=0.5,
        confidence=0.85,
        last_seen_at=one_day_ago,
        current_band=6.0,
        target_band=7.5,
        task_relevance=1.0,
        now=now,
    )

    assert 0.0 <= breakdown.final_priority <= 1.0
    assert 0.0 <= breakdown.recurrence_score <= 1.0
    assert 0.0 <= breakdown.impact_score <= 1.0
    assert 0.0 <= breakdown.confidence_score <= 1.0
    assert 0.0 <= breakdown.recency_score <= 1.0
    assert 0.0 <= breakdown.target_gap_score <= 1.0
    assert breakdown.recurrence_score == 0.8  # 4 / 5 = 0.8
    assert breakdown.impact_score == 0.5  # 0.5 / 1.0 = 0.5


def test_priority_recency_decay() -> None:
    """Test that older errors decay in recency score and priority."""
    now = datetime.now(UTC)
    recent = now - timedelta(days=1)
    old = now - timedelta(days=28)  # 2 half-lives

    recent_priority = PriorityCalculator.compute(
        recurrence_count=3,
        estimated_band_impact=0.5,
        confidence=0.8,
        last_seen_at=recent,
        now=now,
    )

    old_priority = PriorityCalculator.compute(
        recurrence_count=3,
        estimated_band_impact=0.5,
        confidence=0.8,
        last_seen_at=old,
        now=now,
    )

    assert recent_priority.recency_score > old_priority.recency_score
    assert recent_priority.final_priority > old_priority.final_priority


def test_trend_calculator_insufficient_data() -> None:
    """Test that fewer than 3 samples yield INSUFFICIENT_DATA."""
    res_empty = TrendCalculator.analyze([])
    assert res_empty.trend == Trend.INSUFFICIENT_DATA
    assert res_empty.sample_size == 0

    res_two = TrendCalculator.analyze([6.0, 6.5])
    assert res_two.trend == Trend.INSUFFICIENT_DATA
    assert res_two.sample_size == 2
    assert res_two.last_score == 6.5
    assert res_two.rolling_mean == 6.25


def test_trend_calculator_progression() -> None:
    """Test improving, declining, and stable trajectories."""
    # Improving: 5.5 -> 6.0 -> 6.5 -> 7.0
    improving = TrendCalculator.analyze([5.5, 6.0, 6.5, 7.0])
    assert improving.trend == Trend.IMPROVING
    assert improving.slope is not None and improving.slope > 0.08
    assert improving.last_score == 7.0

    # Declining: 7.0 -> 6.5 -> 6.0 -> 5.5
    declining = TrendCalculator.analyze([7.0, 6.5, 6.0, 5.5])
    assert declining.trend == Trend.DECLINING
    assert declining.slope is not None and declining.slope < -0.08

    # Stable: 6.5 -> 6.5 -> 6.5 -> 6.5
    stable = TrendCalculator.analyze([6.5, 6.5, 6.5, 6.5])
    assert stable.trend == Trend.STABLE
    assert stable.slope == 0.0


def test_trend_calculator_confidence_interval() -> None:
    """Test 95% confidence interval calculation when n >= 5."""
    res = TrendCalculator.analyze([6.0, 6.5, 6.5, 7.0, 7.0, 7.5])
    assert res.confidence_interval_95 is not None
    assert res.rolling_mean is not None
    lower, upper = res.confidence_interval_95
    assert lower <= res.rolling_mean <= upper


def test_weakness_lifecycle_promotion_to_confirmed() -> None:
    """Test promotion rule: >= 3 occurrences across >= 2 attempts with confidence >= 0.6."""
    now = datetime.now(UTC)

    # Fails rule: only 1 attempt
    dec1 = WeaknessLifecycleService.evaluate_weakness_lifecycle(
        current_status=WeaknessStatus.HYPOTHESIS,
        total_occurrences=4,
        distinct_attempt_count=1,
        consecutive_clean_attempts=0,
        confidence=0.8,
        last_seen_at=now,
    )
    assert dec1.new_status == WeaknessStatus.HYPOTHESIS
    assert not dec1.is_status_changed

    # Meets rule: 3 occurrences across 2 attempts, confidence 0.75
    dec2 = WeaknessLifecycleService.evaluate_weakness_lifecycle(
        current_status=WeaknessStatus.HYPOTHESIS,
        total_occurrences=3,
        distinct_attempt_count=2,
        consecutive_clean_attempts=0,
        confidence=0.75,
        last_seen_at=now,
    )
    assert dec2.new_status == WeaknessStatus.CONFIRMED
    assert dec2.is_status_changed


def test_weakness_resolution_and_regression() -> None:
    """Test progressive resolution (improving -> resolved) and regression detection."""
    now = datetime.now(UTC)

    # 2 clean attempts: CONFIRMED -> IMPROVING
    dec_improving = WeaknessLifecycleService.evaluate_weakness_lifecycle(
        current_status=WeaknessStatus.CONFIRMED,
        total_occurrences=3,
        distinct_attempt_count=2,
        consecutive_clean_attempts=2,
        confidence=0.8,
        last_seen_at=now,
    )
    assert dec_improving.new_status == WeaknessStatus.IMPROVING

    # 3 clean attempts: CONFIRMED -> RESOLVED
    dec_resolved = WeaknessLifecycleService.evaluate_weakness_lifecycle(
        current_status=WeaknessStatus.IMPROVING,
        total_occurrences=3,
        distinct_attempt_count=2,
        consecutive_clean_attempts=3,
        confidence=0.8,
        last_seen_at=now,
    )
    assert dec_resolved.new_status == WeaknessStatus.RESOLVED

    # Regression: RESOLVED with clean attempts dropping to 0
    dec_regressed = WeaknessLifecycleService.evaluate_weakness_lifecycle(
        current_status=WeaknessStatus.RESOLVED,
        total_occurrences=4,
        distinct_attempt_count=3,
        consecutive_clean_attempts=0,
        confidence=0.85,
        last_seen_at=now,
    )
    assert dec_regressed.new_status == WeaknessStatus.CONFIRMED
    assert "Regression detected" in dec_regressed.reason


def test_error_aggregation_grouping() -> None:
    """Test grouping raw error events by category and subtype."""
    attempt_id = uuid.uuid4()
    errors = [
        ErrorEventCreate(
            attempt_id=attempt_id,
            category=ErrorCategory.GRAMMAR,
            subtype="article",
            evidence_text="missing 'the'",
            severity=ErrorSeverity.MEDIUM,
            confidence=0.9,
        ),
        ErrorEventCreate(
            attempt_id=attempt_id,
            category=ErrorCategory.GRAMMAR,
            subtype="article",
            evidence_text="redundant 'a'",
            severity=ErrorSeverity.LOW,
            confidence=0.8,
        ),
        ErrorEventCreate(
            attempt_id=attempt_id,
            category=ErrorCategory.LEXICAL,
            subtype="collocation",
            evidence_text="do a mistake instead of make a mistake",
            severity=ErrorSeverity.HIGH,
            confidence=0.95,
        ),
    ]

    groups = ErrorAggregationService.group_errors(errors)
    assert len(groups) == 2

    grammar_group = next(g for g in groups if g.category == ErrorCategory.GRAMMAR)
    assert grammar_group.subtype == "article"
    assert grammar_group.occurrences == 2
    assert grammar_group.mean_confidence == 0.85

    lexical_group = next(g for g in groups if g.category == ErrorCategory.LEXICAL)
    assert lexical_group.subtype == "collocation"
    assert lexical_group.occurrences == 1
    assert lexical_group.severities == [ErrorSeverity.HIGH]
