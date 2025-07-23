# ==============================================================================
# FILE: api/schemas/ranks.py
# ==============================================================================
# This file defines the Pydantic models for Rank data validation.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class RankBase(BaseModel):
    """The base schema for a rank, containing common fields."""

    name: str
    badge_url: Optional[str] = None


class RankCreate(RankBase):
    """Schema for data required when creating a new rank."""

    pass


class RankUpdate(BaseModel):
    """
    Schema for data that can be updated on a rank record.
    All fields are optional to allow for partial updates.
    """

    name: Optional[str] = None
    badge_url: Optional[str] = None


class Rank(RankBase):
    """
    The default response model when returning rank data.
    Includes the database ID and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
