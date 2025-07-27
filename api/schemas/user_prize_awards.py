# ==============================================================================
# FILE: api/schemas/user_prize_awards.py
# ==============================================================================
# This file defines the Pydantic models for the UserPrizeAward record,
# which tracks the delivery of prizes to users.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# Import base schemas for nesting
from .season_prizes import SeasonPrize
from .users import User


class UserPrizeAwardBase(BaseModel):
    """The base schema for a prize award record."""

    delivered: bool = False
    notes: Optional[str] = None


class UserPrizeAwardCreate(BaseModel):
    """Schema for data required when creating a new prize award record."""

    user_id: int
    season_prize_id: int


class UserPrizeAwardUpdate(BaseModel):
    """
    Schema for data that can be updated on a prize award record.
    Typically used to mark a prize as delivered.
    """

    delivered: Optional[bool] = None
    notes: Optional[str] = None


class UserPrizeAward(UserPrizeAwardBase):
    """
    The default response model when returning a prize award record.
    This is a nested schema for a rich API response.
    """

    id: int
    user: User  # Nested User object
    season_prize: SeasonPrize  # Nested SeasonPrize object
    awarded_at: datetime
    delivered_at: Optional[datetime] = None
    delivered_by: Optional[int] = None

    model_config = ConfigDict(from_attributes=True)
