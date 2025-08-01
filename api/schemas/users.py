# ==============================================================================
# FILE: api/schemas/users.py
# ==============================================================================
# This file defines the Pydantic models for User data validation.

from typing import Optional

from pydantic import BaseModel, ConfigDict


class UserCreate(BaseModel):
    """Schema for data required when registering a new user."""

    discord_id: int
    in_game_name: str
    lodestone_id: str


class UserUpdate(BaseModel):
    """Schema for data that can be updated on a user record."""

    status: Optional[str] = None
    admin: Optional[bool] = None


class User(BaseModel):
    """The default response model when returning user data."""

    id: int
    uuid: str
    discord_id: int
    in_game_name: Optional[str]
    lodestone_id: str
    status: str
    admin: bool

    model_config = ConfigDict(from_attributes=True)


class UserIdentifier(BaseModel):
    """A lightweight schema for identifying a user by name."""

    in_game_name: Optional[str] = "Unknown User"
