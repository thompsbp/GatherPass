# ==============================================================================
# FILE: api/crud/prizes.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Prize model.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_prize(
    db: AsyncSession, prize_data: schemas.PrizeCreate
) -> models.Prize:
    """Creates a new prize in the database."""
    new_prize = models.Prize(
        description=prize_data.description,
        value=prize_data.value,
        lodestone_id=prize_data.lodestone_id,
        discord_role=prize_data.discord_role,
    )
    db.add(new_prize)
    await db.commit()
    await db.refresh(new_prize)
    return new_prize


async def get_prize_by_id(db: AsyncSession, prize_id: int) -> models.Prize | None:
    """Retrieves a prize from the database by its primary key ID."""
    result = await db.execute(select(models.Prize).filter(models.Prize.id == prize_id))
    return result.scalars().first()


async def get_prizes(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> list[models.Prize]:
    """Retrieves a list of all prizes with pagination."""
    result = await db.execute(select(models.Prize).offset(offset).limit(limit))
    return list(result.scalars().all())


async def update_prize(
    db: AsyncSession,
    prize: models.Prize,
    update_data: schemas.PrizeUpdate,
) -> models.Prize:
    """Updates a prize's record."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(prize, key, value)

    db.add(prize)
    await db.commit()
    await db.refresh(prize)
    return prize


async def delete_prize(db: AsyncSession, prize: models.Prize) -> None:
    """Deletes a prize from the database."""
    await db.delete(prize)
    await db.commit()
    return
