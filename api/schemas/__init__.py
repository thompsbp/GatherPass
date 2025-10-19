# ==============================================================================
# FILE: api/schemas/__init__.py
# ==============================================================================
# This file makes the `schemas` directory a Python package and exposes
# all Pydantic models from a single, convenient namespace.

from .auth import Actor, Token, TokenData, TokenRequest
from .items import Item, ItemCreate, ItemUpdate
from .prizes import Prize, PrizeCreate, PrizeUpdate
from .promotions import PromotionCandidate, PromotionResult
from .ranks import Rank, RankCreate, RankUpdate
from .season_items import SeasonItem, SeasonItemCreate, SeasonItemUpdate
from .season_prizes import SeasonPrize, SeasonPrizeCreate
from .season_ranks import SeasonRank, SeasonRankCreate, SeasonRankUpdate
from .season_user_ranks import (
    SeasonRankPromotionCreate,
    SeasonUserRank,
    SeasonUserRankCreate,
)
from .season_users import SeasonUser, SeasonUserCreate
from .seasons import Season, SeasonCreate, SeasonUpdate
from .submissions import Submission, SubmissionCreate, SubmissionUpdate
from .summaries import UserItemSummary, UserSeasonSummary
from .user_prize_awards import (
    UserPrizeAward,
    UserPrizeAwardCreate,
    UserPrizeAwardUpdate,
)
from .users import User, UserCreate, UserIdentifier, UserUpdate
