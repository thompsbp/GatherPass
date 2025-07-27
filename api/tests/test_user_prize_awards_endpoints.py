# ==============================================================================
# FILE: api/tests/test_user_prize_awards_endpoints.py
# ==============================================================================
# This file contains the integration test suite for the user prize award endpoints.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from auth import create_access_token
from schemas import UserCreate

# --- Helper functions create model instances directly ---


def create_test_user(discord_id, is_admin=False, is_verified=True):
    """Helper to create a user model instance."""
    status = "pending"
    if is_verified:
        status = "verified"
    return models.User(
        discord_id=discord_id,
        in_game_name=f"TestUser{discord_id}",
        lodestone_id=str(discord_id),
        admin=is_admin,
        status=status,
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
async def test_create_user_prize_award_success(test_client, async_db_session):
    """
    - GIVEN: An admin, a user, and a complete prize setup exist.
    - WHEN: The admin creates a prize award for the user.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()

    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    season_prize = models.SeasonPrize(season_rank=season_rank, prize=prize)

    async_db_session.add_all(
        [admin, user, season, rank, prize, season_rank, season_prize]
    )
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season_prize)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.post(
        f"/users/{user.id}/prize-awards/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user.id, "season_prize_id": season_prize.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == user.id


@pytest.mark.asyncio
async def test_get_awards_for_user_success(test_client, async_db_session):
    """
    - GIVEN: A user has been awarded a prize.
    - WHEN: That same user requests their list of awarded prizes.
    - THEN: The request should succeed with a 200 OK status.
    """
    user = create_test_user(3)
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()
    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    season_prize = models.SeasonPrize(season_rank=season_rank, prize=prize)
    award = models.UserPrizeAward(user=user, season_prize=season_prize)

    async_db_session.add_all(
        [user, season, rank, prize, season_rank, season_prize, award]
    )
    await async_db_session.commit()
    await async_db_session.refresh(user)

    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        f"/users/{user.id}/prize-awards/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_get_awards_for_user_fail_unauthorized(test_client, async_db_session):
    """
    - GIVEN: Two regular users exist.
    - WHEN: User A tries to get the list of prizes for User B.
    - THEN: The request should fail with a 403 Forbidden error.
    """
    user_a = create_test_user(4)
    user_b = create_test_user(5)

    async_db_session.add_all([user_a, user_b])
    await async_db_session.commit()
    await async_db_session.refresh(user_a)
    await async_db_session.refresh(user_b)

    token = create_access_token(data={"sub": user_a.uuid})

    response = await test_client.get(
        f"/users/{user_b.id}/prize-awards/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_update_award_success(test_client, async_db_session):
    """
    - GIVEN: A user has been awarded a prize.
    - WHEN: An admin updates the award to mark it as delivered.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(6, is_admin=True)
    user = create_test_user(7)
    season = create_test_season()
    rank = create_test_rank()
    prize = create_test_prize()
    season_rank = models.SeasonRank(
        season=season, rank=rank, number=1, required_points=100
    )
    season_prize = models.SeasonPrize(season_rank=season_rank, prize=prize)
    award = models.UserPrizeAward(user=user, season_prize=season_prize)

    async_db_session.add_all(
        [admin, user, season, rank, prize, season_rank, season_prize, award]
    )
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    await async_db_session.refresh(award)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.patch(
        f"/prize-awards/{award.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"delivered": True, "notes": "Delivered in person."},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["delivered"] is True
