# ==============================================================================
# FILE: api/crud/season_user_ranks.py
# ==============================================================================
# This file contains the database logic for promoting and viewing user ranks.

import asyncio

import crud
import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def promote_user_to_rank(
    db: AsyncSession, user_id: int, season_id: int, target_season_rank_id: int
) -> dict:
    """
    Awards a user a target rank, backfilling any missed ranks and awarding
    all associated prizes. Returns a dictionary containing the newly awarded ranks and prizes.
    """
    all_season_ranks_task = crud.get_ranks_for_season(db, season_id=season_id)
    user_awards_task = get_user_ranks_for_season(
        db, user_id=user_id, season_id=season_id
    )
    all_season_prizes_task = crud.get_prizes_for_season(db, season_id=season_id)

    all_season_ranks, user_awards, all_season_prizes = await asyncio.gather(
        all_season_ranks_task, user_awards_task, all_season_prizes_task
    )

    target_rank = next(
        (sr for sr in all_season_ranks if sr.id == target_season_rank_id), None
    )
    if not target_rank:
        return {"awarded_ranks": [], "awarded_prizes": []}

    awarded_rank_ids = {award.season_rank_id for award in user_awards}
    ranks_to_award = [
        models.SeasonUserRank(user_id=user_id, season_rank_id=sr.id)
        for sr in all_season_ranks
        if sr.number <= target_rank.number and sr.id not in awarded_rank_ids
    ]

    if not ranks_to_award:
        return {"awarded_ranks": [], "awarded_prizes": []}

    prizes_by_rank_id = {sp.season_rank_id: sp for sp in all_season_prizes}
    prizes_to_award = [
        models.UserPrizeAward(
            user_id=user_id, season_prize_id=prizes_by_rank_id[award.season_rank_id].id
        )
        for award in ranks_to_award
        if award.season_rank_id in prizes_by_rank_id
    ]

    db.add_all(ranks_to_award + prizes_to_award)
    await db.commit()

    newly_awarded_rank_ids = [award.id for award in ranks_to_award]
    newly_awarded_prize_ids = [award.id for award in prizes_to_award]

    ranks_result = await db.execute(
        select(models.SeasonUserRank)
        .filter(models.SeasonUserRank.id.in_(newly_awarded_rank_ids))
        .options(
            selectinload(models.SeasonUserRank.season_rank).selectinload(
                models.SeasonRank.rank
            )
        )
    )
    prizes_result = await db.execute(
        select(models.UserPrizeAward)
        .filter(models.UserPrizeAward.id.in_(newly_awarded_prize_ids))
        .options(
            selectinload(models.UserPrizeAward.season_prize).selectinload(
                models.SeasonPrize.prize
            )
        )
    )

    return {
        "awarded_ranks": list(ranks_result.scalars().all()),
        "awarded_prizes": list(prizes_result.scalars().all()),
    }


async def get_all_awarded_ranks_for_season(
    db: AsyncSession, season_id: int
) -> list[models.SeasonUserRank]:
    """
    Retrieves all rank awards for all users within a specific season.
    """
    result = await db.execute(
        select(models.SeasonUserRank)
        .join(models.SeasonRank)
        .filter(models.SeasonRank.season_id == season_id)
    )
    return list(result.scalars().all())


async def get_user_ranks_for_season(
    db: AsyncSession, season_id: int, user_id: int
) -> list[models.SeasonUserRank]:
    """Retrieves a list of all ranks a user has been awarded in a specific season."""
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
