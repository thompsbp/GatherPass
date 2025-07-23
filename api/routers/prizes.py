# = a============================================================================
# FILE: api/routers/prizes.py
# ==============================================================================
# This file contains all API endpoints related to prize management.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/prizes",
    tags=["Prizes"],
)


@router.post("/", response_model=schemas.Prize, status_code=status.HTTP_201_CREATED)
async def handle_create_prize(
    prize_data: schemas.PrizeCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Creates a new prize."""
    return await crud.create_prize(db=db, prize_data=prize_data)


@router.get("/", response_model=List[schemas.Prize])
async def handle_get_prizes(
    offset: int = 0,
    limit: int = 100,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a list of all prizes."""
    return await crud.get_prizes(db, offset=offset, limit=limit)


@router.get("/{prize_id}", response_model=schemas.Prize)
async def handle_get_prize(
    prize_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a single prize by its ID."""
    prize = await crud.get_prize_by_id(db, prize_id=prize_id)
    if prize is None:
        raise HTTPException(status_code=404, detail="Prize not found")
    return prize


@router.patch("/{prize_id}", response_model=schemas.Prize)
async def handle_update_prize(
    prize_id: int,
    update_data: schemas.PrizeUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates an existing prize."""
    prize_to_update = await crud.get_prize_by_id(db, prize_id=prize_id)
    if prize_to_update is None:
        raise HTTPException(status_code=404, detail="Prize not found")

    return await crud.update_prize(db, prize=prize_to_update, update_data=update_data)


@router.delete("/{prize_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_delete_prize(
    prize_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Deletes a prize."""
    prize_to_delete = await crud.get_prize_by_id(db, prize_id=prize_id)
    if prize_to_delete is None:
        raise HTTPException(status_code=404, detail="Prize not found")

    await crud.delete_prize(db, prize=prize_to_delete)
    return None
