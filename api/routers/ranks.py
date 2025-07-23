# ==============================================================================
# FILE: api/routers/ranks.py
# ==============================================================================
# This file contains all API endpoints related to rank management.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/ranks",
    tags=["Ranks"],
)


@router.post("/", response_model=schemas.Rank, status_code=status.HTTP_201_CREATED)
async def handle_create_rank(
    rank_data: schemas.RankCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Creates a new rank."""
    return await crud.create_rank(db=db, rank_data=rank_data)


@router.get("/", response_model=List[schemas.Rank])
async def handle_get_ranks(
    offset: int = 0,
    limit: int = 100,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a list of all ranks."""
    return await crud.get_ranks(db, offset=offset, limit=limit)


@router.get("/{rank_id}", response_model=schemas.Rank)
async def handle_get_rank(
    rank_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a single rank by its ID."""
    rank = await crud.get_rank_by_id(db, rank_id=rank_id)
    if rank is None:
        raise HTTPException(status_code=404, detail="Rank not found")
    return rank


@router.patch("/{rank_id}", response_model=schemas.Rank)
async def handle_update_rank(
    rank_id: int,
    update_data: schemas.RankUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates an existing rank."""
    rank_to_update = await crud.get_rank_by_id(db, rank_id=rank_id)
    if rank_to_update is None:
        raise HTTPException(status_code=404, detail="Rank not found")

    return await crud.update_rank(db, rank=rank_to_update, update_data=update_data)


@router.delete("/{rank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_delete_rank(
    rank_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Deletes a rank."""
    rank_to_delete = await crud.get_rank_by_id(db, rank_id=rank_id)
    if rank_to_delete is None:
        raise HTTPException(status_code=404, detail="Rank not found")

    await crud.delete_rank(db, rank=rank_to_delete)
    return None
