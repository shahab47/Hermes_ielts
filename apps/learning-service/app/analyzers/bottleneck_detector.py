"""Deterministic training bottleneck detection engine."""

from __future__ import annotations

from collections.abc import Sequence

from pydantic import BaseModel, Field

from app.models.error import Weakness
from app.models.learner import Skill, SkillState


class BottleneckCandidate(BaseModel):
    """Scored candidate bottleneck."""

    skill: Skill
    criterion: str
    criterion_gap: float = Field(description="Target band minus estimated band")
    recurrence_weight: float = Field(description="Weight from associated active weaknesses")
    confidence: float
    urgency_score: float = Field(description="Aggregate urgency score [0, 1]")
    rationale: str


class PrimaryBottleneck(BaseModel):
    """The selected primary training bottleneck for the learner."""

    selected_skill: Skill
    selected_criterion: str
    urgency_score: float
    rationale: str
    actionable_remediation: str
    contributing_weaknesses: list[str] = []


class BottleneckDetector:
    """Identifies the single highest-impact bottleneck limiting the learner's overall IELTS score."""

    @classmethod
    def detect_primary_bottleneck(
        cls,
        target_overall_band: float,
        skill_states: Sequence[SkillState],
        active_weaknesses: Sequence[Weakness],
    ) -> PrimaryBottleneck | None:
        """Evaluate all skills and weaknesses to select the primary bottleneck."""
        if not skill_states:
            return None

        candidates: list[BottleneckCandidate] = []

        for state in skill_states:
            curr_band = state.estimated_band if state.estimated_band is not None else 5.0
            gap = max(target_overall_band - curr_band, 0.0)

            # Match active weaknesses belonging to this skill
            skill_weaknesses = [
                w
                for w in active_weaknesses
                if w.category.value == state.skill.value or state.skill.value in ("writing", "speaking")
            ]
            rec_weight = sum(w.priority for w in skill_weaknesses)
            norm_rec = min(rec_weight / 3.0, 1.0)

            # Urgency = 0.45 * gap_norm + 0.35 * recurrence + 0.20 * confidence
            gap_norm = min(gap / 2.5, 1.0)
            conf = state.confidence if state.confidence > 0 else 0.5
            urgency = (0.45 * gap_norm) + (0.35 * norm_rec) + (0.20 * conf)

            candidates.append(
                BottleneckCandidate(
                    skill=state.skill,
                    criterion=f"{state.skill.value}_overall",
                    criterion_gap=round(gap, 2),
                    recurrence_weight=round(norm_rec, 2),
                    confidence=round(conf, 2),
                    urgency_score=round(urgency, 4),
                    rationale=(
                        f"{state.skill.value.capitalize()} band is {curr_band:.1f} vs target {target_overall_band:.1f} "
                        f"(gap: {gap:.1f}, {len(skill_weaknesses)} active weaknesses)"
                    ),
                )
            )

        if not candidates:
            return None

        # Sort candidates descending by urgency
        candidates.sort(key=lambda c: c.urgency_score, reverse=True)
        top = candidates[0]

        top_weaknesses = [
            f"{w.category.value}: {w.subtype}"
            for w in active_weaknesses
            if w.category.value == top.skill.value or top.skill.value in ("writing", "speaking")
        ][:3]

        remediation_map = {
            Skill.WRITING: "Focus on Task 2 structure, clear topic sentences, and eliminating repetitive cohesive devices.",
            Skill.SPEAKING: "Conduct timed Part 2 drills to build fluency and reduce mid-clause hesitation.",
            Skill.READING: "Practice skimming for main ideas and targeted scanning for True/False/Not Given questions.",
            Skill.LISTENING: "Focus on Section 3/4 distractors, spelling precision, and signposting words.",
            Skill.VOCABULARY: "Complete daily FSRS reviews of high-yield academic collocations.",
            Skill.GRAMMAR: "Complete focused micro-drills on complex sentence subordination and article accuracy.",
            Skill.PRONUNCIATION: "Practice sentence stress and connected speech chunking.",
        }

        return PrimaryBottleneck(
            selected_skill=top.skill,
            selected_criterion=top.criterion,
            urgency_score=top.urgency_score,
            rationale=top.rationale,
            actionable_remediation=remediation_map.get(
                top.skill, "Complete targeted drills in your weakest skill area."
            ),
            contributing_weaknesses=top_weaknesses,
        )
