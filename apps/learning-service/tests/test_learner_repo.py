"""Unit tests for LearnerRepository."""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, MagicMock

import pytest

from app.models.learner import Learner, Skill, SkillState
from app.repositories.learner_repo import LearnerRepository
from app.schemas.learner import LearnerCreate


@pytest.fixture
def mock_session() -> AsyncMock:
    session = AsyncMock()
    session.add = MagicMock()
    session.flush = AsyncMock()
    return session


@pytest.mark.asyncio
async def test_create_learner(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    data = LearnerCreate(
        external_user_id="user_123",
        target_exam="IELTS Academic",
        target_overall_band=7.5,
        timezone="UTC",
    )

    learner = await repo.create(data)

    assert learner.external_user_id == "user_123"
    assert learner.target_overall_band == 7.5
    mock_session.add.assert_called_once_with(learner)
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_id(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    test_id = uuid.uuid4()
    mock_learner = Learner(id=test_id, external_user_id="user_123")
    mock_session.get.return_value = mock_learner

    result = await repo.get_by_id(test_id)

    assert result == mock_learner
    mock_session.get.assert_awaited_once_with(Learner, test_id)


@pytest.mark.asyncio
async def test_get_by_external_id(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    mock_learner = Learner(id=uuid.uuid4(), external_user_id="user_456")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_learner
    mock_session.execute.return_value = mock_result

    result = await repo.get_by_external_id("user_456")

    assert result == mock_learner
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_with_skill_states(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    test_id = uuid.uuid4()
    mock_learner = Learner(id=test_id, external_user_id="user_789")
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_learner
    mock_session.execute.return_value = mock_result

    result = await repo.get_with_skill_states(test_id)

    assert result == mock_learner
    mock_session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_skill_state(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    test_id = uuid.uuid4()
    mock_state = SkillState(learner_id=test_id, skill=Skill.WRITING, estimated_band=6.5)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = mock_state
    mock_session.execute.return_value = mock_result

    result = await repo.get_skill_state(test_id, Skill.WRITING)

    assert result == mock_state


@pytest.mark.asyncio
async def test_upsert_skill_state_create(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    test_id = uuid.uuid4()
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute.return_value = mock_result

    state = await repo.upsert_skill_state(test_id, Skill.SPEAKING, estimated_band=7.0, confidence=0.8)

    assert state.learner_id == test_id
    assert state.skill == Skill.SPEAKING
    assert state.estimated_band == 7.0
    mock_session.add.assert_called_once()
    mock_session.flush.assert_awaited_once()


@pytest.mark.asyncio
async def test_upsert_skill_state_update(mock_session: AsyncMock) -> None:
    repo = LearnerRepository(mock_session)
    test_id = uuid.uuid4()
    existing_state = SkillState(learner_id=test_id, skill=Skill.SPEAKING, estimated_band=6.0, confidence=0.5)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = existing_state
    mock_session.execute.return_value = mock_result

    state = await repo.upsert_skill_state(test_id, Skill.SPEAKING, estimated_band=7.5, confidence=0.9)

    assert state.estimated_band == 7.5
    assert state.confidence == 0.9
    mock_session.flush.assert_awaited_once()
