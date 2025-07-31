# ==============================================================================
# FILE: api/crud/season_prizes.py
# ==============================================================================
# This file contains all the database functions for the SeasonPrize association.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def add_prize_to_season_rank(
    db: AsyncSession, season_rank_id: int, prize_id: int
) -> models.SeasonPrize | None:
    """
    Associates a prize with a specific season rank.
    Returns None if the prize is already associated with this season rank.
    """
    # Check for an existing link
    existing_link_result = await db.execute(
        select(models.SeasonPrize).filter_by(
            season_rank_id=season_rank_id, prize_id=prize_id
        )
    )
    if existing_link_result.scalars().first():
        return None

    new_season_prize = models.SeasonPrize(
        season_rank_id=season_rank_id,
        prize_id=prize_id,
    )
    db.add(new_season_prize)
    await db.commit()
    await db.refresh(new_season_prize)

    result = await db.execute(
        select(models.SeasonPrize)
        .filter(models.SeasonPrize.id == new_season_prize.id)
        .options(
            selectinload(models.SeasonPrize.prize),
            selectinload(models.SeasonPrize.season_rank).selectinload(
                models.SeasonRank.rank
            ),
            selectinload(models.SeasonPrize.season_rank).selectinload(
                models.SeasonRank.season
            ),
        )
    )
    return result.scalars().one()


async def get_season_prize_by_ids(
    db: AsyncSession, season_rank_id: int, prize_id: int
) -> models.SeasonPrize | None:
    """Retrieves a specific SeasonPrize link by the season_rank and prize IDs."""
    result = await db.execute(
        select(models.SeasonPrize).filter_by(
            season_rank_id=season_rank_id, prize_id=prize_id
        )
    )
    return result.scalars().first()


async def get_prizes_for_season(
    db: AsyncSession, season_id: int
) -> list[models.SeasonPrize]:
    """
    Retrieves a list of all prizes for a specific season, sorted by
    rank number and then by prize description.
    """
    result = await db.execute(
        select(models.SeasonPrize)
        .join(models.SeasonRank)
        .join(models.Prize)
        .filter(models.SeasonRank.season_id == season_id)
        .order_by(models.SeasonRank.number.asc(), models.Prize.description.asc())
        .options(
            selectinload(models.SeasonPrize.prize),
            selectinload(models.SeasonPrize.season_rank).selectinload(
                models.SeasonRank.rank
            ),
            selectinload(models.SeasonPrize.season_rank).selectinload(
                models.SeasonRank.season
            ),
        )
    )
    return list(result.scalars().all())


async def get_prizes_for_season_rank(
    db: AsyncSession, season_rank_id: int
) -> list[models.SeasonPrize]:
    """Retrieves a list of all prizes for a specific season rank."""
    result = await db.execute(
        select(models.SeasonPrize)
        .filter(models.SeasonPrize.season_rank_id == season_rank_id)
        .options(
            selectinload(models.SeasonPrize.prize),
            selectinload(models.SeasonPrize.season_rank),
        )
    )
    return list(result.scalars().all())


async def remove_prize_from_season_rank(
    db: AsyncSession, season_prize: models.SeasonPrize
) -> None:
    """Removes the association between a prize and a season rank."""
    await db.delete(season_prize)
    await db.commit()
    return
