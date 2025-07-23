# ==============================================================================
# FILE: api/tests/test_seasons_crud.py
# ==============================================================================
# This file contains unit tests for the season-related functions in crud/seasons.py.

from datetime import datetime, timedelta, timezone  # Import datetime tools

import crud
import models
import pytest
from schemas import Actor, SeasonCreate, SeasonUpdate, UserCreate

# A mock actor for audit purposes
mock_actor = Actor(id="test_runner", is_bot=True)


# Helper to create a user to act as the 'actor' for creating seasons
async def create_test_admin(db_session):
    """Creates a verified admin user for testing purposes."""
    user_data = UserCreate(
        discord_id=999, in_game_name="Test Admin", lodestone_id="999"
    )
    user = await crud.create_user(db=db_session, user_data=user_data, actor=mock_actor)
    user.admin = True
    user.status = "verified"
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_season(async_db_session):
    """Tests that a season can be created successfully."""
    admin_user = await create_test_admin(async_db_session)
    season_data = SeasonCreate(
        name="Inaugural Season",
        number=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )

    new_season = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    assert new_season is not None
    assert new_season.name == "Inaugural Season"


@pytest.mark.asyncio
async def test_get_season_by_id(async_db_session):
    """Tests retrieving a season by its ID."""
    admin_user = await create_test_admin(async_db_session)
    season_data = SeasonCreate(
        name="Season To Find",
        number=2,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    created_season = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    found_season = await crud.get_season_by_id(
        db=async_db_session, season_id=created_season.id
    )
    assert found_season is not None
    assert found_season.name == "Season To Find"


@pytest.mark.asyncio
async def test_get_seasons(async_db_session):
    """Tests retrieving a list of all seasons."""
    admin_user = await create_test_admin(async_db_session)
    await crud.create_season(
        db=async_db_session,
        season_data=SeasonCreate(
            name="Season A",
            number=10,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
        ),
        actor=admin_user,
    )
    await crud.create_season(
        db=async_db_session,
        season_data=SeasonCreate(
            name="Season B",
            number=11,
            start_date=datetime.now(timezone.utc),
            end_date=datetime.now(timezone.utc) + timedelta(days=30),
        ),
        actor=admin_user,
    )

    all_seasons = await crud.get_seasons(db=async_db_session)
    assert len(all_seasons) == 2


@pytest.mark.asyncio
async def test_update_season(async_db_session):
    """Tests updating an existing season's details."""
    admin_user = await create_test_admin(async_db_session)
    season_data = SeasonCreate(
        name="Original Name",
        number=5,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    season_to_update = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    update_data = SeasonUpdate(name="Updated Name")
    updated_season = await crud.update_season(
        db=async_db_session,
        season=season_to_update,
        update_data=update_data,
        actor=admin_user,
    )

    assert updated_season.name == "Updated Name"


@pytest.mark.asyncio
async def test_delete_season(async_db_session):
    """Tests that a season can be deleted successfully."""
    admin_user = await create_test_admin(async_db_session)
    season_data = SeasonCreate(
        name="To Be Deleted",
        number=99,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    season_to_delete = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )
    season_id = season_to_delete.id

    await crud.delete_season(db=async_db_session, season=season_to_delete)

    deleted_season = await crud.get_season_by_id(
        db=async_db_session, season_id=season_id
    )
    assert deleted_season is None
