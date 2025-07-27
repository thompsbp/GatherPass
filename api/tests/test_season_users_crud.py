# ==============================================================================
# FILE: api/tests/test_season_users_crud.py
# ==============================================================================
# This file contains unit tests for the season_users CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import Actor, SeasonCreate, UserCreate


def create_test_user(discord_id, is_admin=False):
    """Helper to create a user model instance."""
    return models.User(
        discord_id=discord_id,
        in_game_name=f"TestUser{discord_id}",
        lodestone_id=str(discord_id),
        admin=is_admin,
        status="verified",
        created_by="test",
        updated_by="test",
    )


def create_test_season():
    """Helper to create a season model instance."""
    return models.Season(
        name="Test Season",
        number=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )


# --- Test Cases ---


@pytest.mark.asyncio
async def test_register_user_for_season(async_db_session):
    """Tests that a user can be successfully registered for a season."""
    admin = create_test_user(1, is_admin=True)
    user_to_register = create_test_user(2)
    season = create_test_season()

    async_db_session.add_all([admin, user_to_register, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user_to_register)
    await async_db_session.refresh(season)

    new_link = await crud.register_user_for_season(
        db=async_db_session,
        season_id=season.id,
        user_id=user_to_register.id,
        actor=admin,
    )

    assert new_link is not None
    assert new_link.season_id == season.id
    assert new_link.user_id == user_to_register.id
    assert new_link.total_points == 0


@pytest.mark.asyncio
async def test_register_duplicate_user_for_season(async_db_session):
    """Tests that registering the same user for a season twice returns None."""
    admin = create_test_user(1, is_admin=True)
    user_to_register = create_test_user(2)
    season = create_test_season()

    async_db_session.add_all([admin, user_to_register, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user_to_register)
    await async_db_session.refresh(season)

    # First time should succeed
    await crud.register_user_for_season(
        db=async_db_session,
        season_id=season.id,
        user_id=user_to_register.id,
        actor=admin,
    )

    # Second time should fail and return None
    duplicate_link = await crud.register_user_for_season(
        db=async_db_session,
        season_id=season.id,
        user_id=user_to_register.id,
        actor=admin,
    )

    assert duplicate_link is None


@pytest.mark.asyncio
async def test_get_user_progress_in_season(async_db_session):
    """Tests retrieving a specific user's progress in a season."""
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()

    async_db_session.add_all([admin, user, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)

    await crud.register_user_for_season(
        db=async_db_session, season_id=season.id, user_id=user.id, actor=admin
    )

    progress = await crud.get_user_progress_in_season(
        db=async_db_session, season_id=season.id, user_id=user.id
    )

    assert progress is not None
    assert progress.user.discord_id == 2


@pytest.mark.asyncio
async def test_get_all_users_for_season(async_db_session):
    """Tests retrieving all users (leaderboard) for a season."""
    admin = create_test_user(1, is_admin=True)
    user1 = create_test_user(2)
    user2 = create_test_user(3)
    season = create_test_season()

    async_db_session.add_all([admin, user1, user2, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user1)
    await async_db_session.refresh(user2)
    await async_db_session.refresh(season)

    await crud.register_user_for_season(
        db=async_db_session, season_id=season.id, user_id=user1.id, actor=admin
    )

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user2)
    await async_db_session.refresh(season)

    await crud.register_user_for_season(
        db=async_db_session, season_id=season.id, user_id=user2.id, actor=admin
    )

    leaderboard = await crud.get_all_users_for_season(
        db=async_db_session, season_id=season.id
    )

    assert len(leaderboard) == 2
