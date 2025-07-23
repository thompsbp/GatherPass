# ==============================================================================
# FILE: api/crud/items.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the Item model.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def create_item(
    db: AsyncSession, item_data: schemas.ItemCreate
) -> models.Item | None:
    """Creates a new item in the database."""
    existing_item = await db.execute(
        select(models.Item).filter(models.Item.lodestone_id == item_data.lodestone_id)
    )
    if existing_item.scalars().first():
        return None

    new_item = models.Item(
        name=item_data.name,
        lodestone_id=item_data.lodestone_id,
    )
    db.add(new_item)
    await db.commit()
    await db.refresh(new_item)
    return new_item


async def get_item_by_id(db: AsyncSession, item_id: int) -> models.Item | None:
    """Retrieves an item from the database by its primary key ID."""
    result = await db.execute(select(models.Item).filter(models.Item.id == item_id))
    return result.scalars().first()


async def get_items(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> list[models.Item]:
    """Retrieves a list of all items with pagination."""
    result = await db.execute(select(models.Item).offset(offset).limit(limit))
    return list(result.scalars().all())


async def update_item(
    db: AsyncSession,
    item: models.Item,
    update_data: schemas.ItemUpdate,
) -> models.Item:
    """Updates an item's record."""
    update_dict = update_data.model_dump(exclude_unset=True)

    for key, value in update_dict.items():
        setattr(item, key, value)

    db.add(item)
    await db.commit()
    await db.refresh(item)
    return item


async def delete_item(db: AsyncSession, item: models.Item) -> None:
    """Deletes an item from the database."""
    await db.delete(item)
    await db.commit()
    return
