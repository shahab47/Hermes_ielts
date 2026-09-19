"""Error aggregation and learner state sync engine."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from dataclasses import dataclass

from app.models.error import ErrorCategory, ErrorSeverity
from app.schemas.error import ErrorEventCreate


@dataclass
class AggregatedErrorGroup:
    """Group of error occurrences under the same category and subtype."""

    category: ErrorCategory
    subtype: str
    occurrences: int
    severities: list[ErrorSeverity]
    mean_confidence: float
    evidence_samples: list[str]


class ErrorAggregationService:
    """Aggregates raw error events from an attempt into structured groups."""

    @classmethod
    def group_errors(
        cls,
        errors: Sequence[ErrorEventCreate],
    ) -> list[AggregatedErrorGroup]:
        """Group a list of error events by (category, subtype)."""
        grouped: dict[tuple[ErrorCategory, str], list[ErrorEventCreate]] = defaultdict(list)

        for err in errors:
            grouped[(err.category, err.subtype)].append(err)

        result: list[AggregatedErrorGroup] = []
        for (category, subtype), group in grouped.items():
            confidences = [e.confidence for e in group]
            mean_conf = sum(confidences) / len(confidences) if confidences else 0.5
            result.append(
                AggregatedErrorGroup(
                    category=category,
                    subtype=subtype,
                    occurrences=len(group),
                    severities=[e.severity for e in group],
                    mean_confidence=round(mean_conf, 3),
                    evidence_samples=[e.evidence_text for e in group[:3]],  # up to 3 excerpts
                )
            )

        return result

    @classmethod
    def calculate_error_impact(cls, severities: Sequence[ErrorSeverity]) -> float:
        """Map severities to estimated band score impact."""
        severity_weights = {
            ErrorSeverity.LOW: 0.1,
            ErrorSeverity.MEDIUM: 0.25,
            ErrorSeverity.HIGH: 0.5,
            ErrorSeverity.CRITICAL: 1.0,
        }
        if not severities:
            return 0.1
        # Highest severity dominates, with slight additive penalty for multiples
        max_impact = max(severity_weights[s] for s in severities)
        count_bonus = min(len(severities) * 0.05, 0.5)
        return min(max_impact + count_bonus, 1.5)
