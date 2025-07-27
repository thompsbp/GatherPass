# ==============================================================================
# FILE: api/tests/test_season_ranks_crud.py
# ==============================================================================
# This file contains unit tests for the season_ranks CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import SeasonRankCreate, SeasonRankUpdate

# --- Helper functions create model instances directly, without using CRUD ---


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


def create_test_rank():
    """Helper to create a rank model instance."""
    return models.Rank(name="Test Rank", badge_url="http://example.com/test.png")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_add_rank_to_season(async_db_session):
    """Tests that a rank can be successfully associated with a season."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, season, rank])
    await async_db_session.commit()

    # Refresh objects after commit to load their state (IDs, etc.)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    rank_data = SeasonRankCreate(rank_id=rank.id, number=1, required_points=100)

    new_link = await crud.add_rank_to_season(
        db=async_db_session, season_id=season.id, rank_data=rank_data
    )

    assert new_link is not None
    assert new_link.season_id == season.id
    assert new_link.rank_id == rank.id
    assert new_link.required_points == 100


@pytest.mark.asyncio
async def test_add_duplicate_rank_to_season(async_db_session):
    """Tests that adding the same rank to a season twice returns None."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    rank_data = SeasonRankCreate(rank_id=rank.id, number=1, required_points=100)

    # First time should succeed
    await crud.add_rank_to_season(
        db=async_db_session, season_id=season.id, rank_data=rank_data
    )

    # Second time should fail and return None
    duplicate_link = await crud.add_rank_to_season(
        db=async_db_session, season_id=season.id, rank_data=rank_data
    )

    assert duplicate_link is None


@pytest.mark.asyncio
async def test_get_ranks_for_season(async_db_session):
    """Tests retrieving all ranks associated with a season."""
    admin = create_test_admin()
    season = create_test_season()
    rank1 = create_test_rank()
    rank2 = models.Rank(name="Another Rank")

    async_db_session.add_all([admin, season, rank1, rank2])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(rank1)
    await async_db_session.refresh(rank2)

    await crud.add_rank_to_season(
        db=async_db_session,
        season_id=season.id,
        rank_data=SeasonRankCreate(rank_id=rank1.id, number=1, required_points=100),
    )

    await async_db_session.refresh(season)
    await async_db_session.refresh(rank2)

    await crud.add_rank_to_season(
        db=async_db_session,
        season_id=season.id,
        rank_data=SeasonRankCreate(rank_id=rank2.id, number=2, required_points=500),
    )

    ranks_in_season = await crud.get_ranks_for_season(
        db=async_db_session, season_id=season.id
    )

    assert len(ranks_in_season) == 2
    assert ranks_in_season[0].rank.name == "Test Rank"


@pytest.mark.asyncio
async def test_update_season_rank(async_db_session):
    """Tests updating the requirements of a rank in a season."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    rank_data = SeasonRankCreate(rank_id=rank.id, number=1, required_points=100)
    link_to_update = await crud.add_rank_to_season(
        db=async_db_session, season_id=season.id, rank_data=rank_data
    )

    await async_db_session.refresh(link_to_update)

    update_data = SeasonRankUpdate(required_points=250)
    updated_link = await crud.update_season_rank(
        db=async_db_session, season_rank=link_to_update, update_data=update_data
    )

    assert updated_link.required_points == 250


@pytest.mark.asyncio
async def test_remove_rank_from_season(async_db_session):
    """Tests that a rank can be disassociated from a season."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    rank_data = SeasonRankCreate(rank_id=rank.id, number=1, required_points=100)
    link_to_delete = await crud.add_rank_to_season(
        db=async_db_session, season_id=season.id, rank_data=rank_data
    )

    await crud.remove_rank_from_season(db=async_db_session, season_rank=link_to_delete)

    await async_db_session.refresh(season)

    ranks_in_season = await crud.get_ranks_for_season(
        db=async_db_session, season_id=season.id
    )
    assert len(ranks_in_season) == 0
