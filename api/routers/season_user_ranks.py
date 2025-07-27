# ==============================================================================
# FILE: api/routers/season_user_ranks.py
# ==============================================================================
# This file contains the nested API endpoints for managing ranks awarded to
# users within a season.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Season User Ranks"],
)


@router.post(
    "/users/{user_id}/seasons/{season_id}/ranks", response_model=schemas.SeasonUserRank
)
async def handle_award_rank_to_user(
    user_id: int,
    season_id: int,
    rank_award_data: schemas.SeasonUserRankCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Awards a specific season rank to a user."""
    user_to_award = await crud.get_user_by_id(db, user_id=user_id)
    if not user_to_award:
        raise HTTPException(status_code=404, detail="User not found")

    season_rank_to_award = await crud.get_season_rank_by_ids(
        db, season_id=season_id, rank_id=rank_award_data.season_rank_id
    )
    if not season_rank_to_award:
        raise HTTPException(
            status_code=404, detail="That rank is not part of this season"
        )

    new_award = await crud.award_rank_to_user(
        db, user_id=user_id, season_rank_id=season_rank_to_award.id
    )
    if new_award is None:
        raise HTTPException(
            status_code=400,
            detail="User has already been awarded this rank.",
        )
    return new_award


@router.get(
    "/users/{user_id}/seasons/{season_id}/ranks",
    response_model=List[schemas.SeasonUserRank],
)
async def handle_get_user_ranks_for_season(
    user_id: int,
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all ranks a user has earned in a season."""
    return await crud.get_user_ranks_for_season(
        db, user_id=user_id, season_id=season_id
    )
