# ==============================================================================
# FILE: api/crud/summaries.py
# ==============================================================================
# This file contains complex database functions for generating summary data.

import asyncio

import crud
import models
import schemas
from sqlalchemy import func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def get_user_item_summary_for_season(
    db: AsyncSession, user_id: int, season_id: int
) -> list[schemas.UserItemSummary]:
    """
    Calculates the total quantity of each unique item a user has submitted
    for a specific season.
    """

    result = await db.execute(
        select(
            models.Item, func.sum(models.Submission.quantity).label("total_quantity")
        )
        .join(
            models.SeasonItem, models.Submission.season_item_id == models.SeasonItem.id
        )
        .join(models.Item, models.SeasonItem.item_id == models.Item.id)
        .filter(
            models.Submission.user_id == user_id,
            models.SeasonItem.season_id == season_id,
        )
        .group_by(models.Item.id)
        .order_by(models.Item.name.asc())
    )

    summary_list = [
        schemas.UserItemSummary(item=item, total_quantity=total_quantity)
        for item, total_quantity in result.all()
    ]
    return summary_list


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

    item_summary_task = get_user_item_summary_for_season(
        db, user_id=user_id, season_id=season_id
    )

    highest_rank_result, awarded_prizes_result, item_summary = await asyncio.gather(
        highest_rank_task, awarded_prizes_task, item_summary_task
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
        item_summary=item_summary,
    )

    return summary
