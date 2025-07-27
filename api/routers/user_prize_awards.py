# ==============================================================================
# FILE: api/routers/user_prize_awards.py
# ==============================================================================
# This file contains the API endpoints for managing prize awards for users.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

user_awards_router = APIRouter(
    prefix="/users/{user_id}/prize-awards",
    tags=["User Prize Awards"],
)

awards_router = APIRouter(
    prefix="/prize-awards",
    tags=["User Prize Awards"],
)


@user_awards_router.post("/", response_model=schemas.UserPrizeAward)
async def handle_create_user_prize_award(
    user_id: int,
    award_data: schemas.UserPrizeAwardCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Creates a record that a user has been awarded a prize."""
    if user_id != award_data.user_id:
        raise HTTPException(
            status_code=400, detail="User ID in path does not match body"
        )

    user = await crud.get_user_by_id(db, user_id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    new_award = await crud.create_user_prize_award(db, award_data=award_data)
    if new_award is None:
        raise HTTPException(
            status_code=400,
            detail="This prize has already been awarded to this user.",
        )
    return new_award


@user_awards_router.get("/", response_model=List[schemas.UserPrizeAward])
async def handle_get_awards_for_user(
    user_id: int,
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all prize awards for a specific user."""
    if not (current_user.admin is True or int(current_user.id) == user_id):
        raise HTTPException(
            status_code=403, detail="Not authorized to view these awards"
        )

    return await crud.get_awards_for_user(db, user_id=user_id)


@awards_router.patch("/{award_id}", response_model=schemas.UserPrizeAward)
async def handle_update_user_prize_award(
    award_id: int,
    update_data: schemas.UserPrizeAwardUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates a prize award, e.g., to mark it as delivered."""
    award_to_update = await crud.get_user_prize_award_by_id(db, award_id=award_id)
    if award_to_update is None:
        raise HTTPException(status_code=404, detail="Prize award not found")

    return await crud.update_user_prize_award(
        db, award=award_to_update, update_data=update_data, actor=admin_user
    )
