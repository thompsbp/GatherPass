# ==============================================================================
# FILE: api/schemas/season_users.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonUser association,
# which represents a user's participation and progress in a season.
from typing import Optional

from pydantic import BaseModel, ConfigDict

from .seasons import Season
from .users import User


class SeasonUserBase(BaseModel):
    """The base schema for a season-user link, containing common fields."""

    total_points: int = 0


class SeasonUserCreate(BaseModel):
    """
    Schema for data required when registering a user for a season.
    If user_id is omitted, it defaults to the current authenticated user.
    """

    user_id: Optional[int] = None


class SeasonUser(SeasonUserBase):
    """
    The default response model when returning a user's progress in a season.
    This is a nested schema that includes the full User and Season objects.
    """

    id: int
    user: User
    season: Season

    model_config = ConfigDict(from_attributes=True)
