# ==============================================================================
# FILE: api/tests/test_user_prize_awards_crud.py
# ==============================================================================
# This file contains unit tests for the user_prize_awards CRUD functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import (
    Actor,
    PrizeCreate,
    RankCreate,
    SeasonCreate,
    UserCreate,
    UserPrizeAwardCreate,
    UserPrizeAwardUpdate,
)

# --- Helper functions create model instances directly ---


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
    return models.Rank(name="Test Rank")


def create_test_prize():
    """Helper to create a prize model instance."""
    return models.Prize(description="Test Prize")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_user_prize_award(async_db_session):
    """Tests that a prize award record can be created successfully."""
    user = create_test_user(1)
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()

    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    season_prize = models.SeasonPrize(season_rank=season_rank, prize=prize)

    async_db_session.add_all([user, season, rank, prize, season_rank, season_prize])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season_prize)

    award_data = UserPrizeAwardCreate(user_id=user.id, season_prize_id=season_prize.id)

    new_award = await crud.create_user_prize_award(
        db=async_db_session, award_data=award_data
    )

    assert new_award is not None
    assert new_award.user_id == user.id
    assert new_award.season_prize_id == season_prize.id


@pytest.mark.asyncio
async def test_get_awards_for_user(async_db_session):
    """Tests retrieving all prize awards for a specific user."""
    user = create_test_user(1)
    season = create_test_season()
    rank = create_test_rank()
    prize1 = create_test_prize()
    prize2 = models.Prize(description="Another Prize")

    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    sp1 = models.SeasonPrize(season_rank=season_rank, prize=prize1)
    sp2 = models.SeasonPrize(season_rank=season_rank, prize=prize2)

    award1 = models.UserPrizeAward(user=user, season_prize=sp1)
    award2 = models.UserPrizeAward(user=user, season_prize=sp2)

    async_db_session.add_all(
        [user, season, rank, prize1, prize2, season_rank, sp1, sp2, award1, award2]
    )
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize1)
    await async_db_session.refresh(prize2)
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(sp1)
    await async_db_session.refresh(sp2)
    await async_db_session.refresh(award1)
    await async_db_session.refresh(award2)

    user_awards = await crud.get_awards_for_user(db=async_db_session, user_id=user.id)

    assert len(user_awards) == 2


@pytest.mark.asyncio
async def test_update_user_prize_award(async_db_session):
    """Tests updating an award to mark it as delivered."""
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()

    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    season_prize = models.SeasonPrize(season_rank=season_rank, prize=prize)
    award_to_update = models.UserPrizeAward(user=user, season_prize=season_prize)

    async_db_session.add_all(
        [admin, user, season, rank, prize, season_rank, season_prize, award_to_update]
    )
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(prize)
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season_prize)
    await async_db_session.refresh(award_to_update)

    update_data = UserPrizeAwardUpdate(delivered=True, notes="Hand-delivered")

    updated_award = await crud.update_user_prize_award(
        db=async_db_session,
        award=award_to_update,
        update_data=update_data,
        actor=admin,
    )

    await async_db_session.refresh(admin)
    assert updated_award.delivered is True
    assert updated_award.delivered_by == admin.discord_id
