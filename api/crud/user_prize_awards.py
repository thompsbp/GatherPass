# ==============================================================================
# FILE: api/crud/user_prize_awards.py
# ==============================================================================
# This file contains all the database functions for the UserPrizeAward model.

from datetime import datetime, timezone
from typing import Optional

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def create_user_prize_award(
    db: AsyncSession, award_data: schemas.UserPrizeAwardCreate
) -> models.UserPrizeAward | None:
    """
    Creates a record that a user has been awarded a specific season prize.
    Returns None if this award already exists.
    """
    existing_award = await db.execute(
        select(models.UserPrizeAward).filter_by(
            user_id=award_data.user_id, season_prize_id=award_data.season_prize_id
        )
    )
    if existing_award.scalars().first():
        return None

    new_award = models.UserPrizeAward(
        user_id=award_data.user_id,
        season_prize_id=award_data.season_prize_id,
    )
    db.add(new_award)
    await db.commit()
    await db.refresh(new_award)

    # Re-fetch with all relationships eagerly loaded for the API response
    result = await db.execute(
        select(models.UserPrizeAward)
        .filter(models.UserPrizeAward.id == new_award.id)
        .options(
            selectinload(models.UserPrizeAward.user),
            selectinload(models.UserPrizeAward.season_prize).selectinload(
                models.SeasonPrize.prize
            ),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.rank),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.season),
        )
    )
    return result.scalars().one()


async def get_awards_for_user(
    db: AsyncSession, user_id: int
) -> list[models.UserPrizeAward]:
    """Retrieves a list of all prize awards for a specific user."""
    result = await db.execute(
        select(models.UserPrizeAward)
        .filter(models.UserPrizeAward.user_id == user_id)
        .options(
            selectinload(models.UserPrizeAward.user),
            selectinload(models.UserPrizeAward.season_prize).selectinload(
                models.SeasonPrize.prize
            ),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.rank),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.season),
        )
    )
    return list(result.scalars().all())


async def get_user_prize_award_by_id(
    db: AsyncSession, award_id: int
) -> models.UserPrizeAward | None:
    """Retrieves a single prize award record by its primary key ID."""
    result = await db.execute(
        select(models.UserPrizeAward).filter(models.UserPrizeAward.id == award_id)
    )
    return result.scalars().first()


async def update_user_prize_award(
    db: AsyncSession,
    award: models.UserPrizeAward,
    update_data: schemas.UserPrizeAwardUpdate,
    actor: models.User,
) -> models.UserPrizeAward:
    """Updates a prize award, typically to mark it as delivered."""
    # --- The Permanent Fix ---
    # 1. Capture the ID before the object's state is expired by the commit.
    award_id = award.id

    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(award, key, value)

    if update_data.delivered:
        setattr(award, "delivered_at", datetime.now(timezone.utc))
        setattr(award, "delivered_by", actor.discord_id)

    db.add(award)
    await db.commit()

    # 2. Use the safe, captured ID to re-fetch the fully-loaded object.
    result = await db.execute(
        select(models.UserPrizeAward)
        .filter(models.UserPrizeAward.id == award_id)
        .options(
            selectinload(models.UserPrizeAward.user),
            selectinload(models.UserPrizeAward.season_prize).selectinload(
                models.SeasonPrize.prize
            ),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.rank),
            selectinload(models.UserPrizeAward.season_prize)
            .selectinload(models.SeasonPrize.season_rank)
            .selectinload(models.SeasonRank.season),
        )
    )
    return result.scalars().one()
