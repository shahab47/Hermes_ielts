"""Audio asset model."""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from app.models.attempt import Attempt

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, UUIDPrimaryKeyMixin


class AudioAsset(Base, UUIDPrimaryKeyMixin):
    """Audio recording from a speaking attempt."""

    __tablename__ = "audio_assets"

    attempt_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("attempts.id"), nullable=False, unique=True
    )
    storage_uri: Mapped[str] = mapped_column(String(1000), nullable=False)
    duration_ms: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sample_rate: Mapped[int | None] = mapped_column(Integer, nullable=True)
    codec: Mapped[str | None] = mapped_column(String(50), nullable=True)
    transcript: Mapped[str | None] = mapped_column(Text, nullable=True)
    timestamps_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    acoustic_metrics_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    attempt: Mapped[Attempt] = relationship(back_populates="audio_asset")
