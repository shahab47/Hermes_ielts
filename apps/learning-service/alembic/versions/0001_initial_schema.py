"""Initial database schema for IELTS learning service.

Revision ID: 0001_initial_schema
Revises:
Create Date: 2026-09-19 19:00:00
"""

from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial_schema"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Enable PostgreSQL extensions
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "vector"')
    op.execute('CREATE EXTENSION IF NOT EXISTS "pg_trgm"')

    # 1. learners
    op.create_table(
        "learners",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("external_user_id", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("target_exam", sa.String(50), nullable=False, server_default="IELTS Academic"),
        sa.Column("target_overall_band", sa.Float(), nullable=True),
        sa.Column("exam_date", sa.DateTime(timezone=True), nullable=True),
        sa.Column("timezone", sa.String(50), nullable=False, server_default="UTC"),
        sa.Column("baseline_status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 2. skill_states
    op.create_table(
        "skill_states",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("skill", sa.String(50), nullable=False),
        sa.Column("estimated_band", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("recent_score", sa.Float(), nullable=True),
        sa.Column("rolling_score", sa.Float(), nullable=True),
        sa.Column("trend", sa.String(50), nullable=False, server_default="insufficient_data"),
        sa.Column("practice_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_practiced_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_assessed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.UniqueConstraint("learner_id", "skill", name="uq_learner_skill"),
    )

    # 3. tasks
    op.create_table(
        "tasks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("skill", sa.String(50), nullable=False, index=True),
        sa.Column("task_type", sa.String(100), nullable=False, index=True),
        sa.Column("difficulty", sa.String(50), nullable=False),
        sa.Column("topic", sa.String(200), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("provenance", sa.Text(), nullable=True),
        sa.Column("content_json", postgresql.JSONB(), nullable=False),
        sa.Column("answer_json", postgresql.JSONB(), nullable=True),
        sa.Column("rubric_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 4. attempts
    op.create_table(
        "attempts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("skill", sa.String(50), nullable=False, index=True),
        sa.Column("task_type", sa.String(100), nullable=False),
        sa.Column("prompt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("tasks.id"), nullable=True),
        sa.Column("raw_input", sa.Text(), nullable=True),
        sa.Column("normalized_input", sa.Text(), nullable=True),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 5. assessments
    op.create_table(
        "assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("attempts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("estimated_band", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evaluator_version", sa.String(100), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 6. criterion_scores
    op.create_table(
        "criterion_scores",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "assessment_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("assessments.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("criterion", sa.String(100), nullable=False),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("evidence_json", postgresql.JSONB(), nullable=False),
    )

    # 7. error_events
    op.create_table(
        "error_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("attempts.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("subtype", sa.String(100), nullable=False, index=True),
        sa.Column("evidence_text", sa.Text(), nullable=False),
        sa.Column("severity", sa.String(50), nullable=False),
        sa.Column("recurrence_group", sa.String(200), nullable=True),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 8. weaknesses
    op.create_table(
        "weaknesses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("category", sa.String(50), nullable=False, index=True),
        sa.Column("subtype", sa.String(100), nullable=False, index=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="hypothesis"),
        sa.Column("recurrence_rate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("impact_estimate", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("confidence", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("priority", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("first_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 9. learning_items
    op.create_table(
        "learning_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("item_type", sa.String(50), nullable=False, index=True),
        sa.Column("canonical_form", sa.String(500), nullable=False),
        sa.Column("meaning", sa.Text(), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("fsrs_state_json", postgresql.JSONB(), nullable=True),
        sa.Column("mastery_state", sa.String(50), nullable=False, server_default="new"),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True, index=True),
        sa.Column("stability", sa.Float(), nullable=True),
        sa.Column("difficulty", sa.Float(), nullable=True),
        sa.Column("reps", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("lapses", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 10. review_events
    op.create_table(
        "review_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learning_item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learning_items.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("rating", sa.Integer(), nullable=False),
        sa.Column("review_type", sa.String(50), nullable=False),
        sa.Column("response_time_ms", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 11. practice_sessions
    op.create_table(
        "practice_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("planned_minutes", sa.Integer(), nullable=True),
        sa.Column("actual_minutes", sa.Integer(), nullable=True),
        sa.Column("objectives_json", postgresql.JSONB(), nullable=True),
        sa.Column("completion_status", sa.String(50), nullable=False, server_default="planned"),
    )

    # 12. recommendations
    op.create_table(
        "recommendations",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("recommendation_type", sa.String(50), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
        sa.Column("priority", sa.Float(), nullable=False, server_default="0.0"),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="active"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 13. audio_assets
    op.create_table(
        "audio_assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "attempt_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("attempts.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("storage_uri", sa.String(1000), nullable=False),
        sa.Column("duration_ms", sa.Integer(), nullable=True),
        sa.Column("sample_rate", sa.Integer(), nullable=True),
        sa.Column("codec", sa.String(50), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("timestamps_json", postgresql.JSONB(), nullable=True),
        sa.Column("acoustic_metrics_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 14. learner_events
    op.create_table(
        "learner_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "learner_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("learners.id", ondelete="CASCADE"),
            nullable=False,
            index=True,
        ),
        sa.Column("event_type", sa.String(100), nullable=False, index=True),
        sa.Column("payload_json", postgresql.JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now(), index=True),
    )

    # 15. content_items
    op.create_table(
        "content_items",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source", sa.String(50), nullable=False),
        sa.Column("author_or_organization", sa.String(200), nullable=True),
        sa.Column("reference_url", sa.String(1000), nullable=True),
        sa.Column("license_provenance", sa.String(200), nullable=False, server_default="public_domain_or_open"),
        sa.Column("skill", sa.String(50), nullable=False, index=True),
        sa.Column("task_type", sa.String(100), nullable=False, index=True),
        sa.Column("level", sa.String(50), nullable=False, server_default="B2-C1"),
        sa.Column("topic", sa.String(200), nullable=True, index=True),
        sa.Column("difficulty", sa.String(50), nullable=False, server_default="intermediate"),
        sa.Column("content_text", sa.Text(), nullable=False),
        sa.Column("metadata_json", postgresql.JSONB(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # 16. content_chunks
    op.create_table(
        "content_chunks",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("uuid_generate_v4()")),
        sa.Column(
            "item_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("content_items.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("token_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("content_chunks")
    op.drop_table("content_items")
    op.drop_table("learner_events")
    op.drop_table("audio_assets")
    op.drop_table("recommendations")
    op.drop_table("practice_sessions")
    op.drop_table("review_events")
    op.drop_table("learning_items")
    op.drop_table("weaknesses")
    op.drop_table("error_events")
    op.drop_table("criterion_scores")
    op.drop_table("assessments")
    op.drop_table("attempts")
    op.drop_table("tasks")
    op.drop_table("skill_states")
    op.drop_table("learners")
