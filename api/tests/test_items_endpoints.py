# ==============================================================================
# FILE: api/tests/test_items_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the /items router.

import crud
import pytest
from auth import create_access_token
from schemas import Actor, ItemCreate, UserCreate

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


# --- Tests for POST /items/ ---


@pytest.mark.asyncio
async def test_create_item_success(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated admin user attempts to create a new item with valid data.
    - Expected Outcome:
        The request should succeed with an HTTP 201 Created status.
    """
    admin_user = await create_test_user(async_db_session, 1, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Mythril Ore", "lodestone_id": "5053"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Mythril Ore"


@pytest.mark.asyncio
async def test_create_item_fail_unauthorized(test_client, async_db_session):
    """
    - What is being tested:
        An authenticated, non-admin user attempts to create a new item.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    non_admin_user = await create_test_user(async_db_session, 2)
    token = create_access_token(data={"sub": non_admin_user.uuid})

    response = await test_client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Contraband", "lodestone_id": "0000"},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_item_fail_duplicate(test_client, async_db_session):
    """
    - What is being tested:
        An admin attempts to create an item with a lodestone_id that already exists.
    - Expected Outcome:
        The request should fail with an HTTP 400 Bad Request error.
    """
    admin_user = await create_test_user(async_db_session, 3, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    # Create the first item
    await test_client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Darksteel Ore", "lodestone_id": "5054"},
    )

    # Attempt to create it again
    response = await test_client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token}"},
        json={"name": "Duplicate Ore", "lodestone_id": "5054"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


# --- Tests for GET /items/ ---


@pytest.mark.asyncio
async def test_get_items_success(test_client, async_db_session):
    """
    - What is being tested:
        A regular, registered user attempts to retrieve the list of all items.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    # An admin creates an item first
    admin_user = await create_test_user(async_db_session, 4, is_admin=True)
    token_admin = create_access_token(data={"sub": admin_user.uuid})
    await test_client.post(
        "/items/",
        headers={"Authorization": f"Bearer {token_admin}"},
        json={"name": "Cobalt Ore", "lodestone_id": "5055"},
    )

    # Now, a regular user requests the list
    regular_user = await create_test_user(async_db_session, 5)
    token_user = create_access_token(data={"sub": regular_user.uuid})

    response = await test_client.get(
        "/items/", headers={"Authorization": f"Bearer {token_user}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0


# --- Tests for DELETE /items/{item_id} ---


@pytest.mark.asyncio
async def test_delete_item_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin user attempts to delete an existing item.
    - Expected Outcome:
        The request should succeed with an HTTP 204 No Content status.
    """
    admin_user = await create_test_user(async_db_session, 6, is_admin=True)
    token = create_access_token(data={"sub": admin_user.uuid})

    # Create an item to delete
    item_data = ItemCreate(name="Temporary Item", lodestone_id="9999")
    item_to_delete = await crud.create_item(db=async_db_session, item_data=item_data)

    # Delete the item via the endpoint
    response = await test_client.delete(
        f"/items/{item_to_delete.id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 204

    # Verify it's gone from the database
    deleted_item = await crud.get_item_by_id(
        db=async_db_session, item_id=item_to_delete.id
    )
    assert deleted_item is None
