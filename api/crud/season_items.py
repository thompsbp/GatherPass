# ==============================================================================
# FILE: api/crud/season_items.py
# ==============================================================================
# This file contains all the database functions for the SeasonItem association.

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload


async def add_item_to_season(
    db: AsyncSession, season_id: int, item_data: schemas.SeasonItemCreate
) -> models.SeasonItem | None:
    """
    Associates an item with a season, setting its point value.
    Returns the new, fully-loaded SeasonItem object for serialization.
    """
    existing_link_result = await db.execute(
        select(models.SeasonItem).filter_by(
            season_id=season_id, item_id=item_data.item_id
        )
    )
    if existing_link_result.scalars().first():
        return None

    new_season_item = models.SeasonItem(
        season_id=season_id,
        item_id=item_data.item_id,
        point_value=item_data.point_value,
    )
    db.add(new_season_item)
    await db.commit()

    # --- The Permanent Fix ---
    # After committing, we must refresh the object to load its database state
    # (like the auto-generated ID) before we can use it again.
    await db.refresh(new_season_item)

    # Now that the object is "live", we can re-fetch it with its relationships
    # loaded for the API response.
    result = await db.execute(
        select(models.SeasonItem)
        .filter(models.SeasonItem.id == new_season_item.id)
        .options(
            selectinload(models.SeasonItem.item), selectinload(models.SeasonItem.season)
        )
    )
    return result.scalars().one()


# ... (The rest of the functions in this file are correct and do not need to be changed) ...


async def get_season_item_by_ids(
    db: AsyncSession, season_id: int, item_id: int
) -> models.SeasonItem | None:
    """
    Retrieves a specific SeasonItem link by the season and item IDs.
    """
    result = await db.execute(
        select(models.SeasonItem).filter_by(season_id=season_id, item_id=item_id)
    )
    return result.scalars().first()


async def get_items_for_season(
    db: AsyncSession, season_id: int
) -> list[models.SeasonItem]:
    """
    Retrieves a list of all items associated with a specific season,
    sorted alphabetically by the item's name.
    """
    result = await db.execute(
        select(models.SeasonItem)
        .join(models.Item)  # Join with the Item table to access its columns
        .filter(models.SeasonItem.season_id == season_id)
        .order_by(models.Item.name.asc())  # Sort by the item's name
        .options(
            selectinload(models.SeasonItem.item),
            selectinload(models.SeasonItem.season),
        )
    )
    return list(result.scalars().all())


async def update_season_item(
    db: AsyncSession,
    season_item: models.SeasonItem,
    update_data: schemas.SeasonItemUpdate,
) -> models.SeasonItem:
    """Updates the point value for an item within a season."""
    update_dict = update_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(season_item, key, value)

    db.add(season_item)
    await db.commit()
    await db.refresh(season_item)
    return season_item


async def remove_item_from_season(
    db: AsyncSession, season_item: models.SeasonItem
) -> None:
    """Removes the association between an item and a season."""
    await db.delete(season_item)
    await db.commit()
    return
