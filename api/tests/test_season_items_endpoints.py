# ==============================================================================
# FILE: api/tests/test_season_items_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the
# nested /seasons/{season_id}/items router.

from datetime import datetime, timedelta, timezone

import crud
import models  # Import models directly
import pytest
from auth import create_access_token
from schemas import Actor, ItemCreate, SeasonCreate, UserCreate

# --- Helper functions now create model instances directly, without using CRUD ---


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


def create_test_item():
    """Helper to create an item model instance."""
    return models.Item(name="Test Item", lodestone_id="12345")


# --- Test Cases ---


@pytest.mark.asyncio
async def test_add_item_to_season_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin adds an existing item to an existing season.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    admin_user = create_test_user(1, is_admin=True)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin_user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin_user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"item_id": item.id, "point_value": 150},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["point_value"] == 150


@pytest.mark.asyncio
async def test_add_item_to_season_fail_unauthorized(test_client, async_db_session):
    """
    - What is being tested:
        A non-admin user attempts to add an item to a season.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    non_admin = create_test_user(2)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([non_admin, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(non_admin)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    token = create_access_token(data={"sub": non_admin.uuid})

    response = await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"item_id": item.id, "point_value": 150},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_add_item_to_season_fail_duplicate(test_client, async_db_session):
    """
    - What is being tested:
        An admin attempts to add the same item to a season twice.
    - Expected Outcome:
        The second request should fail with an HTTP 400 Bad Request error.
    """
    admin_user = create_test_user(4, is_admin=True)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin_user, season, item])
    await async_db_session.commit()

    # --- The Definitive Fix: Refresh objects after commit ---
    await async_db_session.refresh(admin_user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    token = create_access_token(data={"sub": admin_user.uuid})

    # First request should succeed
    await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"item_id": item.id, "point_value": 150},
    )

    # Second request should fail
    response = await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"item_id": item.id, "point_value": 200},
    )
    assert response.status_code == 400
    assert "already in this season" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_items_for_season_success(test_client, async_db_session):
    """
    - What is being tested:
        A regular registered user requests the list of items for a season.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status.
    """
    admin_user = create_test_user(5, is_admin=True)
    regular_user = create_test_user(6)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin_user, regular_user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin_user)
    await async_db_session.refresh(regular_user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    admin_token = create_access_token(data={"sub": admin_user.uuid})
    await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {admin_token}"},
        json={"item_id": item.id, "point_value": 100},
    )

    user_token = create_access_token(data={"sub": regular_user.uuid})

    response = await test_client.get(
        f"/seasons/{season.id}/items",  # Note the trailing slash
        headers={"Authorization": f"Bearer {user_token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1


@pytest.mark.asyncio
async def test_remove_item_from_season_success(test_client, async_db_session):
    """
    - What is being tested:
        An admin removes an item from a season.
    - Expected Outcome:
        The request should succeed with an HTTP 204 No Content status.
    """
    admin_user = create_test_user(7, is_admin=True)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin_user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin_user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    token = create_access_token(data={"sub": admin_user.uuid})

    await test_client.post(
        f"/seasons/{season.id}/items",
        headers={"Authorization": f"Bearer {token}"},
        json={"item_id": item.id, "point_value": 100},
    )

    response = await test_client.delete(
        f"/seasons/{season.id}/items/{item.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204
