"""Repository for Question Bank and Question Sets (Phase P14)."""

from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.domain.question_bank import Question, QuestionSet
from app.models.learner import Skill
from app.models.question_bank import QuestionModel, QuestionSetModel
from app.models.task import TaskDifficulty


class QuestionRepository:
    """Data access layer for Question Bank items and collections."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save_question(self, question: Question) -> QuestionModel:
        """Persists a domain Question into QuestionModel."""
        model = QuestionModel(
            id=question.id,
            question_set_id=question.question_set_id,
            skill=question.skill,
            task_type=question.task_type,
            question_type=question.question_type,
            difficulty=question.difficulty,
            cefr=question.cefr.value if question.cefr else None,
            prompt=question.prompt,
            instructions=question.instructions,
            options_json=[opt.model_dump() for opt in question.options] if question.options else None,
            answer_json=question.answer.model_dump(),
            explanation_json=question.explanation.model_dump(),
            media_json=[m.model_dump() for m in question.media] if question.media else None,
            tags=question.tags,
            provenance_json=question.provenance.model_dump(mode="json"),
            review_status=question.review_status.value,
            quality_score=question.quality_score,
            version=question.version,
        )
        self._session.add(model)
        await self._session.flush()
        return model

    async def get_by_id(self, question_id: uuid.UUID) -> QuestionModel | None:
        """Retrieve question by UUID."""
        return await self._session.get(QuestionModel, question_id)

    async def search_questions(
        self,
        skill: Skill | None = None,
        question_type: str | None = None,
        difficulty: TaskDifficulty | None = None,
        limit: int = 50,
    ) -> Sequence[QuestionModel]:
        """Filtered search across question bank."""
        stmt = select(QuestionModel)
        if skill:
            stmt = stmt.where(QuestionModel.skill == skill)
        if question_type:
            stmt = stmt.where(QuestionModel.question_type == question_type)
        if difficulty:
            stmt = stmt.where(QuestionModel.difficulty == difficulty)
        stmt = stmt.order_by(QuestionModel.created_at.desc()).limit(limit)
        result = await self._session.execute(stmt)
        return result.scalars().all()

    async def save_question_set(self, question_set: QuestionSet) -> QuestionSetModel:
        """Persists a QuestionSet collection and associated questions."""
        set_model = QuestionSetModel(
            id=question_set.id,
            title=question_set.title,
            skill=question_set.skill,
            task_type=question_set.task_type,
            description=question_set.description,
            time_limit_minutes=question_set.time_limit_minutes,
            passage_or_transcript=question_set.passage_or_transcript,
            provenance_json=question_set.provenance.model_dump(mode="json"),
            version=question_set.version,
        )
        self._session.add(set_model)
        await self._session.flush()

        for q in question_set.questions:
            q.question_set_id = set_model.id
            await self.save_question(q)

        await self._session.flush()
        return set_model

    async def get_question_set_by_id(self, set_id: uuid.UUID) -> QuestionSetModel | None:
        """Retrieve QuestionSet with eagerly loaded questions."""
        stmt = (
            select(QuestionSetModel)
            .where(QuestionSetModel.id == set_id)
            .options(selectinload(QuestionSetModel.questions))
        )
        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()
