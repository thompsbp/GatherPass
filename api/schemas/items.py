# ==============================================================================
# FILE: api/schemas/items.py
# ==============================================================================
# This file defines the Pydantic models for Item data validation.

from typing import Optional

from pydantic import BaseModel, ConfigDict


class ItemBase(BaseModel):
    """The base schema for an item, containing common fields."""

    name: str
    lodestone_id: str


class ItemCreate(ItemBase):
    """Schema for data required when creating a new item."""

    pass


class ItemUpdate(BaseModel):
    """
    Schema for data that can be updated on an item record.
    All fields are optional to allow for partial updates.
    """

    name: Optional[str] = None
    lodestone_id: Optional[str] = None


class Item(ItemBase):
    """
    The default response model when returning item data.
    Includes the database ID.
    """

    id: int

    model_config = ConfigDict(from_attributes=True)
