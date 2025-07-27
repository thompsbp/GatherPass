# ==============================================================================
# FILE: api/crud/season_user_ranks.py
# ==============================================================================
# This file contains all the database functions for the SeasonUserRank association.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def award_rank_to_user(
    db: AsyncSession, user_id: int, season_rank_id: int
) -> models.SeasonUserRank | None:
    """
    Awards a specific season rank to a user.
    Returns None if the user has already been awarded this rank.
    """
    existing_award_result = await db.execute(
        select(models.SeasonUserRank).filter_by(
            user_id=user_id, season_rank_id=season_rank_id
        )
    )
    if existing_award_result.scalars().first():
        return None

    new_award = models.SeasonUserRank(
        user_id=user_id,
        season_rank_id=season_rank_id,
    )
    db.add(new_award)
    await db.commit()

    await db.refresh(new_award)
    new_award_id = new_award.id  # Now it's safe to access the ID.

    result = await db.execute(
        select(models.SeasonUserRank)
        .filter(models.SeasonUserRank.id == new_award_id)
        .options(
            selectinload(models.SeasonUserRank.user),
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.rank
            ),
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.season
            ),
        )
    )
    return result.scalars().one()


async def get_user_ranks_for_season(
    db: AsyncSession, season_id: int, user_id: int
) -> list[models.SeasonUserRank]:
    """
    Retrieves a list of all ranks a user has been awarded in a specific season.
    """
    result = await db.execute(
        select(models.SeasonUserRank)
        .join(models.SeasonRank)
        .filter(
            models.SeasonUserRank.user_id == user_id,
            models.SeasonRank.season_id == season_id,
        )
        .options(
            selectinload(models.SeasonUserRank.user),
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.rank
            ),
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.season
            ),
        )
    )
    return list(result.scalars().all())
