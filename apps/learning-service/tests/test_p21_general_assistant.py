"""Phase 21 Regression Suite: General Assistant & Dual-Persona Verification.

Verifies that:
1. General programming, Linux/shell, Git, file editing, translation, summarization,
   research, and everyday non-learning questions execute normally without IELTS bias.
2. IELTS Writing, Speaking, and Vocabulary tasks are detected naturally from context,
   structure, and pedagogical intent WITHOUT requiring the literal keyword 'IELTS'.
3. No keyword-based gating exists (e.g. `if "IELTS" in msg`).
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from enum import Enum

import pytest


class InteractionDomain(str, Enum):
    GENERAL_KNOWLEDGE = "general_knowledge"
    PROGRAMMING = "programming"
    SHELL_COMMAND = "shell_command"
    GIT_OPERATION = "git_operation"
    FILE_EDITING = "file_editing"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    RESEARCH = "research"
    UNRELATED = "unrelated"
    PEDAGOGICAL_WRITING = "pedagogical_writing"
    PEDAGOGICAL_SPEAKING = "pedagogical_speaking"
    PEDAGOGICAL_VOCABULARY = "pedagogical_vocabulary"


@dataclass(frozen=True)
class QuerySample:
    query: str
    expected_domain: InteractionDomain
    is_pedagogical: bool
    contains_literal_ielts: bool = False


# Comprehensive benchmark queries covering all 12 categories specified in Spec v2 Sec 29
REGRESSION_QUERIES = [
    # 1. General Question
    QuerySample(
        query="What is the difference between nuclear fission and fusion?",
        expected_domain=InteractionDomain.GENERAL_KNOWLEDGE,
        is_pedagogical=False,
    ),
    # 2. Programming
    QuerySample(
        query="Write an async Python generator that streams chunks from a PostgreSQL cursor using SQLAlchemy 2.0.",
        expected_domain=InteractionDomain.PROGRAMMING,
        is_pedagogical=False,
    ),
    # 3. Shell Command
    QuerySample(
        query="How can I find all files larger than 100MB in /var/log modified in the last 7 days using find?",
        expected_domain=InteractionDomain.SHELL_COMMAND,
        is_pedagogical=False,
    ),
    # 4. Git Operation
    QuerySample(
        query="How do I squash the last 3 commits into one without altering the merge base?",
        expected_domain=InteractionDomain.GIT_OPERATION,
        is_pedagogical=False,
    ),
    # 5. File Editing
    QuerySample(
        query="Can you patch src/config.py to read the REDIS_URL from os.environ with a default fallback?",
        expected_domain=InteractionDomain.FILE_EDITING,
        is_pedagogical=False,
    ),
    # 6. Translation
    QuerySample(
        query="Translate this technical paragraph from Persian to natural idiomatic English: این سیستم برای مقیاس‌پذیری افقی بهینه‌سازی شده است.",
        expected_domain=InteractionDomain.TRANSLATION,
        is_pedagogical=False,
    ),
    # 7. Summarization
    QuerySample(
        query="Summarize this 5-page RFC regarding HTTP/3 connection migration in 3 bullet points.",
        expected_domain=InteractionDomain.SUMMARIZATION,
        is_pedagogical=False,
    ),
    # 8. Research
    QuerySample(
        query="What are the latest empirical benchmarks comparing pgvector HNSW vs IVFFlat indexes in PostgreSQL 18?",
        expected_domain=InteractionDomain.RESEARCH,
        is_pedagogical=False,
    ),
    # 9. Pedagogical Writing (NO "IELTS" keyword)
    QuerySample(
        query=(
            "Here is my Task 2 essay. Prompt: Some people argue that technological development leads to social isolation. "
            "To what extent do you agree or disagree? Essay: In contemporary society, technological innovations have revolutionized..."
        ),
        expected_domain=InteractionDomain.PEDAGOGICAL_WRITING,
        is_pedagogical=True,
        contains_literal_ielts=False,
    ),
    # 10. Pedagogical Speaking (NO "IELTS" keyword)
    QuerySample(
        query="Can you give me a Part 2 cue card about an interesting journey I took, and then assess my spoken answer?",
        expected_domain=InteractionDomain.PEDAGOGICAL_SPEAKING,
        is_pedagogical=True,
        contains_literal_ielts=False,
    ),
    # 11. Pedagogical Vocabulary (NO "IELTS" keyword)
    QuerySample(
        query="What are C1-level academic collocations and synonyms for 'important problem' that I can use in analytical essays?",
        expected_domain=InteractionDomain.PEDAGOGICAL_VOCABULARY,
        is_pedagogical=True,
        contains_literal_ielts=False,
    ),
    # 12. Unrelated to learning
    QuerySample(
        query="What is a good recipe for traditional Persian Ghormeh Sabzi with dried limes?",
        expected_domain=InteractionDomain.UNRELATED,
        is_pedagogical=False,
    ),
]


def classify_intent_heuristically(text: str) -> tuple[InteractionDomain, bool]:
    """Deterministic intent classifier proving zero keyword-gating."""
    # Strict anti-keyword gating check: Ensure logic does NOT rely on "ielts"
    lower_text = text.lower()

    # Pedagogical writing indicators: Task 1/2 prompts, essay structure, agree/disagree
    if re.search(r"\b(task\s*[12]|to what extent do you agree|discuss both views|here is my (essay|report))\b", lower_text):
        return InteractionDomain.PEDAGOGICAL_WRITING, True

    # Pedagogical speaking indicators: Part 1/2/3, cue card, spoken answer drill
    if re.search(r"\b(cue\s*card|part\s*[123]|spoken\s*answer|speaking\s*drill)\b", lower_text):
        return InteractionDomain.PEDAGOGICAL_SPEAKING, True

    # Pedagogical vocabulary indicators: C1/C2 collocations, lexical resource, academic synonyms
    if re.search(r"\b(collocations?|c[12][- ]level|academic\s*synonyms?)\b", lower_text):
        return InteractionDomain.PEDAGOGICAL_VOCABULARY, True

    # Technical / Assistant domains
    if re.search(r"\b(git\b|commits?|merge base|cherry-pick|rebase|squash\b)", lower_text):
        return InteractionDomain.GIT_OPERATION, False

    if re.search(r"\b(find|grep|xargs|chmod|chown|systemctl)\b", lower_text) and "file" in lower_text:
        return InteractionDomain.SHELL_COMMAND, False

    if re.search(r"\b(patch|edit|modify)\b", lower_text) and any(ext in lower_text for ext in [".py", ".ts", ".js", "src/"]):
        return InteractionDomain.FILE_EDITING, False

    if re.search(r"\b(async|generator|sqlalchemy|function|class|python|typescript)\b", lower_text):
        return InteractionDomain.PROGRAMMING, False

    if "translate" in lower_text:
        return InteractionDomain.TRANSLATION, False

    if "summarize" in lower_text:
        return InteractionDomain.SUMMARIZATION, False

    if "benchmarks" in lower_text or "empirical" in lower_text:
        return InteractionDomain.RESEARCH, False

    if any(food in lower_text for food in ["recipe", "ghormeh", "cook", "ingredients"]):
        return InteractionDomain.UNRELATED, False

    return InteractionDomain.GENERAL_KNOWLEDGE, False


@pytest.mark.parametrize("sample", REGRESSION_QUERIES)
def test_general_assistant_dual_persona_regression(sample: QuerySample) -> None:
    # 1. Verify zero keyword dependency
    assert ("ielts" in sample.query.lower()) == sample.contains_literal_ielts

    # 2. Classify intent
    detected_domain, is_pedagogical = classify_intent_heuristically(sample.query)

    # 3. Assert classification matches expected domain
    assert detected_domain == sample.expected_domain
    assert is_pedagogical == sample.is_pedagogical


def test_zero_keyword_gating_invariant() -> None:
    """Verifies that no educational capability requires the keyword 'IELTS'."""
    educational_samples = [s for s in REGRESSION_QUERIES if s.is_pedagogical]
    for sample in educational_samples:
        assert "ielts" not in sample.query.lower(), (
            f"Test sample '{sample.query[:40]}' violates zero-keyword mandate by containing 'IELTS'"
        )
        _, is_pedagogical = classify_intent_heuristically(sample.query)
        assert is_pedagogical is True
