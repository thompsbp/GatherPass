# ==============================================================================
# FILE: api/tests/test_prizes_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the /prizes router.

import crud
import pytest
from auth import create_access_token
from schemas import Actor, PrizeCreate, UserCreate

# A mock actor for audit purposes
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


# --- Tests for POST /prizes/ ---


@pytest.mark.asyncio
async def test_create_prize_success(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated admin user attempts to create a new prize.
    - Expected Outcome:
        The request should succeed with an HTTP 201 Created status.
    """
    admin_user = await create_test_user(async_db_session, 1, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.post(
        "/prizes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Grand Prize", "value": 10000},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "Grand Prize"


@pytest.mark.asyncio
async def test_create_prize_fail_unauthorized(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated, non-admin user attempts to create a new prize.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    non_admin_user = await create_test_user(async_db_session, 2)
    token = create_access_token(data={"sub": non_admin_user.uuid})

    response = await test_client.post(
        "/prizes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "Runner-up Prize"},
    )
    assert response.status_code == 403


# --- Tests for GET /prizes/ ---


@pytest.mark.asyncio
async def test_get_prizes_success(test_client, async_db_session):
    """
    - What is being tested:
        A regular, registered user attempts to retrieve the list of all prizes.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    # An admin creates a prize first
    admin_user = await create_test_user(async_db_session, 3, is_admin=True)
    token_admin = create_access_token(data={"sub": admin_user.uuid})
    await test_client.post(
        "/prizes/",
        headers={"Authorization": f"Bearer {token_admin}"},
        json={"description": "Participation Award"},
    )

    # Now, a regular user requests the list
    regular_user = await create_test_user(async_db_session, 4)
    token_user = create_access_token(data={"sub": regular_user.uuid})

    response = await test_client.get(
        "/prizes/", headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


# --- Tests for GET /prizes/{prize_id} ---


@pytest.mark.asyncio
async def test_get_prize_by_id_fail_not_found(test_client, async_db_session):
    """
    - What is being tested:
        A registered user requests a prize with an ID that does not exist.
    - Expected Outcome:
        The request should fail with an HTTP 404 Not Found error.
    """
    user = await create_test_user(async_db_session, 5)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/prizes/99999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


# --- Tests for DELETE /prizes/{prize_id} ---


@pytest.mark.asyncio
async def test_delete_prize_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin user attempts to delete an existing prize.
    - Expected Outcome:
        The request should succeed with an HTTP 204 No Content status.
    """
    admin_user = await create_test_user(async_db_session, 6, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    # Create a prize to delete
    prize_data = PrizeCreate(description="Temporary Prize")
    prize_to_delete = await crud.create_prize(
        db=async_db_session, prize_data=prize_data
    )

    # Delete the prize via the endpoint
    response = await test_client.delete(
        f"/prizes/{prize_to_delete.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify it's gone from the database
    deleted_prize = await crud.get_prize_by_id(
        db=async_db_session, prize_id=prize_to_delete.id
    )
    assert deleted_prize is None
