# ==============================================================================
# FILE: api/routers/season_users.py
# ==============================================================================
# This file contains the nested API endpoints for managing user participation
# and progress within a season.
from typing import List, Optional

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
    - If `user_id` or `discord_id` is provided, the requester must be an admin.
    - If the payload is empty, the requester registers themself.
    """
    user_to_register: Optional[models.User] = None

    if user_data.user_id is not None:
        user_to_register = await crud.get_user_by_id(db, user_id=user_data.user_id)
    elif user_data.discord_id is not None:
        user_to_register = await crud.get_user_by_discord_id(
            db, discord_id=user_data.discord_id
        )
    else:
        user_to_register = current_user

    if not user_to_register:
        raise HTTPException(status_code=404, detail="User to be registered not found")

    if not (
        current_user.admin is True or int(current_user.id) == int(user_to_register.id)
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to register another user for a season.",
        )

    # 3. Ensure the season exists
    season = await crud.get_season_by_id(db, season_id=season_id)
    if not season:
        raise HTTPException(status_code=404, detail="Season not found")

    # 4. Perform the registration
    new_season_user = await crud.register_user_for_season(
        db, season_id=season_id, user_id=int(user_to_register.id), actor=current_user
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
