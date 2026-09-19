"""Content schema and pgvector embeddings model for RAG (Phase 8)."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector
from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDPrimaryKeyMixin
from app.models.learner import Skill
from app.models.task import TaskDifficulty, TaskSource


class ContentItem(Base, UUIDPrimaryKeyMixin, TimestampMixin):
    """Pedagogical content entity (rubrics, exercises, guides, prompts)."""

    __tablename__ = "content_items"

    title: Mapped[str] = mapped_column(String(500), nullable=False)
    source: Mapped[TaskSource] = mapped_column(String(50), nullable=False)
    author_or_organization: Mapped[str | None] = mapped_column(String(200), nullable=True)
    reference_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    license_provenance: Mapped[str] = mapped_column(String(200), default="public_domain_or_open")
    skill: Mapped[Skill] = mapped_column(String(50), nullable=False, index=True)
    task_type: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    level: Mapped[str] = mapped_column(String(50), default="B2-C1")
    topic: Mapped[str | None] = mapped_column(String(200), nullable=True, index=True)
    difficulty: Mapped[TaskDifficulty] = mapped_column(String(50), default=TaskDifficulty.INTERMEDIATE)
    content_text: Mapped[str] = mapped_column(Text, nullable=False)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

    # Relationships
    chunks: Mapped[list[ContentChunk]] = relationship(back_populates="item", cascade="all, delete-orphan")


class ContentChunk(Base, UUIDPrimaryKeyMixin):
    """Semantic chunk with pgvector embedding vector for hybrid retrieval."""

    __tablename__ = "content_chunks"

    item_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("content_items.id"), nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, default=0)
    # 768-dimensional or 1536-dimensional embedding vector (default 768 for fast local models like all-mpnet-base-v2)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(768), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    item: Mapped[ContentItem] = relationship(back_populates="chunks")
