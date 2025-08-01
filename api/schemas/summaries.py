# ==============================================================================
# FILE: api/schemas/summaries.py
# ==============================================================================
# This file defines the Pydantic models for summary-style API responses.

from typing import List, Optional

from pydantic import BaseModel

from .prizes import Prize
from .ranks import Rank


class UserSeasonSummary(BaseModel):
    """
    A complete summary of a user's progress and rewards for a specific season.
    """

    user_id: int
    season_id: int
    total_points: int
    current_rank: Optional[Rank] = None
    awarded_prizes: List[Prize] = []
