"""Repository for learner data access."""

from __future__ import annotations

import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.learner import Learner, Skill, SkillState
from app.schemas.learner import LearnerCreate


class LearnerRepository:
    """Data access layer for learner operations."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, data: LearnerCreate) -> Learner:
        """Create a new learner."""
        learner = Learner(
            external_user_id=data.external_user_id,
            target_exam=data.target_exam,
            target_overall_band=data.target_overall_band,
            exam_date=data.exam_date,
            timezone=data.timezone,
        )
        self._session.add(learner)
        await self._session.flush()
        return learner

    async def get_by_id(self, learner_id: uuid.UUID) -> Learner | None:
        """Get a learner by ID."""
        return await self._session.get(Learner, learner_id)

    async def get_by_external_id(self, external_user_id: str) -> Learner | None:
        """Get a learner by external user ID."""
        result = await self._session.execute(select(Learner).where(Learner.external_user_id == external_user_id))
        return result.scalar_one_or_none()

    async def get_with_skill_states(self, learner_id: uuid.UUID) -> Learner | None:
        """Get a learner with all skill states loaded."""
        result = await self._session.execute(
            select(Learner).where(Learner.id == learner_id).options(selectinload(Learner.skill_states))
        )
        return result.scalar_one_or_none()

    async def get_skill_state(self, learner_id: uuid.UUID, skill: Skill) -> SkillState | None:
        """Get a specific skill state."""
        result = await self._session.execute(
            select(SkillState).where(SkillState.learner_id == learner_id, SkillState.skill == skill)
        )
        return result.scalar_one_or_none()

    async def upsert_skill_state(self, learner_id: uuid.UUID, skill: Skill, **kwargs) -> SkillState:
        """Create or update a skill state."""
        state = await self.get_skill_state(learner_id, skill)
        if state is None:
            state = SkillState(learner_id=learner_id, skill=skill, **kwargs)
            self._session.add(state)
        else:
            for key, value in kwargs.items():
                setattr(state, key, value)
        await self._session.flush()
        return state
