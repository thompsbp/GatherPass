# ==============================================================================
# FILE: api/crud/submissions.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Submission model.

import crud
import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def create_submission(
    db: AsyncSession, submission_data: schemas.SubmissionCreate, actor: models.User
) -> models.Submission | None:
    """
    Creates a new submission record, and updates the user's total points for the season.
    Returns None if the SeasonItem does not exist or if the user is not registered
    for the season.
    """
    season_item_result = await db.execute(
        select(models.SeasonItem).filter(
            models.SeasonItem.id == submission_data.season_item_id
        )
    )
    season_item = season_item_result.scalars().first()

    if not season_item:
        return None

    season_user = await crud.get_user_progress_in_season(
        db, season_id=season_item.season_id, user_id=submission_data.user_id
    )

    if not season_user:
        return None

    total_points = season_item.point_value * submission_data.quantity

    new_submission = models.Submission(
        user_id=submission_data.user_id,
        season_item_id=submission_data.season_item_id,
        quantity=submission_data.quantity,
        total_point_value=total_points,
        created_by=actor.id,
        updated_by=actor.id,
    )
    db.add(new_submission)

    season_user.total_points += total_points
    db.add(season_user)

    await db.commit()
    await db.refresh(new_submission)

    result = await db.execute(
        select(models.Submission)
        .filter(models.Submission.id == new_submission.id)
        .options(
            selectinload(models.Submission.user),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.item
            ),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.season
            ),
            selectinload(models.Submission.creator),
            selectinload(models.Submission.updater),
        )
    )
    return result.scalars().one()


async def get_submissions(
    db: AsyncSession, season_id: int, user_id: int | None = None
) -> list[models.Submission]:
    """
    Retrieves all submissions for a season, with an optional filter for a specific user.
    Results are sorted by creation date.
    """
    query = (
        select(models.Submission)
        .join(models.SeasonItem)
        .filter(models.SeasonItem.season_id == season_id)
        .order_by(models.Submission.created_at.desc())
        .options(
            selectinload(models.Submission.user),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.item
            ),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.season
            ),
            selectinload(models.Submission.creator),
            selectinload(models.Submission.updater),
        )
    )

    if user_id:
        query = query.filter(models.Submission.user_id == user_id)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_submission_by_id(
    db: AsyncSession, submission_id: int
) -> models.Submission | None:
    """Retrieves a single submission by its primary key ID."""
    result = await db.execute(
        select(models.Submission)
        .filter(models.Submission.id == submission_id)
        .options(selectinload(models.Submission.season_item))
    )
    return result.scalars().first()


async def update_submission(
    db: AsyncSession,
    submission: models.Submission,
    update_data: schemas.SubmissionUpdate,
    actor: models.User,
) -> models.Submission:
    """
    Updates a submission's quantity and corrects the user's total points for the season.
    """
    submission_id = submission.id

    old_total_points = submission.total_point_value
    new_total_points = submission.season_item.point_value * update_data.quantity
    point_difference = new_total_points - old_total_points

    submission.quantity = update_data.quantity
    submission.total_point_value = new_total_points
    submission.updated_by = actor.id
    db.add(submission)

    season_user = await crud.get_user_progress_in_season(
        db,
        season_id=submission.season_item.season_id,
        user_id=submission.user_id,
    )

    if season_user:
        season_user.total_points += point_difference
        season_user.updated_by = actor.id
        db.add(season_user)

    await db.commit()

    result = await db.execute(
        select(models.Submission)
        .filter(models.Submission.id == submission_id)
        .options(
            selectinload(models.Submission.user),
            selectinload(models.Submission.creator),
            selectinload(models.Submission.updater),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.item
            ),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.season
            ),
        )
    )
    return result.scalars().one()


async def delete_submission(db: AsyncSession, submission: models.Submission) -> None:
    """
    Deletes a submission and subtracts its point value from the user's
    total points for the season.
    """
    points_to_remove = submission.total_point_value

    season_user = await crud.get_user_progress_in_season(
        db,
        season_id=submission.season_item.season_id,
        user_id=submission.user_id,
    )

    if season_user:
        season_user.total_points -= points_to_remove
        db.add(season_user)

    await db.delete(submission)
    await db.commit()
    return
