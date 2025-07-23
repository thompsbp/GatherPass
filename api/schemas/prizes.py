# ==============================================================================
# FILE: api/schemas/prizes.py
# ==============================================================================
# This file defines the Pydantic models for Prize data validation.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class PrizeBase(BaseModel):
    """The base schema for a prize, containing common fields."""

    description: str
    value: Optional[int] = None
    lodestone_id: Optional[str] = None
    discord_role: Optional[int] = None


class PrizeCreate(PrizeBase):
    """Schema for data required when creating a new prize."""

    pass


class PrizeUpdate(BaseModel):
    """
    Schema for data that can be updated on a prize record.
    All fields are optional to allow for partial updates.
    """

    description: Optional[str] = None
    value: Optional[int] = None
    lodestone_id: Optional[str] = None
    discord_role: Optional[int] = None


class Prize(PrizeBase):
    """
    The default response model when returning prize data.
    Includes the database ID and timestamps.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
