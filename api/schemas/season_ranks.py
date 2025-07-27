# ==============================================================================
# FILE: api/schemas/season_ranks.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonRank association.

from typing import Optional

from pydantic import BaseModel, ConfigDict

from .ranks import Rank
from .seasons import Season


class SeasonRankBase(BaseModel):
    """The base schema for a season-rank link, containing common fields."""

    number: int
    required_points: int


class SeasonRankCreate(SeasonRankBase):
    """Schema for data required when associating a rank with a season."""

    # We'll need the ID of the rank being added.
    rank_id: int


class SeasonRankUpdate(BaseModel):
    """
    Schema for data that can be updated on a season-rank link.
    """

    number: Optional[int] = None
    required_points: Optional[int] = None


class SeasonRank(SeasonRankBase):
    """
    The default response model when returning season-rank data.
    This is a nested schema that includes the full Rank and Season objects.
    """

    id: int
    rank: Rank  # Nested Rank object
    season: Season  # Nested Season object

    model_config = ConfigDict(from_attributes=True)
