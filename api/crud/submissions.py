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
        created_by=str(actor.id),
        updated_by=str(actor.id),
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
        )
    )
    return result.scalars().one()


async def get_submissions_for_user_in_season(
    db: AsyncSession, user_id: int, season_id: int
) -> list[models.Submission]:
    """Retrieves all submissions for a specific user within a specific season."""
    result = await db.execute(
        select(models.Submission)
        .join(models.SeasonItem)
        .filter(
            models.Submission.user_id == user_id,
            models.SeasonItem.season_id == season_id,
        )
        .options(
            selectinload(models.Submission.user),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.item
            ),
            selectinload(models.Submission.season_item).selectinload(
                models.SeasonItem.season
            ),
        )
    )
    return list(result.scalars().all())
