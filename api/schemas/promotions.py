# ==============================================================================
# FILE: api/schemas/promotions.py
# ==============================================================================
# This file defines the Pydantic models for the promotion check feature.

from typing import Optional

from pydantic import BaseModel

from .ranks import Rank
from .season_user_ranks import SeasonUserRank
from .user_prize_awards import UserPrizeAward
from .users import User


class PromotionCandidate(BaseModel):
    """
    Represents a user who is eligible for a rank promotion.
    """

    user: User
    total_points: int
    current_rank: Optional[Rank] = None
    eligible_rank: Rank


class PromotionResult(BaseModel):
    """
    Represents the result of a promotion action, including all newly
    awarded ranks and prizes.
    """

    awarded_ranks: list[SeasonUserRank] = []
    awarded_prizes: list[UserPrizeAward] = []
