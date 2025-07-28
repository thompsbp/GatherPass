# ==============================================================================
# FILE: api/routers/items.py
# ==============================================================================
# This file contains all API endpoints related to item management.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/items",
    tags=["Items"],
)


@router.post("/", response_model=schemas.Item, status_code=status.HTTP_201_CREATED)
async def handle_create_item(
    item_data: schemas.ItemCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Creates a new item."""
    new_item = await crud.create_item(db=db, item_data=item_data)
    if new_item is None:
        raise HTTPException(
            status_code=400,
            detail="An item with this Lodestone ID already exists.",
        )
    return new_item


@router.get("/", response_model=List[schemas.Item])
async def handle_get_items(
    offset: int = 0,
    limit: int = 100,
    name: str | None = None,  # Add the optional query parameter
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a list of all items."""
    return await crud.get_items(db, offset=offset, limit=limit, name=name)


@router.get("/{item_id}", response_model=schemas.Item)
async def handle_get_item(
    item_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a single item by its ID."""
    item = await crud.get_item_by_id(db, item_id=item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return item


@router.patch("/{item_id}", response_model=schemas.Item)
async def handle_update_item(
    item_id: int,
    update_data: schemas.ItemUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates an existing item."""
    item_to_update = await crud.get_item_by_id(db, item_id=item_id)
    if item_to_update is None:
        raise HTTPException(status_code=404, detail="Item not found")

    return await crud.update_item(db, item=item_to_update, update_data=update_data)


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_delete_item(
    item_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Deletes an item."""
    item_to_delete = await crud.get_item_by_id(db, item_id=item_id)
    if item_to_delete is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await crud.delete_item(db, item=item_to_delete)
    return None
