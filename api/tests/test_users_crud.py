# ==============================================================================
# FILE: api/tests/test_users_crud.py
# ==============================================================================
# This file contains unit tests for the user-related functions in crud/users.py.
# These tests interact directly with the database session.

import crud
import pytest
from schemas import Actor, UserCreate, UserUpdate

# A mock actor for audit purposes in tests
mock_bot_actor = Actor(id="test_bot", is_bot=True)


@pytest.mark.asyncio
async def test_create_user(async_db_session):
    """Tests that a user can be created successfully."""
    user_data = UserCreate(
        discord_id=12345, in_game_name="Test User", lodestone_id="123"
    )
    new_user = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_bot_actor
    )

    assert new_user is not None
    assert new_user.discord_id == 12345
    assert new_user.in_game_name == "Test User"
    assert new_user.status == "pending"
    assert new_user.created_by == "test_bot"


@pytest.mark.asyncio
async def test_get_user_by_discord_id(async_db_session):
    """Tests retrieving a user by their Discord ID."""
    user_data = UserCreate(discord_id=67890, in_game_name="Find Me", lodestone_id="456")
    await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_bot_actor
    )

    found_user = await crud.get_user_by_discord_id(
        db=async_db_session, discord_id=67890
    )
    assert found_user is not None
    assert found_user.in_game_name == "Find Me"


@pytest.mark.asyncio
async def test_update_user(async_db_session):
    """Tests updating a user's status and admin flag."""
    user_data = UserCreate(
        discord_id=11122, in_game_name="Original Name", lodestone_id="789"
    )
    user_to_update = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_bot_actor
    )

    update_data = UserUpdate(status="verified", admin=True)
    updated_user = await crud.update_user(
        db=async_db_session,
        user=user_to_update,
        update_data=update_data,
        actor=mock_bot_actor,
    )

    assert updated_user.status == "verified"
    assert updated_user.admin is True


@pytest.mark.asyncio
async def test_ban_user(async_db_session):
    """Tests that a user's status can be set to 'banned'."""
    user_data = UserCreate(
        discord_id=33445, in_game_name="Soon Banned", lodestone_id="101"
    )
    user_to_ban = await crud.create_user(
        db=async_db_session, user_data=user_data, actor=mock_bot_actor
    )

    banned_user = await crud.ban_user(
        db=async_db_session, user=user_to_ban, actor=mock_bot_actor
    )
    assert banned_user.status == "banned"
