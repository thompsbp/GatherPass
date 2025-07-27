# ==============================================================================
# FILE: api/crud/season_ranks.py
# ==============================================================================
# This file contains all the database functions for the SeasonRank association.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def add_rank_to_season(
    db: AsyncSession, season_id: int, rank_data: schemas.SeasonRankCreate
) -> models.SeasonRank | None:
    """
    Associates a rank with a season, setting its number and required points.
    Returns the new, fully-loaded SeasonRank object for serialization.
    """
    existing_link_result = await db.execute(
        select(models.SeasonRank).filter_by(
            season_id=season_id, rank_id=rank_data.rank_id
        )
    )
    if existing_link_result.scalars().first():
        return None

    new_season_rank = models.SeasonRank(
        season_id=season_id,
        rank_id=rank_data.rank_id,
        number=rank_data.number,
        required_points=rank_data.required_points,
    )
    db.add(new_season_rank)
    await db.commit()
    await db.refresh(new_season_rank)

    result = await db.execute(
        select(models.SeasonRank)
        .filter(models.SeasonRank.id == new_season_rank.id)
        .options(
            selectinload(models.SeasonRank.rank), selectinload(models.SeasonRank.season)
        )
    )
    return result.scalars().one()


async def get_season_rank_by_ids(
    db: AsyncSession, season_id: int, rank_id: int
) -> models.SeasonRank | None:
    """
    Retrieves a specific SeasonRank link by the season and rank IDs.
    """
    result = await db.execute(
        select(models.SeasonRank).filter_by(season_id=season_id, rank_id=rank_id)
    )
    return result.scalars().first()


async def get_ranks_for_season(
    db: AsyncSession, season_id: int
) -> list[models.SeasonRank]:
    """
    Retrieves a list of all ranks associated with a specific season.
    """
    result = await db.execute(
        select(models.SeasonRank)
        .filter(models.SeasonRank.season_id == season_id)
        .options(
            selectinload(models.SeasonRank.rank), selectinload(models.SeasonRank.season)
        )
    )
    return list(result.scalars().all())


async def update_season_rank(
    db: AsyncSession,
    season_rank: models.SeasonRank,
    update_data: schemas.SeasonRankUpdate,
) -> models.SeasonRank:
    """Updates the details for a rank within a season."""
    season_rank_id = season_rank.id

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(season_rank, key, value)

    db.add(season_rank)
    await db.commit()

    result = await db.execute(
        select(models.SeasonRank)
        .filter(models.SeasonRank.id == season_rank_id)
        .options(
            selectinload(models.SeasonRank.rank), selectinload(models.SeasonRank.season)
        )
    )
    return result.scalars().one()


async def remove_rank_from_season(
    db: AsyncSession, season_rank: models.SeasonRank
) -> None:
    """Removes the association between a rank and a season."""
    await db.delete(season_rank)
    await db.commit()
    return
