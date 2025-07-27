# ==============================================================================
# FILE: api/models.py
# ==============================================================================
# This file defines the complete database schema as SQLAlchemy ORM models.

import uuid

from database import Base
from sqlalchemy import (
    INT,
    TIMESTAMP,
    BigInteger,
    Boolean,
    Column,
    Enum,
    ForeignKey,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import relationship

# --- Main Tables ---


class User(Base):
    __tablename__ = "user"
    id = Column(INT, primary_key=True, autoincrement=True)
    uuid = Column(
        String(36), unique=True, nullable=False, default=lambda: str(uuid.uuid4())
    )
    discord_id = Column(BigInteger, unique=True, nullable=False)
    in_game_name = Column(String(255))
    lodestone_id = Column(String(255))
    status = Column(
        Enum("pending", "verified", "banned"), nullable=False, default="pending"
    )
    admin = Column(Boolean, nullable=False, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
    change_requested_by = Column(BigInteger)


class Season(Base):
    __tablename__ = "season"
    id = Column(INT, primary_key=True, autoincrement=True)
    number = Column(INT, unique=True, nullable=False)
    name = Column(String(255), unique=True, nullable=False)
    start_date = Column(TIMESTAMP, nullable=False)
    end_date = Column(TIMESTAMP, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Item(Base):
    __tablename__ = "item"
    id = Column(INT, primary_key=True, autoincrement=True)
    lodestone_id = Column(String(255), unique=True)
    name = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Rank(Base):
    __tablename__ = "rank"
    id = Column(INT, primary_key=True, autoincrement=True)
    name = Column(String(255))
    badge_url = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Prize(Base):
    __tablename__ = "prize"
    id = Column(INT, primary_key=True, autoincrement=True)
    description = Column(String(255))
    value = Column(INT)
    lodestone_id = Column(INT)
    discord_role = Column(BigInteger)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())


class Submission(Base):
    __tablename__ = "submission"
    id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey("user.id"), nullable=False)
    season_item_id = Column(INT, ForeignKey("season_item.id"), nullable=False)
    quantity = Column(INT, nullable=False, default=1)
    total_point_value = Column(INT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
    change_requested_by = Column(BigInteger)


# --- Join & Tracking Tables ---


class SeasonUser(Base):
    __tablename__ = "season_user"
    id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey("user.id"), nullable=False)
    season_id = Column(INT, ForeignKey("season.id"), nullable=False)
    total_points = Column(INT, nullable=False, default=0)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    created_by = Column(String(255), nullable=False)
    updated_by = Column(String(255), nullable=False)
    change_requested_by = Column(BigInteger)
    __table_args__ = (UniqueConstraint("user_id", "season_id", name="_user_season_uc"),)

    user = relationship("User")
    season = relationship("Season")


class SeasonItem(Base):
    __tablename__ = "season_item"
    id = Column(INT, primary_key=True, autoincrement=True)
    season_id = Column(INT, ForeignKey("season.id"), nullable=False)
    item_id = Column(INT, ForeignKey("item.id"), nullable=False)
    point_value = Column(INT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint("season_id", "item_id", name="_season_item_uc"),)

    item = relationship("Item")
    season = relationship("Season")


class SeasonRank(Base):
    __tablename__ = "season_rank"
    id = Column(INT, primary_key=True, autoincrement=True)
    season_id = Column(INT, ForeignKey("season.id"), nullable=False)
    rank_id = Column(INT, ForeignKey("rank.id"), nullable=False)
    number = Column(INT)
    required_points = Column(INT)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
    __table_args__ = (UniqueConstraint("season_id", "rank_id", name="_season_rank_uc"),)

    rank = relationship("Rank")
    season = relationship("Season")


class SeasonPrize(Base):
    __tablename__ = "season_prize"
    id = Column(INT, primary_key=True, autoincrement=True)
    prize_id = Column(INT, ForeignKey("prize.id"), nullable=False)
    season_rank_id = Column(INT, ForeignKey("season_rank.id"), nullable=False)

    prize = relationship("Prize")
    season_rank = relationship("SeasonRank")


class SeasonUserRank(Base):
    __tablename__ = "season_user_rank"
    id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey("user.id"), nullable=False)
    season_rank_id = Column(INT, ForeignKey("season_rank.id"), nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    __table_args__ = (
        UniqueConstraint("user_id", "season_rank_id", name="_user_season_rank_uc"),
    )

    user = relationship("User")
    season_rank = relationship("SeasonRank")


class UserPrizeAward(Base):
    __tablename__ = "user_prize_award"
    id = Column(INT, primary_key=True, autoincrement=True)
    user_id = Column(INT, ForeignKey("user.id"), nullable=False)
    season_prize_id = Column(INT, ForeignKey("season_prize.id"), nullable=False)
    delivered = Column(Boolean, nullable=False, default=False)
    awarded_at = Column(TIMESTAMP, server_default=func.now())
    delivered_at = Column(TIMESTAMP, nullable=True)
    delivered_by = Column(BigInteger, nullable=True)
    notes = Column(Text, nullable=True)

    user = relationship("User")
    season_prize = relationship("SeasonPrize")
