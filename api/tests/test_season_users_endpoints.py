# ==============================================================================
# FILE: api/tests/test_season_users_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the
# nested /seasons/{season_id}/users router.

from datetime import datetime, timedelta, timezone

import crud
import models  # Import models directly
import pytest
from auth import create_access_token
from schemas import Actor, SeasonCreate, UserCreate


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


def create_test_season(number=1):
    """Helper to create a season model instance."""
    return models.Season(
        name=f"Test Season {number}",
        number=number,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )


# --- Test Cases ---


@pytest.mark.asyncio
async def test_admin_registers_another_user_success(test_client, async_db_session):
    """
    - GIVEN: An admin and a regular user exist.
    - WHEN: The admin makes a POST request to register the regular user for a season.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(1, is_admin=True)
    other_user = create_test_user(2)
    season = create_test_season()

    async_db_session.add_all([admin, other_user, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(other_user)
    await async_db_session.refresh(season)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.post(
        f"/seasons/{season.id}/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": other_user.id},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == other_user.id
    assert data["season"]["id"] == season.id


@pytest.mark.asyncio
async def test_user_registers_themself_success(test_client, async_db_session):
    """
    - GIVEN: A regular user exists.
    - WHEN: The user makes a POST request to register themself with an empty payload.
    - THEN: The request should succeed with a 200 OK status.
    """
    user = create_test_user(3)
    season = create_test_season()

    async_db_session.add_all([user, season])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)

    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.post(
        f"/seasons/{season.id}/users",
        headers={"Authorization": f"Bearer {token}"},
        json={},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["user"]["id"] == user.id


@pytest.mark.asyncio
async def test_user_registers_another_user_fail(test_client, async_db_session):
    """
    - GIVEN: Two regular users exist.
    - WHEN: User A tries to register User B for a season.
    - THEN: The request should fail with a 403 Forbidden error.
    """
    user_a = create_test_user(4)
    user_b = create_test_user(5)
    season = create_test_season()

    async_db_session.add_all([user_a, user_b, season])
    await async_db_session.commit()

    await async_db_session.refresh(user_a)
    await async_db_session.refresh(user_b)
    await async_db_session.refresh(season)

    token = create_access_token(data={"sub": user_a.uuid})

    response = await test_client.post(
        f"/seasons/{season.id}/users",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user_b.id},
    )
    assert response.status_code == 403
    assert "Not authorized" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_leaderboard_success(test_client, async_db_session):
    """
    - GIVEN: A season with registered users exists.
    - WHEN: A regular user requests the leaderboard for that season.
    - THEN: The request should succeed with a 200 OK status.
    """
    admin = create_test_user(6, is_admin=True)
    user1 = create_test_user(7)
    user2 = create_test_user(8)
    season = create_test_season()

    async_db_session.add_all([admin, user1, user2, season])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user1)
    await async_db_session.refresh(user2)
    await async_db_session.refresh(season)

    # Admin registers the two users
    await crud.register_user_for_season(
        db=async_db_session, season_id=season.id, user_id=user1.id, actor=admin
    )

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user1)
    await async_db_session.refresh(user2)
    await async_db_session.refresh(season)

    await crud.register_user_for_season(
        db=async_db_session, season_id=season.id, user_id=user2.id, actor=admin
    )

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user1)
    await async_db_session.refresh(user2)
    await async_db_session.refresh(season)

    token = create_access_token(data={"sub": user1.uuid})
    response = await test_client.get(
        f"/seasons/{season.id}/users", headers={"Authorization": f"Bearer {token}"}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
