# ==============================================================================
# FILE: api/tests/test_prizes_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the /prizes router.

import crud
import models
import pytest
from auth import create_access_token
from schemas import UserCreate

# --- Helper function to create users for tests ---


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


# --- Test Cases ---


@pytest.mark.asyncio
async def test_create_prize_success(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated admin user attempts to create a new prize.
    - Expected Outcome:
        The request should succeed with an HTTP 201 Created status.
    """
    admin_user = create_test_user(1, is_admin=True)
    async_db_session.add(admin_user)
    await async_db_session.commit()
    await async_db_session.refresh(admin_user)

    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.post(
        "/prizes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "100,000 Gil", "value": 100000},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["description"] == "100,000 Gil"


@pytest.mark.asyncio
async def test_create_prize_fail_unauthorized(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated, non-admin user attempts to create a new prize.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    non_admin_user = create_test_user(2)
    async_db_session.add(non_admin_user)
    await async_db_session.commit()
    await async_db_session.refresh(non_admin_user)

    token = create_access_token(data={"sub": non_admin_user.uuid})

    response = await test_client.post(
        "/prizes/",
        headers={"Authorization": f"Bearer {token}"},
        json={"description": "A consolation prize"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_get_prizes_success(test_client, async_db_session):
    """
    - What is being tested:
        A regular, registered user attempts to retrieve the list of all prizes.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    # An admin creates a prize first
    admin_user = create_test_user(3, is_admin=True)
    prize = models.Prize(description="Participation Award")
    async_db_session.add_all([admin_user, prize])
    await async_db_session.commit()

    # Now, a regular user requests the list
    regular_user = create_test_user(4)
    async_db_session.add(regular_user)
    await async_db_session.commit()
    await async_db_session.refresh(regular_user)

    token_user = create_access_token(data={"sub": regular_user.uuid})

    response = await test_client.get(
        "/prizes/", headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


@pytest.mark.asyncio
async def test_get_prize_by_id_fail_not_found(test_client, async_db_session):
    """
    - What is being tested:
        A registered user requests a prize with an ID that does not exist.
    - Expected Outcome:
        The request should fail with an HTTP 404 Not Found error.
    """
    user = create_test_user(5)
    async_db_session.add(user)
    await async_db_session.commit()
    await async_db_session.refresh(user)

    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/prizes/99999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_prize_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin user attempts to delete an existing prize.
    - Expected Outcome:
        The request should succeed with an HTTP 204 No Content status.
    """
    admin_user = create_test_user(6, is_admin=True)
    prize_to_delete = models.Prize(description="Temporary Prize")
    async_db_session.add_all([admin_user, prize_to_delete])
    await async_db_session.commit()

    await async_db_session.refresh(admin_user)
    await async_db_session.refresh(prize_to_delete)

    token = create_access_token(data={"sub": admin_user.uuid})

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
