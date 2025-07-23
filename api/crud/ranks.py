# ==============================================================================
# FILE: api/crud/ranks.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Rank model.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_rank(db: AsyncSession, rank_data: schemas.RankCreate) -> models.Rank:
    """Creates a new rank in the database."""
    new_rank = models.Rank(
        name=rank_data.name,
        badge_url=rank_data.badge_url,
    )
    db.add(new_rank)
    await db.commit()
    await db.refresh(new_rank)
    return new_rank


async def get_rank_by_id(db: AsyncSession, rank_id: int) -> models.Rank | None:
    """Retrieves a rank from the database by its primary key ID."""
    result = await db.execute(select(models.Rank).filter(models.Rank.id == rank_id))
    return result.scalars().first()


async def get_ranks(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> list[models.Rank]:
    """Retrieves a list of all ranks with pagination."""
    result = await db.execute(select(models.Rank).offset(offset).limit(limit))
    return list(result.scalars().all())


async def update_rank(
    db: AsyncSession,
    rank: models.Rank,
    update_data: schemas.RankUpdate,
) -> models.Rank:
    """Updates a rank's record."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(rank, key, value)

    db.add(rank)
    await db.commit()
    await db.refresh(rank)
    return rank


async def delete_rank(db: AsyncSession, rank: models.Rank) -> None:
    """Deletes a rank from the database."""
    await db.delete(rank)
    await db.commit()
    return
