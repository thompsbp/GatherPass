# ==============================================================================
# FILE: api/crud/season_users.py
# ==============================================================================
# This file contains all the database functions for the SeasonUser association.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def register_user_for_season(
    db: AsyncSession, season_id: int, user_id: int, actor: models.User
) -> models.SeasonUser | None:
    """
    Registers a user for a specific season.
    Returns None if the user is already registered for the season.
    """
    existing_link_result = await db.execute(
        select(models.SeasonUser).filter_by(season_id=season_id, user_id=user_id)
    )
    if existing_link_result.scalars().first():
        return None

    new_season_user = models.SeasonUser(
        season_id=season_id,
        user_id=user_id,
        created_by=actor.id,
        updated_by=actor.id,
    )
    db.add(new_season_user)
    await db.commit()

    # --- The Permanent Fix ---
    # After committing, we must refresh the object to load its database state
    # (like the auto-generated ID) before we can use it again.
    await db.refresh(new_season_user)

    # Now that the object is "live", we can re-fetch it with its relationships
    # loaded for the API response.
    result = await db.execute(
        select(models.SeasonUser)
        .filter(models.SeasonUser.id == new_season_user.id)
        .options(
            selectinload(models.SeasonUser.user), selectinload(models.SeasonUser.season)
        )
    )
    return result.scalars().one()


async def get_user_progress_in_season(
    db: AsyncSession, season_id: int, user_id: int
) -> models.SeasonUser | None:
    """
    Retrieves a specific user's progress within a season.
    """
    result = await db.execute(
        select(models.SeasonUser)
        .filter_by(season_id=season_id, user_id=user_id)
        .options(
            selectinload(models.SeasonUser.user), selectinload(models.SeasonUser.season)
        )
    )
    return result.scalars().first()


async def get_all_users_for_season(
    db: AsyncSession, season_id: int
) -> list[models.SeasonUser]:
    """
    Retrieves a list of all users participating in a specific season (leaderboard).
    """
    result = await db.execute(
        select(models.SeasonUser)
        .filter(models.SeasonUser.season_id == season_id)
        .options(
            selectinload(models.SeasonUser.user), selectinload(models.SeasonUser.season)
        )
    )
    return list(result.scalars().all())
