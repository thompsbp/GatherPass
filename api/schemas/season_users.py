# ==============================================================================
# FILE: api/schemas/season_users.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonUser association.

from typing import Optional

from pydantic import BaseModel, ConfigDict, model_validator

from .seasons import Season
from .users import User


class SeasonUserBase(BaseModel):
    """The base schema for a season-user link, containing common fields."""

    total_points: int = 0


class SeasonUserCreate(BaseModel):
    """
    Schema for data required when registering a user for a season.
    - If user_id or discord_id is omitted, it defaults to the current authenticated user.
    - Providing both user_id and discord_id is an error.
    """

    user_id: Optional[int] = None
    discord_id: Optional[int] = None

    @model_validator(mode="before")
    @classmethod
    def check_one_id_provided(cls, data):
        """Ensures that only one of the ID fields is provided."""
        if isinstance(data, dict):
            if (
                "user_id" in data
                and data["user_id"] is not None
                and "discord_id" in data
                and data["discord_id"] is not None
            ):
                raise ValueError("Only one of user_id or discord_id should be provided")
        return data


class SeasonUser(SeasonUserBase):
    """
    The default response model when returning a user's progress in a season.
    """

    id: int
    user: User
    season: Season

    model_config = ConfigDict(from_attributes=True)
