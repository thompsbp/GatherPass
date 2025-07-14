# ==============================================================================
# FILE: api/tests/test_auth.py
# ==============================================================================
# This file contains a dedicated test suite for the authentication and
# authorization dependencies in `auth.py`.

import crud
import models
import pytest
import pytest_asyncio
from auth import (
    create_access_token,
    require_admin_user,
    require_registered_user,
    settings,
)
from database import get_db
from fastapi import Depends, FastAPI
from httpx import ASGITransport, AsyncClient
from schemas import Actor, UserCreate

# A mock actor for audit purposes when creating test users
mock_actor = Actor(id="test_runner", is_bot=True)

# --- Test Setup: Create a temporary app with protected endpoints ---
auth_test_app = FastAPI()


@auth_test_app.get("/test-registered")
async def get_registered_user_test(
    user: models.User = Depends(require_registered_user),
):
    return {"status": "ok", "user_id": user.id}


@auth_test_app.get("/test-admin")
async def get_admin_user_test(user: models.User = Depends(require_admin_user)):
    return {"status": "ok", "user_id": user.id}


@pytest_asyncio.fixture(scope="function")
async def test_client(async_db_session):
    """
    This fixture creates a client for our local `auth_test_app` and correctly
    overrides its database dependency to use the single, shared test database
    session provided by the `async_db_session` fixture.
    """

    # Define the dependency override to use the existing, shared test session
    async def override_get_db():
        yield async_db_session

    # Apply the override to our local test app
    auth_test_app.dependency_overrides[get_db] = override_get_db

    # Create the test client
    transport = ASGITransport(app=auth_test_app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    # Clean up the override after the test
    auth_test_app.dependency_overrides.clear()


# --- Test Cases ---


@pytest.mark.asyncio
async def test_registered_user_with_valid_jwt(test_client, async_db_session):
    """
    - GIVEN: A valid, verified user exists in the database.
    - WHEN: A request is made to a 'registered user' endpoint with their valid JWT.
    - THEN: The request should succeed with a 200 OK status.
    """
    user_data = UserCreate(discord_id=1, in_game_name="Verified User", lodestone_id="1")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(user)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/test-registered", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_registered_user_with_pending_status(test_client, async_db_session):
    """
    - GIVEN: A valid user exists, but their status is 'pending'.
    - WHEN: A request is made with their valid JWT.
    - THEN: The request should fail with a 403 Forbidden error and a specific message.
    """
    user_data = UserCreate(discord_id=2, in_game_name="Pending User", lodestone_id="2")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    await async_db_session.refresh(user)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/test-registered", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "pending verification" in response.json()["detail"]


@pytest.mark.asyncio
async def test_registered_user_with_banned_status(test_client, async_db_session):
    """
    - GIVEN: A valid user exists, but their status is 'banned'.
    - WHEN: A request is made with their valid JWT.
    - THEN: The request should fail with a 403 Forbidden error.
    """
    user_data = UserCreate(discord_id=3, in_game_name="Banned User", lodestone_id="3")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    user.status = "banned"
    await async_db_session.commit()
    await async_db_session.refresh(user)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/test-registered", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_admin_user_bootstrap_case(test_client, async_db_session):
    """
    - GIVEN: The database is empty.
    - WHEN: A request is made by the bot on behalf of the ROOT_ADMIN_ID.
    - THEN: The request to an admin endpoint should succeed.
    """
    response = await test_client.get(
        "/test-admin",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(settings.root_admin_id),
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_user_with_valid_jwt(test_client, async_db_session):
    """
    - GIVEN: A verified admin user exists in the database.
    - WHEN: A request is made to an admin endpoint with their valid JWT.
    - THEN: The request should succeed.
    """
    user_data = UserCreate(discord_id=4, in_game_name="JWT Admin", lodestone_id="4")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    user.status = "verified"
    user.admin = True
    await async_db_session.commit()
    await async_db_session.refresh(user)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/test-admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_admin_user_with_bot_proxy(test_client, async_db_session):
    """
    - GIVEN: A verified admin user exists in the database.
    - WHEN: A request is made by the bot on their behalf.
    - THEN: The request to an admin endpoint should succeed.
    """
    user_data = UserCreate(discord_id=5, in_game_name="Bot Admin", lodestone_id="5")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    user.status = "verified"
    user.admin = True
    await async_db_session.commit()
    await async_db_session.refresh(user)

    response = await test_client.get(
        "/test-admin",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(user.discord_id),
        },
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_fail_admin_with_non_admin_user(test_client, async_db_session):
    """
    - GIVEN: A verified, non-admin user exists.
    - WHEN: A request is made to an admin endpoint on their behalf.
    - THEN: The request should fail with a 403 Forbidden error.
    """
    user_data = UserCreate(discord_id=6, in_game_name="Not Admin", lodestone_id="6")
    user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_actor
    )
    user.status = "verified"
    await async_db_session.commit()
    await async_db_session.refresh(user)
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        "/test-admin", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert "Admin privileges required" in response.json()["detail"]
