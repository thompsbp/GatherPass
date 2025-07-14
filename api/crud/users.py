# ==============================================================================
# FILE: api/crud/users.py
# ==============================================================================
# This file contains all the database functions (CRUD) for the User model.

from typing import Union

import models
import schemas
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select


async def get_user_by_uuid(db: AsyncSession, user_uuid: str) -> models.User | None:
    """Retrieves a user from the database by their UUID"""
    result = await db.execute(select(models.User).filter(models.User.uuid == user_uuid))
    return result.scalars().first()


async def get_user_by_id(db: AsyncSession, user_id: int) -> models.User | None:
    """Retrieves a user from the database by their primary key ID."""
    result = await db.execute(select(models.User).filter(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_discord_id(
    db: AsyncSession, discord_id: int
) -> models.User | None:
    """Retrieves a user from the database by their Discord ID."""
    result = await db.execute(
        select(models.User).filter(models.User.discord_id == discord_id)
    )
    return result.scalars().first()


async def get_users(
    db: AsyncSession, offset: int = 0, limit: int = 100
) -> list[models.User]:
    """Retrieves a list of users with pagination."""
    result = await db.execute(select(models.User).offset(offset).limit(limit))
    return list(result.scalars().all())


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


async def update_user(
    db: AsyncSession,
    user: models.User,
    update_data: schemas.UserUpdate,
    actor: Union[models.User, schemas.Actor],
) -> models.User:
    """Updates a user's record."""
    update_dict = update_data.model_dump(exclude_unset=True)
    update_dict["updated_by"] = actor.id

    for key, value in update_dict.items():
        setattr(user, key, value)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def ban_user(
    db: AsyncSession, user: models.User, actor: Union[models.User, schemas.Actor]
) -> models.User:
    """Sets a user's status to 'banned'."""
    setattr(user, "status", "banned")
    setattr(user, "updated_by", actor.id)

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
