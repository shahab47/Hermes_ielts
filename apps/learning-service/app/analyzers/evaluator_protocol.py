"""Evidence-first assessment protocol definitions and validation."""

from __future__ import annotations

from pydantic import BaseModel, Field, model_validator


class CriterionEvaluation(BaseModel):
    """Rigorous, evidence-backed evaluation of a single criterion."""

    criterion_name: str
    band_score: float = Field(ge=0.0, le=9.0)
    confidence: float = Field(ge=0.0, le=1.0)
    positive_evidence: list[str] = Field(min_length=1, description="Concrete excerpts demonstrating competence")
    limiting_evidence: list[str] = Field(description="Concrete excerpts demonstrating score ceiling")
    descriptor_justification: str = Field(min_length=10, description="Mapping to official public descriptors")
    evaluator_version: str = "v1.0.0"


class WritingAssessmentResult(BaseModel):
    """Complete evidence-first assessment for an IELTS Writing submission."""

    overall_band: float = Field(ge=0.0, le=9.0)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    evaluator_model: str
    evaluator_version: str
    task_achievement_or_response: CriterionEvaluation
    coherence_and_cohesion: CriterionEvaluation
    lexical_resource: CriterionEvaluation
    grammatical_range_and_accuracy: CriterionEvaluation
    primary_bottleneck: str
    actionable_remediation: str

    @model_validator(mode="after")
    def verify_overall_is_average(self) -> WritingAssessmentResult:
        """Verify that overall band matches the four-criteria arithmetic mean."""
        criteria_scores = [
            self.task_achievement_or_response.band_score,
            self.coherence_and_cohesion.band_score,
            self.lexical_resource.band_score,
            self.grammatical_range_and_accuracy.band_score,
        ]
        mean = sum(criteria_scores) / 4.0
        # Check that reported overall is within 0.5 of mean
        if abs(self.overall_band - mean) > 0.5:
            raise ValueError(f"Overall band {self.overall_band} deviates significantly from criteria mean {mean:.2f}")
        return self


class SpeakingAssessmentResult(BaseModel):
    """Complete evidence-first assessment for an IELTS Speaking response."""

    overall_band: float = Field(ge=0.0, le=9.0)
    overall_confidence: float = Field(ge=0.0, le=1.0)
    evaluator_model: str
    evaluator_version: str
    fluency_and_coherence: CriterionEvaluation
    lexical_resource: CriterionEvaluation
    grammatical_range_and_accuracy: CriterionEvaluation
    pronunciation: CriterionEvaluation | None = None
    is_transcript_only: bool = False
    pronunciation_status: str = "evaluated"

    @model_validator(mode="after")
    def enforce_transcript_only_pronunciation_policy(self) -> SpeakingAssessmentResult:
        """Enforce non-negotiable rule: Pronunciation must be marked unassessed in transcript-only mode."""
        if self.is_transcript_only:
            self.pronunciation = None
            self.pronunciation_status = "unassessed (transcript only - audio required)"
        return self
