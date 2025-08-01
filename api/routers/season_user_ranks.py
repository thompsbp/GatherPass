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
    "/users/{user_id}/seasons/{season_id}/promote",
    response_model=schemas.PromotionResult,
)
async def handle_promote_user_to_rank(
    user_id: int,
    season_id: int,
    promotion_data: schemas.SeasonRankPromotionCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    (Admin) Promotes a user to a target rank, backfilling any missed ranks and prizes.
    """
    promotion_result_data = await crud.promote_user_to_rank(
        db,
        user_id=user_id,
        season_id=season_id,
        target_season_rank_id=promotion_data.season_rank_id,
    )

    if not promotion_result_data["awarded_ranks"]:
        raise HTTPException(
            status_code=400,
            detail="Promotion failed. The user may already have this rank or a higher one, or the target rank is not part of this season.",
        )

    return schemas.PromotionResult(**promotion_result_data)


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
