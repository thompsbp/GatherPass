# ==============================================================================
# FILE: api/crud/summaries.py
# ==============================================================================
# This file contains complex database functions for generating summary data.

import asyncio

import crud
import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def get_user_season_summary(
    db: AsyncSession, user_id: int, season_id: int
) -> schemas.UserSeasonSummary | None:
    """
    Gathers a complete summary of a user's progress and rewards for a season.
    Returns None if the user is not registered for the season.
    """
    season_user = await crud.get_user_progress_in_season(
        db, season_id=season_id, user_id=user_id
    )
    if not season_user:
        return None

    highest_rank_task = db.execute(
        select(models.SeasonUserRank)
        .join(models.SeasonRank)
        .filter(
            models.SeasonUserRank.user_id == user_id,
            models.SeasonRank.season_id == season_id,
        )
        .order_by(models.SeasonRank.number.desc())
        .limit(1)
        .options(
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.rank
            )
        )
    )

    awarded_prizes_task = db.execute(
        select(models.UserPrizeAward)
        .join(models.SeasonPrize)
        .join(models.SeasonRank)
        .filter(
            models.UserPrizeAward.user_id == user_id,
            models.SeasonRank.season_id == season_id,
        )
        .options(
            selectinload(models.UserPrizeAward.season_prize).selectinload(
                models.SeasonPrize.prize
            )
        )
    )

    highest_rank_result, awarded_prizes_result = await asyncio.gather(
        highest_rank_task, awarded_prizes_task
    )

    highest_awarded_rank_record = highest_rank_result.scalars().first()
    awarded_prizes_records = awarded_prizes_result.scalars().all()

    summary = schemas.UserSeasonSummary(
        user_id=user_id,
        season_id=season_id,
        total_points=season_user.total_points,
        current_rank=(
            highest_awarded_rank_record.season_rank.rank
            if highest_awarded_rank_record
            else None
        ),
        awarded_prizes=[award.season_prize.prize for award in awarded_prizes_records],
    )

    return summary
