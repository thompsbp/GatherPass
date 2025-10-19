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

    await db.refresh(new_season_user)

    result = await db.execute(
        select(models.SeasonUser)
        .filter(models.SeasonUser.id == new_season_user.id)
        .options(
            selectinload(models.SeasonUser.user),
            selectinload(models.SeasonUser.season),
            selectinload(models.SeasonUser.creator),
            selectinload(models.SeasonUser.updater),
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
    db: AsyncSession, season_id: int, order: str = "name_asc"
) -> list[models.SeasonUser]:
    """
    Retrieves a list of all users in a season, with flexible sorting.
    """
    query = (
        select(models.SeasonUser)
        .filter(models.SeasonUser.season_id == season_id)
        .options(
            selectinload(models.SeasonUser.user), selectinload(models.SeasonUser.season)
        )
    )

    if order == "points_desc":
        query = query.order_by(models.SeasonUser.total_points.desc())
    else:
        query = query.join(
            models.User, models.SeasonUser.user_id == models.User.id
        ).order_by(models.User.in_game_name.asc())

    result = await db.execute(query)
    return list(result.scalars().all())
