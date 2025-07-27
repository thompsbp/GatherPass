# ==============================================================================
# FILE: api/tests/test_season_items_crud.py
# ==============================================================================
# This file contains unit tests for the season_items CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models  # Import models directly
import pytest
from schemas import (
    Actor,
    ItemCreate,
    SeasonCreate,
    SeasonItemCreate,
    SeasonItemUpdate,
    UserCreate,
)

# --- Helper functions now create model instances directly, without using CRUD ---


def create_test_admin():
    """Helper to create an admin user model instance."""
    return models.User(
        discord_id=999,
        in_game_name="Test Admin",
        lodestone_id="999",
        admin=True,
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


def create_test_item():
    """Helper to create an item model instance."""
    return models.Item(name="Test Item", lodestone_id="12345")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_add_item_to_season(async_db_session):
    """Tests that an item can be successfully associated with a season."""
    admin = create_test_admin()
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item_data = SeasonItemCreate(item_id=item.id, point_value=100)

    new_link = await crud.add_item_to_season(
        db=async_db_session, season_id=season.id, item_data=season_item_data
    )

    assert new_link is not None
    assert new_link.season_id == season.id
    assert new_link.item_id == item.id


@pytest.mark.asyncio
async def test_add_duplicate_item_to_season(async_db_session):
    """Tests that adding the same item to a season twice returns None."""
    admin = create_test_admin()
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item_data = SeasonItemCreate(item_id=item.id, point_value=100)

    await crud.add_item_to_season(
        db=async_db_session, season_id=season.id, item_data=season_item_data
    )

    duplicate_link = await crud.add_item_to_season(
        db=async_db_session, season_id=season.id, item_data=season_item_data
    )

    assert duplicate_link is None


@pytest.mark.asyncio
async def test_get_items_for_season(async_db_session):
    """Tests retrieving all items associated with a season."""
    admin = create_test_admin()
    season = create_test_season()
    item1 = create_test_item()
    item2 = models.Item(name="Another Item", lodestone_id="54321")

    async_db_session.add_all([admin, season, item1, item2])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(item1)
    await async_db_session.refresh(item2)

    await crud.add_item_to_season(
        db=async_db_session,
        season_id=season.id,
        item_data=SeasonItemCreate(item_id=item1.id, point_value=50),
    )

    await async_db_session.refresh(season)
    await async_db_session.refresh(item2)

    await crud.add_item_to_season(
        db=async_db_session,
        season_id=season.id,
        item_data=SeasonItemCreate(item_id=item2.id, point_value=75),
    )

    items_in_season = await crud.get_items_for_season(
        db=async_db_session, season_id=season.id
    )

    assert len(items_in_season) == 2
    assert items_in_season[0].item.name == "Test Item"


@pytest.mark.asyncio
async def test_update_season_item(async_db_session):
    """Tests updating the point value of an item in a season."""
    admin = create_test_admin()
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item_data = SeasonItemCreate(item_id=item.id, point_value=100)
    link_to_update = await crud.add_item_to_season(
        db=async_db_session, season_id=season.id, item_data=season_item_data
    )

    update_data = SeasonItemUpdate(point_value=250)
    updated_link = await crud.update_season_item(
        db=async_db_session, season_item=link_to_update, update_data=update_data
    )

    assert updated_link.point_value == 250


@pytest.mark.asyncio
async def test_remove_item_from_season(async_db_session):
    """Tests that an item can be disassociated from a season."""
    admin = create_test_admin()
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item_data = SeasonItemCreate(item_id=item.id, point_value=100)
    link_to_delete = await crud.add_item_to_season(
        db=async_db_session, season_id=season.id, item_data=season_item_data
    )

    await crud.remove_item_from_season(db=async_db_session, season_item=link_to_delete)

    await async_db_session.refresh(season)

    items_in_season = await crud.get_items_for_season(
        db=async_db_session, season_id=season.id
    )
    assert len(items_in_season) == 0
