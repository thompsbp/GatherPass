# ==============================================================================
# FILE: api/schemas/promotions.py
# ==============================================================================
# This file defines the Pydantic models for the promotion check feature.

from typing import Optional

from pydantic import BaseModel

from .ranks import Rank
from .users import User


class PromotionCandidate(BaseModel):
    """
    Represents a user who is eligible for a rank promotion.
    """

    user: User
    total_points: int
    current_rank: Optional[Rank] = None
    eligible_rank: Rank
