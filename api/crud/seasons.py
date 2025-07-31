# ==============================================================================
# FILE: api/crud/seasons.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Season model.

from datetime import datetime, timezone
from typing import Union

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_season(
    db: AsyncSession, season_data: schemas.SeasonCreate, actor: models.User
) -> models.Season:
    """Creates a new season in the database."""
    new_season = models.Season(
        name=season_data.name,
        number=season_data.number,
        start_date=season_data.start_date,
        end_date=season_data.end_date,
    )
    db.add(new_season)
    await db.commit()
    await db.refresh(new_season)
    return new_season


async def get_season_by_id(db: AsyncSession, season_id: int) -> models.Season | None:
    """Retrieves a season from the database by its primary key ID."""
    result = await db.execute(
        select(models.Season).filter(models.Season.id == season_id)
    )
    return result.scalars().first()


async def get_seasons(
    db: AsyncSession, offset: int = 0, limit: int = 100, name: str | None = None
) -> list[models.Season]:
    """Retrieves a list of all seasons with pagination and optional name filtering."""
    query = select(models.Season)

    if name:
        query = query.filter(models.Season.name.ilike(f"{name}%"))

    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    return list(result.scalars().all())


async def get_current_season(db: AsyncSession) -> models.Season | None:
    """
    Retrieves the currently active season. If no season is currently active,
    it retrieves the one that finished most recently. It will not select a
    season that is in the future.
    """
    now = datetime.now(timezone.utc)

    # First, try to find a currently active season (start_date <= now <= end_date)
    current_season_result = await db.execute(
        select(models.Season).filter(
            models.Season.start_date <= now, models.Season.end_date >= now
        )
    )
    current_season = current_season_result.scalars().first()

    if current_season:
        return current_season

    # If no season is active, find the most recently finished one
    most_recent_finished_result = await db.execute(
        select(models.Season)
        .filter(
            models.Season.end_date < now
        )  # Find all seasons that have already ended
        .order_by(
            models.Season.end_date.desc()
        )  # Order by end date to get the newest one first
    )
    return most_recent_finished_result.scalars().first()


async def get_latest_season(db: AsyncSession) -> models.Season | None:
    """Retrieves the season with the highest number."""
    result = await db.execute(
        select(models.Season).order_by(models.Season.number.desc())
    )
    return result.scalars().first()


async def update_season(
    db: AsyncSession,
    season: models.Season,
    update_data: schemas.SeasonUpdate,
    actor: models.User,
) -> models.Season:
    """Updates a season's record."""
    # Get the update data, excluding any fields that were not set
    update_dict = update_data.model_dump(exclude_unset=True)

    # Update the season model with the new data
    for key, value in update_dict.items():
        setattr(season, key, value)

    db.add(season)
    await db.commit()
    await db.refresh(season)
    return season


async def delete_season(db: AsyncSession, season: models.Season) -> None:
    """Deletes a season from the database."""
    await db.delete(season)
    await db.commit()
    return
