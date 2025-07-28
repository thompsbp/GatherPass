# ==============================================================================
# FILE: api/schemas/submissions.py
# ==============================================================================
# This file defines the Pydantic models for the Submission record.

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict

# Import base schemas for nesting
from .season_items import SeasonItem
from .users import User


class SubmissionBase(BaseModel):
    """The base schema for a submission."""

    quantity: int = 1


class SubmissionCreate(SubmissionBase):
    """Schema for data required when creating a new submission."""

    user_id: int
    season_item_id: int


class Submission(SubmissionBase):
    """The default response model when returning submission data."""

    id: int
    total_point_value: int
    created_at: datetime
    user: User
    season_item: SeasonItem

    model_config = ConfigDict(from_attributes=True)
