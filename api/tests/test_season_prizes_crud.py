# ==============================================================================
# FILE: api/tests/test_season_prizes_crud.py
# ==============================================================================
# This file contains unit tests for the season_prizes CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import Actor, PrizeCreate, RankCreate, SeasonCreate, UserCreate

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


def create_test_prize():
    """Helper to create a prize model instance."""
    return models.Prize(description="Test Prize")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_add_prize_to_season_rank(async_db_session):
    """Tests that a prize can be successfully associated with a season rank."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()

    async_db_session.add_all([admin, season, rank, prize])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)

    # Create the SeasonRank link that will have a prize added to it
    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    # Refresh all objects after commits to ensure their state is loaded
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(prize)

    new_link = await crud.add_prize_to_season_rank(
        db=async_db_session, season_rank_id=season_rank.id, prize_id=prize.id
    )

    assert new_link is not None
    assert new_link.season_rank_id == season_rank.id
    assert new_link.prize_id == prize.id


@pytest.mark.asyncio
async def test_get_prizes_for_season_rank(async_db_session):
    """Tests retrieving all prizes associated with a season rank."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()
    prize1 = create_test_prize()
    prize2 = models.Prize(description="Another Prize")

    async_db_session.add_all([admin, season, rank, prize1, prize2])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize1)
    await async_db_session.refresh(prize2)

    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()

    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize1)
    await async_db_session.refresh(prize2)

    await crud.add_prize_to_season_rank(
        db=async_db_session, season_rank_id=season_rank.id, prize_id=prize1.id
    )
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize1)
    await async_db_session.refresh(prize2)
    await crud.add_prize_to_season_rank(
        db=async_db_session, season_rank_id=season_rank.id, prize_id=prize2.id
    )
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize1)
    await async_db_session.refresh(prize2)

    prizes_for_rank = await crud.get_prizes_for_season_rank(
        db=async_db_session, season_rank_id=season_rank.id
    )

    assert len(prizes_for_rank) == 2
    assert prizes_for_rank[0].prize.description == "Test Prize"


@pytest.mark.asyncio
async def test_remove_prize_from_season_rank(async_db_session):
    """Tests that a prize can be disassociated from a season rank."""
    admin = create_test_admin()
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()

    async_db_session.add_all([admin, season, rank, prize])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)

    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()

    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)

    link_to_delete = await crud.add_prize_to_season_rank(
        db=async_db_session, season_rank_id=season_rank.id, prize_id=prize.id
    )
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)

    await crud.remove_prize_from_season_rank(
        db=async_db_session, season_prize=link_to_delete
    )
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)

    prizes_for_rank = await crud.get_prizes_for_season_rank(
        db=async_db_session, season_rank_id=season_rank.id
    )
    assert len(prizes_for_rank) == 0
