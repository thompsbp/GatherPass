# ==============================================================================
# FILE: api/schemas/seasons.py
# ==============================================================================
# This file defines the Pydantic models for Season data validation.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict


class SeasonBase(BaseModel):
    """The base schema for a season, containing common fields."""

    name: str
    number: int
    start_date: datetime
    end_date: datetime


class SeasonCreate(SeasonBase):
    """Schema for data required when creating a new season."""

    pass


class SeasonUpdate(BaseModel):
    """
    Schema for data that can be updated on a season record.
    All fields are optional to allow for partial updates.
    """

    name: Optional[str] = None
    number: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


class Season(SeasonBase):
    """
    The default response model when returning season data.
    Includes the database ID.
    """

    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
