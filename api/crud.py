# ==============================================================================
# FILE: api/crud.py
# ==============================================================================
# This file contains all the functions that interact directly with the database.

from datetime import datetime, timedelta

import models
import schemas
from sqlalchemy import and_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

# --- User CRUD ---


async def get_user_by_discord_id(
    db: AsyncSession, discord_id: int
) -> models.User | None:
    """Retrieves a user from the database by their Discord ID."""
    result = await db.execute(
        select(models.User).filter(models.User.discord_id == discord_id)
    )
    return result.scalars().first()


async def create_user(
    db: AsyncSession, user_data: schemas.UserCreate, actor: schemas.Actor
) -> models.User:
    """Creates a new user in the database."""
    new_user = models.User(
        discord_id=user_data.discord_id,
        in_game_name=user_data.in_game_name,
        lodestone_id=user_data.lodestone_id,
        created_by=actor.id,
        updated_by=actor.id,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user
