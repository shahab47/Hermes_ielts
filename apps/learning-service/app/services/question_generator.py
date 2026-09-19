"""Question Generation and Anti-Hallucination Validation Engine (Phase P17).

Applies strict schema validation, duplicate detection, answerability checks,
leakage detection, and quality gates to AI-generated questions.
"""

from __future__ import annotations

import difflib
import re
from typing import Any

from pydantic import ValidationError

from app.domain.question_bank import (
    Question,
    QuestionReviewStatus,
)


class QuestionGeneratorService:
    """Anti-hallucination validation and quality engine for generated practice questions."""

    @classmethod
    def check_answer_leakage(cls, prompt: str, accepted_answers: list[str]) -> bool:
        """Returns True if the prompt accidentally leaks the exact answer."""
        prompt_lower = prompt.lower()
        for ans in accepted_answers:
            if not ans.strip():
                continue
            # Check if answer appears verbatim in parentheses or as an explicit fill
            pattern = rf"\(\s*{re.escape(ans.lower())}\s*\)"
            if re.search(pattern, prompt_lower):
                return True
            leakage_phrase = rf"(?:the answer is|correct option is)\s*{re.escape(ans.lower())}"
            if re.search(leakage_phrase, prompt_lower):
                return True
        return False

    @classmethod
    def check_answerability(cls, passage: str | None, accepted_answers: list[str]) -> bool:
        """Validates that at least one key term of the accepted answer is grounded in the passage."""
        if not passage or not passage.strip():
            # If no passage required (e.g. general grammar drill or speaking prompt), pass
            return True

        passage_lower = passage.lower()
        for ans in accepted_answers:
            tokens = [t.strip() for t in ans.lower().split() if len(t.strip()) > 3]
            if not tokens:
                # Short word (e.g. 'A', 'True', numbers)
                if ans.lower() in passage_lower:
                    return True
                continue
            # If any significant token appears in passage, consider grounded
            if any(t in passage_lower for t in tokens):
                return True
        return False

    @classmethod
    def check_duplicate(cls, new_prompt: str, existing_prompts: list[str], threshold: float = 0.85) -> bool:
        """Detects near-duplicate questions using similarity ratio."""
        new_clean = new_prompt.strip().lower()
        for existing in existing_prompts:
            ratio = difflib.SequenceMatcher(None, new_clean, existing.strip().lower()).ratio()
            if ratio >= threshold:
                return True
        return False

    @classmethod
    def validate_and_build(
        cls,
        candidate_data: dict[str, Any],
        passage_context: str | None = None,
        existing_prompts: list[str] | None = None,
    ) -> tuple[bool, list[str], Question | None]:
        """Strict validation pipeline executing all Hard Rejection Rules from Spec v3."""
        rejection_reasons: list[str] = []

        # 1. Schema Validation
        try:
            question = Question.model_validate(candidate_data)
        except ValidationError as e:
            return False, [f"Schema validation error: {e}"], None

        # 2. Hard Rule: False Official Attribution
        # Generated questions must NEVER claim to be official British Council/Cambridge/IDP
        provenance = question.provenance
        if provenance.is_generated:
            pub_lower = provenance.publisher.lower()
            if any(org in pub_lower for org in ["cambridge", "idp", "british council", "official ielts"]):
                rejection_reasons.append(
                    "Generated question falsely claims official provenance (hard violation of Section 26/41)."
                )

        # 3. Hard Rule: Empty or missing explanation
        if not question.explanation.text or len(question.explanation.text.strip()) < 10:
            rejection_reasons.append("Explanation is missing or insufficiently detailed (< 10 chars).")

        # 4. Hard Rule: Duplicate options or empty options in MCQ
        if question.options:
            seen_texts: set[str] = set()
            for opt in question.options:
                cleaned = opt.text.strip().lower()
                if cleaned in seen_texts:
                    rejection_reasons.append(f"Duplicate option text detected: '{opt.text}'.")
                seen_texts.add(cleaned)

        # 5. Hard Rule: Answer Leakage
        if cls.check_answer_leakage(question.prompt, question.answer.accepted_values):
            rejection_reasons.append("Prompt contains answer leakage.")

        # 6. Hard Rule: Answerability from Passage
        if passage_context and not cls.check_answerability(passage_context, question.answer.accepted_values):
            rejection_reasons.append("Accepted answer cannot be grounded in or inferred from the provided passage.")

        # 7. Duplicate Check
        if existing_prompts and cls.check_duplicate(question.prompt, existing_prompts):
            rejection_reasons.append("Question is a near-duplicate of an existing question bank item.")

        if rejection_reasons:
            question.review_status = QuestionReviewStatus.REJECTED
            question.quality_score = 0.0
            return False, rejection_reasons, question

        # Calculate quality score based on richness
        quality_score = 1.0
        if not question.explanation.target_evidence:
            quality_score -= 0.15
        if not question.tags:
            quality_score -= 0.10
        question.quality_score = max(0.5, quality_score)
        question.review_status = QuestionReviewStatus.VALIDATED

        return True, [], question
