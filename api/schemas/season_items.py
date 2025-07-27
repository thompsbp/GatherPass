# ==============================================================================
# FILE: api/schemas/season_items.py
# ==============================================================================
# This file defines the Pydantic models for the SeasonItem association.

from typing import Optional

from pydantic import BaseModel, ConfigDict

from .items import Item
from .seasons import Season


class SeasonItemBase(BaseModel):
    """The base schema for a season-item link, containing common fields."""

    point_value: int


class SeasonItemCreate(SeasonItemBase):
    """Schema for data required when associating an item with a season."""

    item_id: int


class SeasonItemUpdate(BaseModel):
    """
    Schema for data that can be updated on a season-item link.
    Only the point value can be changed.
    """

    point_value: Optional[int] = None


class SeasonItem(SeasonItemBase):
    """
    The default response model when returning season-item data.
    This is a nested schema that includes the full Item and Season objects
    for a rich and user-friendly API response.
    """

    id: int
    item: Item
    season: Season
    model_config = ConfigDict(from_attributes=True)
