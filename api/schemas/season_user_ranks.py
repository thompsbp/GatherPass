# ==============================================================================
# FILE: api/schemas/season_user_ranks.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonUserRank association,
# representing a rank awarded to a user in a season.

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from .season_ranks import SeasonRank
from .users import User


class SeasonUserRankCreate(BaseModel):
    """Schema for data required when awarding a rank to a user."""

    # The ID of the specific SeasonRank link (e.g., "Bronze in Season 1")
    season_rank_id: int


class SeasonUserRank(BaseModel):
    """
    The default response model when returning a user's awarded rank.
    This is a nested schema for a rich API response.
    """

    id: int
    user: User
    season_rank: SeasonRank
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SeasonRankPromotionCreate(BaseModel):
    """Schema for the body of a promotion request."""

    season_rank_id: int
