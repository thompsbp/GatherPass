# ==============================================================================
# FILE: api/tests/test_users_endpoints.py
# ==============================================================================
# This file contains a comprehensive integration test suite for the /users router.
# It tests the full stack from API request to database response for each endpoint.

import crud
import pytest
from auth import create_access_token, settings
from schemas import Actor, UserCreate

# A mock actor for audit purposes when creating test users
mock_actor = Actor(id="test_runner", is_bot=True)


# --- Tests for POST /users/ ---


@pytest.mark.asyncio
async def test_create_user_success(test_client, async_db_session):
    """(Success) Tests that the root admin can create a user."""
    response = await test_client.post(
        "/users/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(settings.root_admin_id),
        },
        json={
            "discord_id": settings.root_admin_id,
            "in_game_name": "Root Admin",
            "lodestone_id": "0",
        },
    )
    assert response.status_code == 201
    data = response.json()
    assert data["discord_id"] == settings.root_admin_id


@pytest.mark.asyncio
async def test_create_user_fail_unauthorized(test_client, async_db_session):
    """(Authorization) Tests that a non-admin cannot create a user."""
    response = await test_client.post(
        "/users/",
        headers={
            "X-API-Key": "this-is-the-wrong-key",
            "X-User-Discord-ID": str(settings.root_admin_id),
        },
        json={
            "discord_id": 123,
            "in_game_name": "Test",
            "lodestone_id": "123",
        },
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_user_fail_validation(test_client, async_db_session):
    """(Validation) Tests creating a user with improperly formatted data."""
    response = await test_client.post(
        "/users/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(settings.root_admin_id),
        },
        json={
            "discord_id": "this-is-not-a-number",  # Invalid data type
            "in_game_name": "Invalid User",
            "lodestone_id": "123",
        },
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_create_user_fail_duplicate(test_client, async_db_session):
    """(Business Logic) Tests creating a user with a discord_id that already exists."""
    user_data = UserCreate(discord_id=112233, in_game_name="Existing", lodestone_id="1")
    await crud.create_user(db=async_db_session, user_data=user_data, actor=mock_actor)

    response = await test_client.post(
        "/users/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(settings.root_admin_id),
        },
        json={
            "discord_id": 112233,
            "in_game_name": "Duplicate",
            "lodestone_id": "2",
        },
    )
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


# --- Tests for GET /users/ ---


@pytest.mark.asyncio
async def test_get_users_success(test_client, async_db_session):
    """(Success) Tests that an admin can successfully list users."""
    user_data = UserCreate(discord_id=456, in_game_name="JWT Admin", lodestone_id="456")
    admin_user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    admin_user.admin = True
    admin_user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(admin_user)
    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)


@pytest.mark.asyncio
async def test_get_users_fail_unauthorized(test_client, async_db_session):
    """(Authorization) Tests that a non-admin cannot list users."""
    user_data = UserCreate(
        discord_id=123, in_game_name="Regular User", lodestone_id="123"
    )
    non_admin = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    non_admin.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(non_admin)
    token = create_access_token(data={"sub": non_admin.uuid})

    response = await test_client.get(
        "/users/", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]


# --- Tests for GET /users/{user_id} ---


@pytest.mark.asyncio
async def test_get_user_by_id_fail_not_found(test_client, async_db_session):
    """(Business Logic) Tests getting a user ID that does not exist."""
    admin_data = UserCreate(discord_id=13, in_game_name="Admin", lodestone_id="13")
    admin_user = await crud.create_user(
        db=async_db_session, user_data=admin_data, actor=mock_actor
    )
    admin_user.admin = True
    admin_user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(admin_user)
    token = create_access_token(data={"sub": admin_user.uuid})

    response = await test_client.get(
        "/users/99999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404


# --- Tests for PATCH /users/{user_id} ---


@pytest.mark.asyncio
async def test_patch_user_success(test_client, async_db_session):
    """(Success) Tests that an admin can update another user."""
    admin_data = UserCreate(
        discord_id=10, in_game_name="Updater Admin", lodestone_id="10"
    )
    admin_user = await crud.create_user(
        db=async_db_session, user_data=admin_data, actor=mock_actor
    )
    admin_user.admin = True
    admin_user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(admin_user)
    token = create_access_token(data={"sub": admin_user.uuid})

    target_data = UserCreate(
        discord_id=11, in_game_name="Target User", lodestone_id="11"
    )
    target_user = await crud.create_user(
        db=async_db_session, user_data=target_data, actor=mock_actor
    )

    response = await test_client.patch(
        f"/users/{target_user.id}",
        headers={"Authorization": f"Bearer {token}"},
        json={"status": "verified", "admin": True},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "verified"
    assert data["admin"] is True


# --- Tests for DELETE /users/{user_id} ---


@pytest.mark.asyncio
async def test_delete_user_success(test_client, async_db_session):
    """(Success) Tests that an admin can 'delete' (ban) another user."""
    admin_data = UserCreate(
        discord_id=14, in_game_name="Deleter Admin", lodestone_id="14"
    )
    admin_user = await crud.create_user(
        db=async_db_session, user_data=admin_data, actor=mock_actor
    )
    admin_user.admin = True
    admin_user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(admin_user)
    token = create_access_token(data={"sub": admin_user.uuid})

    target_data = UserCreate(
        discord_id=15, in_game_name="Target To Ban", lodestone_id="15"
    )
    target_user = await crud.create_user(
        db=async_db_session, user_data=target_data, actor=mock_actor
    )

    response = await test_client.delete(
        f"/users/{target_user.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "banned"

    @pytest.mark.asyncio
    async def test_create_user_fail_with_jwt(test_client, async_db_session):
        """
        (Authorization) Tests that a user with a JWT cannot create another user,
        proving the endpoint is truly bot-only.
        """
        # Create a user to act as the requester (in this case, an admin)
        admin_user = create_test_user(9, is_admin=True)
        async_db_session.add(admin_user)
        await async_db_session.commit()
        await async_db_session.refresh(admin_user)

        # Get a valid JWT for the admin
        token = create_access_token(data={"sub": admin_user.uuid})

        # Attempt to create a new user using the JWT
        response = await test_client.post(
            "/users/",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "discord_id": 10,
                "in_game_name": "Test JWT Create",
                "lodestone_id": "10",
            },
        )

        # The request should be forbidden because the endpoint requires the bot's API key.
        assert response.status_code == 403
