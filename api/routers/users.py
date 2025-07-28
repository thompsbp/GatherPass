# ==============================================================================
# FILE: api/routers/users.py
# ==============================================================================
# This file contains all API endpoints related to user management.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_bot_auth
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/users",
    tags=["Users"],
)


@router.post("/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def handle_create_user(
    user_data: schemas.UserCreate,
    is_bot_authenticated: bool = Depends(require_bot_auth),
    db: AsyncSession = Depends(get_db),
):
    """(Bot-Only) Registers a new user."""
    db_user = await crud.get_user_by_discord_id(db, discord_id=user_data.discord_id)
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="A user with this Discord ID is already registered.",
        )

    bot_actor = schemas.Actor(id="bot", is_bot=True)
    return await crud.create_user(db=db, user_data=user_data, actor=bot_actor)


@router.get("/", response_model=List[schemas.User])
async def handle_get_users(
    offset: int = 0,
    limit: int = 100,
    acting_admin: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Gets a list of all users."""
    return await crud.get_users(db, offset=offset, limit=limit)


@router.get("/{user_id}", response_model=schemas.User)
async def handle_get_user(
    user_id: int,
    acting_admin: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Gets a single user by their ID."""
    user_to_get = await crud.get_user_by_id(db, user_id=user_id)
    if user_to_get is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user_to_get


@router.patch("/{user_id}", response_model=schemas.User)
async def handle_update_user(
    user_id: int,
    update_data: schemas.UserUpdate,
    acting_admin: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates a user's status or admin privileges."""
    user_to_update = await crud.get_user_by_id(db, user_id=user_id)
    if user_to_update is None:
        raise HTTPException(status_code=404, detail="User not found")

    return await crud.update_user(
        db, user=user_to_update, update_data=update_data, actor=acting_admin
    )


@router.delete("/{user_id}", response_model=schemas.User)
async def handle_ban_user(
    user_id: int,
    acting_admin: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) 'Deletes' a user by setting their status to 'banned'."""
    user_to_ban = await crud.get_user_by_id(db, user_id=user_id)
    if user_to_ban is None:
        raise HTTPException(status_code=404, detail="User not found")

    return await crud.ban_user(db, user=user_to_ban, actor=acting_admin)
