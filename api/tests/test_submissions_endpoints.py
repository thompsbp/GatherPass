# ==============================================================================
# FILE: api/tests/test_submissions_endpoints.py
# ==============================================================================
# This file contains the integration test suite for the submission endpoints.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from auth import create_access_token
from schemas import SubmissionCreate, UserCreate

# --- Helper functions create model instances directly ---


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
async def test_create_submission_success_self(test_client, async_db_session):
    """
    - GIVEN: A user is registered for a season with a valid item.
    - WHEN: The user submits that item for themself.
    - THEN: The submission is created and their points are updated.
    """
    user = create_test_user(1)
    season = create_test_season()
    item = create_test_item()
    season_item = models.SeasonItem(season=season, item=item, point_value=50)
    season_user = models.SeasonUser(
        user=user, season=season, created_by="test", updated_by="test"
    )

    async_db_session.add_all([user, season, item, season_item, season_user])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season_user)
    await async_db_session.refresh(season_item)

    initial_points = season_user.total_points
    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.post(
        "/submissions/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user.id, "season_item_id": season_item.id, "quantity": 3},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_point_value"] == 150

    await async_db_session.refresh(season_user)
    assert season_user.total_points == initial_points + 150


@pytest.mark.asyncio
async def test_create_submission_success_by_admin(test_client, async_db_session):
    """
    - GIVEN: An admin and another user are registered for a season.
    - WHEN: The admin submits an item on behalf of the other user.
    - THEN: The submission is created and the other user's points are updated.
    """
    admin = create_test_user(2, is_admin=True)
    user = create_test_user(3)
    season = create_test_season()
    item = create_test_item()
    season_item = models.SeasonItem(season=season, item=item, point_value=25)
    season_user = models.SeasonUser(
        user=user, season=season, created_by="test", updated_by="test"
    )

    async_db_session.add_all([admin, user, season, item, season_item, season_user])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season_item)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.post(
        "/submissions/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user.id, "season_item_id": season_item.id, "quantity": 1},
    )
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_create_submission_fail_unauthorized(test_client, async_db_session):
    """
    - GIVEN: Two regular users are registered for a season.
    - WHEN: User A tries to submit an item on behalf of User B.
    - THEN: The request should fail with a 403 Forbidden error.
    """
    user_a = create_test_user(4)
    user_b = create_test_user(5)
    season = create_test_season()
    item = create_test_item()
    season_item = models.SeasonItem(season=season, item=item, point_value=10)

    async_db_session.add_all([user_a, user_b, season, item, season_item])
    await async_db_session.commit()

    # --- The Definitive Fix: Refresh all objects after commit ---
    await async_db_session.refresh(user_a)
    await async_db_session.refresh(user_b)
    await async_db_session.refresh(season_item)

    token = create_access_token(data={"sub": user_a.uuid})

    response = await test_client.post(
        "/submissions/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user_b.id, "season_item_id": season_item.id, "quantity": 1},
    )
    assert response.status_code == 403


@pytest.mark.asyncio
async def test_create_submission_fail_unregistered(test_client, async_db_session):
    """
    - GIVEN: A user is NOT registered for a season.
    - WHEN: An admin tries to submit an item for that user in that season.
    - THEN: The request should fail with a 400 Bad Request error.
    """
    admin = create_test_user(6, is_admin=True)
    user = create_test_user(7)
    season = create_test_season()
    item = create_test_item()
    season_item = models.SeasonItem(season=season, item=item, point_value=10)

    async_db_session.add_all([admin, user, season, item, season_item])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season_item)

    token = create_access_token(data={"sub": admin.uuid})

    response = await test_client.post(
        "/submissions/",
        headers={"Authorization": f"Bearer {token}"},
        json={"user_id": user.id, "season_item_id": season_item.id, "quantity": 1},
    )
    assert response.status_code == 400
    assert "not be registered for this season" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_submissions_for_user_in_season(test_client, async_db_session):
    """
    - GIVEN: A user has made multiple submissions in a season.
    - WHEN: A request is made to view their submissions for that season.
    - THEN: The request should succeed with a 200 OK status and return all submissions.
    """
    user = create_test_user(8)
    season = create_test_season()
    item = create_test_item()
    season_item = models.SeasonItem(season=season, item=item, point_value=10)
    season_user = models.SeasonUser(
        user=user, season=season, created_by="test", updated_by="test"
    )

    async_db_session.add_all([user, season, item, season_item, season_user])
    await async_db_session.commit()

    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(season_item)

    # Create two submissions
    await crud.create_submission(
        db=async_db_session,
        submission_data=SubmissionCreate(
            user_id=user.id, season_item_id=season_item.id, quantity=2
        ),
        actor=user,
    )
    await crud.create_submission(
        db=async_db_session,
        submission_data=SubmissionCreate(
            user_id=user.id, season_item_id=season_item.id, quantity=5
        ),
        actor=user,
    )

    token = create_access_token(data={"sub": user.uuid})

    response = await test_client.get(
        f"/users/{user.id}/seasons/{season.id}/submissions/",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
