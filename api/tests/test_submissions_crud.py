# ==============================================================================
# FILE: api/tests/test_submissions_crud.py
# ==============================================================================
# This file contains unit tests for the submission-related functions.

from datetime import datetime, timedelta, timezone

import crud
import models
import pytest
from schemas import Actor, ItemCreate, SeasonCreate, SubmissionCreate, UserCreate

# --- Helper functions create model instances directly ---


def create_test_user(discord_id, is_admin=False):
    """Helper to create a user model instance."""
    return models.User(
        discord_id=discord_id,
        in_game_name=f"TestUser{discord_id}",
        lodestone_id=str(discord_id),
        admin=is_admin,
        status="verified",
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
async def test_create_submission_success(async_db_session):
    """Tests creating a valid submission and updating user points."""
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item = models.SeasonItem(
        season_id=season.id, item_id=item.id, point_value=50
    )
    async_db_session.add(season_item)
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)

    season_user = models.SeasonUser(
        user_id=user.id,
        season_id=season.id,
        created_by=str(admin.id),
        updated_by=str(admin.id),
    )
    async_db_session.add(season_user)
    await async_db_session.commit()
    await async_db_session.refresh(season_user)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)

    initial_points = season_user.total_points

    submission_data = SubmissionCreate(
        user_id=user.id, season_item_id=season_item.id, quantity=2
    )
    await async_db_session.refresh(season_user)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)

    new_submission = await crud.create_submission(
        db=async_db_session, submission_data=submission_data, actor=admin
    )

    await async_db_session.refresh(season_user)
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)
    await async_db_session.refresh(new_submission)

    assert new_submission is not None
    assert new_submission.user_id == user.id
    assert new_submission.season_item_id == season_item.id
    assert new_submission.quantity == 2
    assert new_submission.total_point_value == 100

    await async_db_session.refresh(season_user)
    assert season_user.total_points == initial_points + 100


@pytest.mark.asyncio
async def test_create_submission_fail_unregistered_user(async_db_session):
    """Tests that a submission fails if the user is not registered for the season."""
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item = models.SeasonItem(
        season_id=season.id, item_id=item.id, point_value=50
    )
    async_db_session.add(season_item)
    await async_db_session.commit()
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)

    submission_data = SubmissionCreate(
        user_id=user.id, season_item_id=season_item.id, quantity=1
    )
    failed_submission = await crud.create_submission(
        db=async_db_session, submission_data=submission_data, actor=admin
    )

    assert failed_submission is None


@pytest.mark.asyncio
async def test_get_submissions_for_user_in_season(async_db_session):
    """Tests retrieving all submissions for a user within a season."""
    admin = create_test_user(1, is_admin=True)
    user = create_test_user(2)
    season = create_test_season()
    item = create_test_item()

    async_db_session.add_all([admin, user, season, item])
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)

    season_item = models.SeasonItem(
        season_id=season.id, item_id=item.id, point_value=50
    )
    async_db_session.add(season_item)
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)

    season_user = models.SeasonUser(
        user_id=user.id,
        season_id=season.id,
        created_by=str(admin.id),
        updated_by=str(admin.id),
    )
    async_db_session.add(season_user)
    await async_db_session.commit()

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)
    await async_db_session.refresh(season_user)

    await crud.create_submission(
        db=async_db_session,
        submission_data=SubmissionCreate(
            user_id=user.id, season_item_id=season_item.id, quantity=1
        ),
        actor=admin,
    )
    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)
    await async_db_session.refresh(season_user)

    await crud.create_submission(
        db=async_db_session,
        submission_data=SubmissionCreate(
            user_id=user.id, season_item_id=season_item.id, quantity=3
        ),
        actor=admin,
    )

    await async_db_session.refresh(admin)
    await async_db_session.refresh(user)
    await async_db_session.refresh(season)
    await async_db_session.refresh(item)
    await async_db_session.refresh(season_item)
    await async_db_session.refresh(season_user)

    submissions = await crud.get_submissions_for_user_in_season(
        db=async_db_session, user_id=user.id, season_id=season.id
    )

    assert len(submissions) == 2
    assert submissions[0].quantity == 1
    assert submissions[1].quantity == 3
