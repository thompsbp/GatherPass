# ==============================================================================
# FILE: api/tests/test_token_endpoints.py
# ==============================================================================
# This file contains the integration test suite for the /token router.

import crud
import pytest
from auth import settings
from jose import jwt
from schemas import Actor, UserCreate

# A mock actor for audit purposes when creating test users
mock_actor = Actor(id="test_runner", is_bot=True)

# --- Helper function to create users for tests ---


async def create_test_user(db_session, discord_id, is_verified=True):
    """A helper to quickly create and set up a user for testing."""
    user_data = UserCreate(
        discord_id=discord_id,
        in_game_name=f"TestUser{discord_id}",
        lodestone_id=str(discord_id),
    )
    user = await crud.create_user(db=db_session, user_data=user_data, actor=mock_actor)
    if is_verified:
        user.status = "verified"
    await db_session.commit()
    await db_session.refresh(user)
    return user


# --- Test Cases ---


@pytest.mark.asyncio
async def test_generate_token_success(test_client, async_db_session):
    """
    - What is being tested:
        A valid, verified user requests a token via the bot proxy.
    - Expected Outcome:
        The request should succeed with an HTTP 200 OK status, and the
        response body should contain a valid JWT.
    """
    # Create a verified user
    verified_user = await create_test_user(async_db_session, 1, is_verified=True)

    # Request a token on their behalf
    response = await test_client.post(
        "/token/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(verified_user.discord_id),
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    # Optional: Verify the token contains the correct user UUID
    payload = jwt.decode(
        data["access_token"], settings.jwt_secret_key, algorithms=[settings.algorithm]
    )
    assert payload["sub"] == verified_user.uuid


@pytest.mark.asyncio
async def test_generate_token_fail_for_pending_user(test_client, async_db_session):
    """
    - What is being tested:
        A user whose status is 'pending' requests a token.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error because
        the `require_registered_user` dependency checks the user's status.
    """
    # Create a user but leave their status as the default 'pending'
    pending_user = await create_test_user(async_db_session, 2, is_verified=False)

    response = await test_client.post(
        "/token/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(pending_user.discord_id),
        },
    )
    assert response.status_code == 403
    assert "pending verification" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_token_fail_for_banned_user(test_client, async_db_session):
    """
    - What is being tested:
        A user whose status is 'banned' requests a token.
    - Expected Outcome:
        The request should be denied with an HTTP 403 Forbidden error.
    """
    # Create a user and set their status to 'banned'
    banned_user = await create_test_user(async_db_session, 3, is_verified=False)
    banned_user.status = "banned"
    await async_db_session.commit()
    await async_db_session.refresh(banned_user)

    response = await test_client.post(
        "/token/",
        headers={
            "X-API-Key": settings.bot_api_key,
            "X-User-Discord-ID": str(banned_user.discord_id),
        },
    )
    assert response.status_code == 403
    assert "Access Denied" in response.json()["detail"]


@pytest.mark.asyncio
async def test_generate_token_fail_unauthenticated(test_client):
    """
    - What is being tested:
        A request is made to the token endpoint without any valid credentials.
    - Expected Outcome:
        The request should be denied with an HTTP 401 Unauthorized error.
    """
    response = await test_client.post("/token/")
    assert response.status_code == 401
