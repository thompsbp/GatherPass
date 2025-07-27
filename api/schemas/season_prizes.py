# ==============================================================================
# FILE: api/schemas/season_prizes.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonPrize association.

from pydantic import BaseModel, ConfigDict

# Import base schemas for nesting
from .prizes import Prize
from .season_ranks import SeasonRank


class SeasonPrizeCreate(BaseModel):
    """Schema for data required when associating a prize with a season rank."""

    prize_id: int


class SeasonPrize(BaseModel):
    """
    The default response model when returning a prize for a season rank.
    This is a nested schema for a rich API response.
    """

    id: int
    prize: Prize  # Nested Prize object
    season_rank: SeasonRank  # Nested SeasonRank object

    model_config = ConfigDict(from_attributes=True)
