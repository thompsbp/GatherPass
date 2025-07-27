# ==============================================================================
# FILE: api/routers/season_users.py
# ==============================================================================
# This file contains the nested API endpoints for managing user participation
# and progress within a season.
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
    tags=["Season Users (Leaderboard)"],
)


@router.post("/{season_id}/users", response_model=schemas.SeasonUser)
async def handle_register_user_for_season(
    season_id: int,
    user_data: schemas.SeasonUserCreate,
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Registers a user for a specific season.
    - If `user_id` is provided, the requester must be an admin.
    - If `user_id` is omitted, the requester registers themself.
    """
    current_user_id = current_user.id

    user_id_to_register: int

    if user_data.user_id is None:
        # Case 1: user_id is omitted. The user is registering themself.
        user_id_to_register = current_user_id
    else:
        # Case 2: user_id is provided. Requester must be an admin or acting on themself.
        if not (current_user.admin is True or current_user_id == user_data.user_id):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to register another user for a season.",
            )
        user_id_to_register = user_data.user_id

    season = await crud.get_season_by_id(db, season_id=season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")
    user_to_register = await crud.get_user_by_id(db, user_id=user_id_to_register)
    if not user_to_register:
        raise HTTPException(status_code=404, detail="User to be registered not found")

    new_season_user = await crud.register_user_for_season(
        db, season_id=season_id, user_id=user_id_to_register, actor=current_user
    )
    if new_season_user is None:
        raise HTTPException(
            status_code=400,
            detail="User is already registered for this season.",
        )
    return new_season_user


@router.get("/{season_id}/users", response_model=List[schemas.SeasonUser])
async def handle_get_all_users_for_season(
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves the leaderboard for a specific season."""
    return await crud.get_all_users_for_season(db, season_id=season_id)


@router.get("/{season_id}/users/{user_id}", response_model=schemas.SeasonUser)
async def handle_get_user_progress_in_season(
    season_id: int,
    user_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves a single user's progress in a season."""
    season_user = await crud.get_user_progress_in_season(
        db, season_id=season_id, user_id=user_id
    )
    if season_user is None:
        raise HTTPException(status_code=404, detail="User not found in this season")
    return season_user
