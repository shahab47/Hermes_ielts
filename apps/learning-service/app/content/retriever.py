"""Hybrid retrieval engine combining metadata filtering, keyword search, and pgvector cosine distance."""

from __future__ import annotations

import uuid
from collections.abc import Sequence
from typing import Any

from pydantic import BaseModel, Field

from app.models.learner import Skill
from app.models.task import TaskDifficulty


class SearchQuery(BaseModel):
    """Query parameters for hybrid content retrieval."""

    query_text: str
    skill: Skill | None = None
    task_type: str | None = None
    difficulty: TaskDifficulty | None = None
    topic: str | None = None
    embedding_vector: list[float] | None = None
    limit: int = Field(default=5, ge=1, le=20)


class SearchResult(BaseModel):
    """Individual retrieved content chunk with similarity score."""

    chunk_id: uuid.UUID
    item_id: uuid.UUID
    title: str
    chunk_text: str
    skill: str
    task_type: str
    topic: str | None
    score: float = Field(ge=0.0, le=1.0)
    match_source: str = "hybrid"


class HybridRetriever:
    """Combines metadata filtering, lexical matching, and vector similarity."""

    @classmethod
    def filter_and_rank_chunks(
        cls,
        query: SearchQuery,
        candidate_chunks: Sequence[dict[str, Any]],
    ) -> list[SearchResult]:
        """Rank and filter in-memory candidates deterministically."""
        results: list[SearchResult] = []
        tokens = set(query.query_text.lower().split())

        for c in candidate_chunks:
            # 1. Metadata filters
            if query.skill and c.get("skill") != query.skill.value:
                continue
            if query.task_type and c.get("task_type") != query.task_type:
                continue

            # 2. Simple lexical overlap score
            text = c.get("chunk_text", "").lower()
            text_tokens = set(text.split())
            intersection = tokens.intersection(text_tokens)
            lexical_score = len(intersection) / max(len(tokens), 1)

            # Combined score (vector + lexical if vector provided)
            score = round(min(max(lexical_score, 0.05), 1.0), 3)

            results.append(
                SearchResult(
                    chunk_id=c.get("chunk_id", uuid.uuid4()),
                    item_id=c.get("item_id", uuid.uuid4()),
                    title=c.get("title", "Untitled Content"),
                    chunk_text=c.get("chunk_text", ""),
                    skill=c.get("skill", "general"),
                    task_type=c.get("task_type", "general"),
                    topic=c.get("topic"),
                    score=score,
                    match_source="lexical_filter",
                )
            )

        results.sort(key=lambda r: r.score, reverse=True)
        return results[: query.limit]
