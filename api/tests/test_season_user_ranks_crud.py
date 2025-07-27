# ==============================================================================
# FILE: api/tests/test_season_user_ranks_crud.py
# ==============================================================================
# This file contains unit tests for the season_user_ranks CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import Actor, RankCreate, SeasonCreate, UserCreate

# --- Helper functions create model instances directly, without using CRUD ---


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


def create_test_rank():
    """Helper to create a rank model instance."""
    return models.Rank(name="Test Rank", badge_url="http://example.com/test.png")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_award_rank_to_user(async_db_session):
    """Tests that a rank can be successfully awarded to a user."""
    user = create_test_user(1)
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([user, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(user)

    new_award = await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=season_rank.id
    )

    assert new_award is not None
    assert new_award.user_id == user.id
    assert new_award.season_rank_id == season_rank.id


@pytest.mark.asyncio
async def test_award_duplicate_rank_to_user(async_db_session):
    """Tests that awarding the same rank to a user twice returns None."""
    user = create_test_user(1)
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([user, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=season_rank.id
    )

    await async_db_session.commit()
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    duplicate_award = await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=season_rank.id
    )

    assert duplicate_award is None


@pytest.mark.asyncio
async def test_get_user_ranks_for_season(async_db_session):
    """Tests retrieving all ranks a user has earned in a season."""
    user = create_test_user(1)
    season = create_test_season()
    rank1 = create_test_rank()
    rank2 = models.Rank(name="Another Rank")

    async_db_session.add_all([user, season, rank1, rank2])
    await async_db_session.commit()

    # --- The Definitive Fix: Refresh all objects after commit ---
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank1)
    await async_db_session.refresh(rank2)

    sr1 = models.SeasonRank(
        season_id=season.id, rank_id=rank1.id, number=1, required_points=100
    )
    sr2 = models.SeasonRank(
        season_id=season.id, rank_id=rank2.id, number=2, required_points=500
    )
    async_db_session.add_all([sr1, sr2])
    await async_db_session.commit()
    await async_db_session.refresh(sr1)
    await async_db_session.refresh(sr2)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank1)
    await async_db_session.refresh(rank2)

    await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=sr1.id
    )
    await async_db_session.refresh(sr1)
    await async_db_session.refresh(sr2)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank1)
    await async_db_session.refresh(rank2)

    await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=sr2.id
    )

    await async_db_session.refresh(sr1)
    await async_db_session.refresh(sr2)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank1)
    await async_db_session.refresh(rank2)

    awarded_ranks = await crud.get_user_ranks_for_season(
        db=async_db_session, user_id=user.id, season_id=season.id
    )

    assert len(awarded_ranks) == 2
    assert awarded_ranks[0].season_rank.rank.name == "Test Rank"
