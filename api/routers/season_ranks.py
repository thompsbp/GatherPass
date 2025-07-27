# ==============================================================================
# FILE: api/routers/season_ranks.py
# ==============================================================================
# This file contains the nested API endpoints for managing ranks within a season.

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
    tags=["Season Ranks"],
)


@router.post("/{season_id}/ranks", response_model=schemas.SeasonRank)
async def handle_add_rank_to_season(
    season_id: int,
    rank_data: schemas.SeasonRankCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Adds a rank to a specific season with requirements."""
    # First, ensure the season and rank actually exist
    season = await crud.get_season_by_id(db, season_id=season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    rank = await crud.get_rank_by_id(db, rank_id=rank_data.rank_id)
    if not rank:
        raise HTTPException(status_code=404, detail="Rank not found")

    new_season_rank = await crud.add_rank_to_season(
        db, season_id=season_id, rank_data=rank_data
    )
    if new_season_rank is None:
        raise HTTPException(
            status_code=400,
            detail="This rank is already in this season.",
        )
    return new_season_rank


@router.get("/{season_id}/ranks", response_model=List[schemas.SeasonRank])
async def handle_get_ranks_for_season(
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all ranks associated with a specific season."""
    return await crud.get_ranks_for_season(db, season_id=season_id)


@router.patch("/{season_id}/ranks/{rank_id}", response_model=schemas.SeasonRank)
async def handle_update_season_rank(
    season_id: int,
    rank_id: int,
    update_data: schemas.SeasonRankUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates the requirements of a rank within a season."""
    season_rank_to_update = await crud.get_season_rank_by_ids(
        db, season_id=season_id, rank_id=rank_id
    )
    if season_rank_to_update is None:
        raise HTTPException(status_code=404, detail="Rank not found in this season")

    return await crud.update_season_rank(
        db, season_rank=season_rank_to_update, update_data=update_data
    )


@router.delete("/{season_id}/ranks/{rank_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_remove_rank_from_season(
    season_id: int,
    rank_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Removes a rank from a season."""
    season_rank_to_delete = await crud.get_season_rank_by_ids(
        db, season_id=season_id, rank_id=rank_id
    )
    if season_rank_to_delete is None:
        raise HTTPException(status_code=404, detail="Rank not found in this season")

    await crud.remove_rank_from_season(db, season_rank=season_rank_to_delete)
    return None
