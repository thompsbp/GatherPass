# ==============================================================================
# FILE: api/routers/season_prizes.py
# ==============================================================================
# This file contains the nested API endpoints for managing prizes associated
# with a specific rank within a season.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/seasons/{season_id}/ranks/{season_rank_id}/prizes",
    tags=["Season Prizes"],
)


@router.post("/", response_model=schemas.SeasonPrize)
async def handle_add_prize_to_season_rank(
    season_id: int,
    season_rank_id: int,
    prize_data: schemas.SeasonPrizeCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Associates a prize with a specific season rank."""
    # Ensure the season_rank and prize actually exist
    season_rank = await crud.get_season_rank_by_ids(
        db, season_id=season_id, rank_id=season_rank_id
    )
    if not season_rank:
        raise HTTPException(status_code=404, detail="Season rank not found")

    prize = await crud.get_prize_by_id(db, prize_id=prize_data.prize_id)
    if not prize:
        raise HTTPException(status_code=404, detail="Prize not found")

    new_season_prize = await crud.add_prize_to_season_rank(
        db, season_rank_id=season_rank.id, prize_id=prize_data.prize_id
    )
    if new_season_prize is None:
        raise HTTPException(
            status_code=400,
            detail="This prize is already associated with this season rank.",
        )
    return new_season_prize


@router.get("/", response_model=List[schemas.SeasonPrize])
async def handle_get_prizes_for_season_rank(
    season_rank_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all prizes for a specific season rank."""
    return await crud.get_prizes_for_season_rank(db, season_rank_id=season_rank_id)


@router.delete("/{prize_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_remove_prize_from_season_rank(
    season_rank_id: int,
    prize_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Removes the association between a prize and a season rank."""
    season_prize_to_delete = await crud.get_season_prize_by_ids(
        db, season_rank_id=season_rank_id, prize_id=prize_id
    )
    if season_prize_to_delete is None:
        raise HTTPException(
            status_code=404, detail="Prize is not associated with this season rank"
        )

    await crud.remove_prize_from_season_rank(db, season_prize=season_prize_to_delete)
    return None
