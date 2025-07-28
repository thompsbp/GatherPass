# ==============================================================================
# FILE: api/crud/seasons.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Season model.

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
    """Retrieves the currently active season based on the current date."""
    now = datetime.now(timezone.utc)
    result = await db.execute(
        select(models.Season).filter(
            models.Season.start_date <= now, models.Season.end_date >= now
        )
    )
    return result.scalars().first()


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
