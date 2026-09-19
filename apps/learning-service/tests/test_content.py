"""Unit tests for content models and hybrid retriever (Phase 10)."""

from __future__ import annotations

import uuid

from app.content.models import ContentChunk, ContentItem
from app.content.retriever import HybridRetriever, SearchQuery
from app.models.learner import Skill
from app.models.task import TaskDifficulty, TaskSource


def test_content_models_instantiation() -> None:
    item_id = uuid.uuid4()
    item = ContentItem(
        id=item_id,
        title="IELTS Writing Task 2 Assessment Criteria",
        source=TaskSource.OFFICIAL_PUBLIC,
        skill=Skill.WRITING,
        task_type="task_2",
        difficulty=TaskDifficulty.INTERMEDIATE,
        content_text="Detailed criteria for Band 7 and Band 8 descriptors...",
    )
    chunk = ContentChunk(
        id=uuid.uuid4(),
        item_id=item_id,
        chunk_index=0,
        chunk_text="Task Response criteria for Band 7 requires addressing all parts.",
        token_count=12,
        embedding=[0.1] * 768,
    )
    item.chunks.append(chunk)

    assert item.title == "IELTS Writing Task 2 Assessment Criteria"
    assert item.skill == Skill.WRITING
    assert len(item.chunks) == 1
    assert item.chunks[0].chunk_index == 0
    assert item.chunks[0].embedding is not None
    assert len(item.chunks[0].embedding) == 768


def test_hybrid_retriever_filter_and_rank() -> None:
    item_id = uuid.uuid4()
    chunk1_id = uuid.uuid4()
    chunk2_id = uuid.uuid4()
    chunk3_id = uuid.uuid4()

    candidates = [
        {
            "chunk_id": chunk1_id,
            "item_id": item_id,
            "title": "Task 2 Opinion Essay Structure",
            "chunk_text": "An opinion essay requires a clear thesis statement in the introduction.",
            "skill": "writing",
            "task_type": "task_2",
            "topic": "education",
        },
        {
            "chunk_id": chunk2_id,
            "item_id": item_id,
            "title": "Speaking Part 2 Strategy",
            "chunk_text": "Prepare notes for 1 minute before speaking for 2 minutes continuously.",
            "skill": "speaking",
            "task_type": "part_2",
            "topic": "hobbies",
        },
        {
            "chunk_id": chunk3_id,
            "item_id": item_id,
            "title": "Task 2 Problem-Solution Structure",
            "chunk_text": "Discuss causes first, followed by practical solutions and evaluations.",
            "skill": "writing",
            "task_type": "task_2",
            "topic": "environment",
        },
    ]

    # Query with skill and task_type filter
    query = SearchQuery(
        query_text="thesis statement introduction",
        skill=Skill.WRITING,
        task_type="task_2",
        limit=5,
    )

    results = HybridRetriever.filter_and_rank_chunks(query, candidates)

    assert len(results) == 2
    # Speaking candidate was filtered out
    assert all(r.skill == "writing" for r in results)
    # Candidate with matching tokens ranked first
    assert results[0].chunk_id == chunk1_id
    assert results[0].score > results[1].score


def test_hybrid_retriever_limit_cutoff() -> None:
    candidates = [
        {
            "chunk_id": uuid.uuid4(),
            "item_id": uuid.uuid4(),
            "title": f"Item {i}",
            "chunk_text": f"Vocabulary practice word list item {i}",
            "skill": "vocabulary",
            "task_type": "lexical",
        }
        for i in range(10)
    ]

    query = SearchQuery(
        query_text="vocabulary practice",
        limit=3,
    )

    results = HybridRetriever.filter_and_rank_chunks(query, candidates)
    assert len(results) == 3
