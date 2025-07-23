# ==============================================================================
# FILE: api/tests/test_seasons_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the /seasons router.

from datetime import datetime, timedelta, timezone

import crud
import pytest
from auth import create_access_token
from schemas import Actor, SeasonCreate, UserCreate

# A mock actor for audit purposes when creating test users/seasons
mock_actor = Actor(id="test_runner", is_bot=True)

# --- Helper function to create users for tests ---


async def create_test_user(db_session, discord_id, is_admin=False, is_verified=True):
    """A helper to quickly create and set up a user for testing."""
    user_data = UserCreate(
        discord_id=discord_id,
        in_game_name=f"TestUser{discord_id}",
        lodestone_id=str(discord_id),
    )
    user = await crud.create_user(db=db_session, user_data=user_data, actor=mock_actor)
    if is_verified:
        user.status = "verified"
    if is_admin:
        user.admin = True
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Tests for POST /seasons/ ---


@pytest.mark.asyncio
async def test_create_season_success(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated admin user attempts to create a new season
        with valid data.
    - Expected Outcome:
        The request should succeed with an HTTP 201 Created status, and the
        response body should contain the data for the newly created season.
    """
    admin_user = await create_test_user(async_db_session, 1, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    start_time = datetime.now(timezone.utc).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    response = await test_client.post(
        "/seasons/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Season 1",
            "number": 1,
            "start_date": start_time,
            "end_date": end_time,
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Season 1"
    assert data["number"] == 1


@pytest.mark.asyncio
async def test_create_season_fail_unauthorized(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated, non-admin user attempts to create a new season.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    non_admin_user = await create_test_user(async_db_session, 2)
    token = create_access_token(data={"sub": non_admin_user.uuid})

    start_time = datetime.now(timezone.utc).isoformat()
    end_time = (datetime.now(timezone.utc) + timedelta(days=30)).isoformat()

    response = await test_client.post(
        "/seasons/",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Season 2",
            "number": 2,
            "start_date": start_time,
            "end_date": end_time,
        },
    )
    assert response.status_code == 403


# --- Tests for GET /seasons/ ---


@pytest.mark.asyncio
async def test_get_seasons_success(test_client, async_db_session):
    """
    - What is being tested:
        A regular, registered user attempts to retrieve the list of all seasons.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    admin_user = await create_test_user(async_db_session, 3, is_admin=True)
    season_data = SeasonCreate(
        name="Test Season",
        number=1,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    regular_user = await create_test_user(async_db_session, 4)
    token = create_access_token(data={"sub": regular_user.uuid})

    response = await test_client.get(
        "/seasons/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_seasons_fail_unauthenticated(test_client):
    """
    - What is being tested:
        A request is made to retrieve the list of seasons without any
        authentication credentials.
    - Expected Outcome:
        The request should be denied with an HTTP 401 Unauthorized error.
    """
    response = await test_client.get("/seasons/")
    assert response.status_code == 401


# --- Tests for GET /seasons/{season_id} ---


@pytest.mark.asyncio
async def test_get_season_by_id_fail_not_found(test_client, async_db_session):
    """
    - What is being tested:
        A registered user requests a season with an ID that does not exist.
    - Expected Outcome:
        The request should fail with an HTTP 404 Not Found error.
    """
    user = await create_test_user(async_db_session, 5)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/seasons/99999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


# --- Tests for PATCH /seasons/{season_id} ---


@pytest.mark.asyncio
async def test_update_season_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin user attempts to update the details of an existing season.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    admin_user = await create_test_user(async_db_session, 6, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    season_data = SeasonCreate(
        name="Original Name",
        number=3,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    season = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    response = await test_client.patch(
        f"/seasons/{season.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Updated Season Name"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Season Name"


# --- Tests for DELETE /seasons/{season_id} ---


@pytest.mark.asyncio
async def test_delete_season_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin user attempts to delete an existing season.
    - Expected Outcome:
        The request should succeed with an HTTP 204 No Content status.
    """
    admin_user = await create_test_user(async_db_session, 7, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    season_data = SeasonCreate(
        name="To Be Deleted",
        number=4,
        start_date=datetime.now(timezone.utc),
        end_date=datetime.now(timezone.utc) + timedelta(days=30),
    )
    season = await crud.create_season(
        db=async_db_session, season_data=season_data, actor=admin_user
    )

    response = await test_client.delete(
        f"/seasons/{season.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    deleted_season = await crud.get_season_by_id(
        db=async_db_session, season_id=season.id
    )
    assert deleted_season is None
