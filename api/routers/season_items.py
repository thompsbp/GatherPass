# ==============================================================================
# FILE: api/routers/season_items.py
# ==============================================================================
# This file contains the nested API endpoints for managing items within a season.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/seasons",
    tags=["Season Items"],
)


@router.post("/{season_id}/items", response_model=schemas.SeasonItem)
async def handle_add_item_to_season(
    season_id: int,
    item_data: schemas.SeasonItemCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Adds an item to a specific season with a point value."""
    season = await crud.get_season_by_id(db, season_id=season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    item = await crud.get_item_by_id(db, item_id=item_data.item_id)
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")

    new_season_item = await crud.add_item_to_season(
        db, season_id=season_id, item_data=item_data
    )
    if new_season_item is None:
        raise HTTPException(
            status_code=400,
            detail="This item is already in this season.",
        )
    return new_season_item


@router.get("/{season_id}/items", response_model=List[schemas.SeasonItem])
async def handle_get_items_for_season(
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all items associated with a specific season."""
    return await crud.get_items_for_season(db, season_id=season_id)


@router.patch("/{season_id}/items/{item_id}", response_model=schemas.SeasonItem)
async def handle_update_season_item(
    season_id: int,
    item_id: int,
    update_data: schemas.SeasonItemUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates the point value of an item within a season."""
    season_item_to_update = await crud.get_season_item_by_ids(
        db, season_id=season_id, item_id=item_id
    )
    if season_item_to_update is None:
        raise HTTPException(status_code=404, detail="Item not found in this season")

    return await crud.update_season_item(
        db, season_item=season_item_to_update, update_data=update_data
    )


@router.delete("/{season_id}/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_remove_item_from_season(
    season_id: int,
    item_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Removes an item from a season."""
    season_item_to_delete = await crud.get_season_item_by_ids(
        db, season_id=season_id, item_id=item_id
    )
    if season_item_to_delete is None:
        raise HTTPException(status_code=404, detail="Item not found in this season")

    await crud.remove_item_from_season(db, season_item=season_item_to_delete)
    return None
