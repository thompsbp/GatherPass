# ==============================================================================
# FILE: api/tests/test_season_user_ranks_endpoints.py
# ==============================================================================
# This file contains the integration test suite for awarding ranks to users.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from auth import create_access_token
from schemas import Actor, RankCreate, SeasonCreate, UserCreate

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
    return models.Rank(name="Test Rank", badge_url="http://example.com/test.png")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_award_rank_to_user_success(test_client, async_db_session):
    """
    - GIVEN: An admin, a user, a season, and a rank exist.
    - WHEN: An admin awards a season rank to the user.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(1, is_admin=True)
    user_to_award = create_test_user(2)
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, user_to_award, season, rank])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)
    await async_db_session.refresh(user_to_award)

    # Create the SeasonRank link that will be awarded
    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()

    # Refresh all objects to ensure their state is loaded after commits
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user_to_award)
    await async_db_session.refresh(season_rank)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.post(
        f"/users/{user_to_award.id}/seasons/{season.id}/ranks",
        headers={"Authorization": f"Bearer {token}"},
        json={"season_rank_id": season_rank.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == user_to_award.id
    assert data["season_rank"]["id"] == season_rank.id


@pytest.mark.asyncio
async def test_get_user_ranks_for_season_success(test_client, async_db_session):
    """
    - GIVEN: A user has been awarded a rank in a season.
    - WHEN: A registered user requests the list of awarded ranks.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(3, is_admin=True)
    user = create_test_user(4)
    season = create_test_season()
    rank = create_test_rank()

    async_db_session.add_all([admin, user, season, rank])
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(rank)

    season_rank = models.SeasonRank(
        season_id=season.id, rank_id=rank.id, number=1, required_points=100
    )
    async_db_session.add(season_rank)
    await async_db_session.commit()

    # Refresh objects after commits to ensure their state is loaded
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season_rank)

    # Admin awards the rank to the user
    await crud.award_rank_to_user(
        db=async_db_session, user_id=user.id, season_rank_id=season_rank.id
    )

    # User requests their list of ranks
    token = create_access_token(data={"sub": user.uuid})
    response = await test_client.get(
        f"/users/{user.id}/seasons/{season.id}/ranks",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["season_rank"]["rank"]["name"] == "Test Rank"
