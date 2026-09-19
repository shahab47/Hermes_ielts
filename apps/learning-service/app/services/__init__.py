"""Domain and analysis services for IELTS Learning Service."""

from app.services.error_aggregator import AggregatedErrorGroup, ErrorAggregationService
from app.services.priority_calculator import PriorityBreakdown, PriorityCalculator
from app.services.trend_calculator import TrendAnalysis, TrendCalculator
from app.services.weakness_service import WeaknessLifecycleService, WeaknessTransitionDecision

__all__ = [
    "AggregatedErrorGroup",
    "ErrorAggregationService",
    "PriorityBreakdown",
    "PriorityCalculator",
    "TrendAnalysis",
    "TrendCalculator",
    "WeaknessLifecycleService",
    "WeaknessTransitionDecision",
]
