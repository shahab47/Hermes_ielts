"""Statistical trend calculator for IELTS skill assessments."""

from __future__ import annotations

import math
import statistics
from collections.abc import Sequence

from pydantic import BaseModel, Field

from app.models.learner import Trend


class TrendAnalysis(BaseModel):
    """Result of skill trend analysis."""

    sample_size: int = Field(ge=0, description="Total number of assessment samples")
    last_score: float | None = Field(default=None, description="Most recent band score")
    rolling_mean: float | None = Field(default=None, description="Rolling mean of recent scores")
    rolling_median: float | None = Field(default=None, description="Rolling median of recent scores")
    trend: Trend = Field(default=Trend.INSUFFICIENT_DATA, description="Calculated trend direction")
    slope: float | None = Field(default=None, description="Linear progression slope (bands per attempt)")
    confidence_interval_95: tuple[float, float] | None = Field(
        default=None, description="95% confidence interval (lower, upper)"
    )


class TrendCalculator:
    """Calculates deterministic trends across temporal IELTS attempts."""

    MIN_SAMPLES_FOR_TREND = 3
    MIN_SAMPLES_FOR_CI = 5
    ROLLING_WINDOW_SIZE = 5

    # Threshold for slope to be considered improving or declining (in band score units per attempt)
    SLOPE_THRESHOLD = 0.08

    @classmethod
    def analyze(
        cls,
        scores_chronological: Sequence[float],
    ) -> TrendAnalysis:
        """Analyze a chronologically ordered sequence of band scores."""
        n = len(scores_chronological)
        if n == 0:
            return TrendAnalysis(sample_size=0, trend=Trend.INSUFFICIENT_DATA)

        last_score = float(scores_chronological[-1])

        if n < cls.MIN_SAMPLES_FOR_TREND:
            return TrendAnalysis(
                sample_size=n,
                last_score=last_score,
                rolling_mean=round(statistics.fmean(scores_chronological), 2),
                rolling_median=round(statistics.median(scores_chronological), 2),
                trend=Trend.INSUFFICIENT_DATA,
            )

        # Recent window for rolling mean and median
        recent_window = list(scores_chronological[-cls.ROLLING_WINDOW_SIZE :])
        r_mean = round(statistics.fmean(recent_window), 2)
        r_median = round(statistics.median(recent_window), 2)

        # Linear regression slope (y = scores, x = 0..k-1) over the window or all samples
        window_size = len(recent_window)
        x_vals = list(range(window_size))
        x_bar = statistics.fmean(x_vals)
        y_bar = statistics.fmean(recent_window)

        denom = sum((x - x_bar) ** 2 for x in x_vals)
        slope = (
            sum((x - x_bar) * (y - y_bar) for x, y in zip(x_vals, recent_window, strict=False)) / denom
            if denom > 0
            else 0.0
        )
        slope = round(slope, 3)

        # Determine trend direction
        if slope > cls.SLOPE_THRESHOLD:
            trend = Trend.IMPROVING
        elif slope < -cls.SLOPE_THRESHOLD:
            trend = Trend.DECLINING
        else:
            trend = Trend.STABLE

        # 95% Confidence Interval (t-distribution approx with 1.96 / standard error if sample >= 5)
        ci_95: tuple[float, float] | None = None
        if n >= cls.MIN_SAMPLES_FOR_CI:
            std_dev = statistics.stdev(recent_window)
            std_err = std_dev / math.sqrt(window_size)
            # using 2.0 for approx 95% t-interval with small samples
            margin = 2.0 * std_err
            ci_lower = round(max(r_mean - margin, 0.0), 2)
            ci_upper = round(min(r_mean + margin, 9.0), 2)
            ci_95 = (ci_lower, ci_upper)

        return TrendAnalysis(
            sample_size=n,
            last_score=last_score,
            rolling_mean=r_mean,
            rolling_median=r_median,
            trend=trend,
            slope=slope,
            confidence_interval_95=ci_95,
        )
