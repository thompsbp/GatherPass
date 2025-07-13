# ==============================================================================
# api/schemas
# ==============================================================================
# This file defines the Pydantic models which act as the data contracts
# for the API. They ensure that data coming in and going out matches a
# specific structure.


from typing import Optional

from pydantic import BaseModel, ConfigDict


class Actor(BaseModel):
    """Represents the authenticated entity making a request (the bot or a user)."""

    id: str
    is_bot: bool


class Token(BaseModel):
    """Defines the structure for a JWT response sent to a user."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """Defines the data structure contained within a JWT payload."""

    user_id: Optional[str] = None


class UserCreate(BaseModel):
    """
    Schema for data required when registering a new user.
    Used by the bot when calling the POST /users/ endpoint.
    """

    discord_id: int
    in_game_name: str
    lodestone_id: str


class UserUpdate(BaseModel):
    """
    Schema for data that can be updated on a user record.
    Fields are optional so an admin can update just one thing at a time.
    """

    status: Optional[str] = None
    admin: Optional[bool] = None


class User(BaseModel):
    """
    The default response model when returning user data.
    This ensures sensitive data (like audit fields) isn't exposed by default.
    """

    id: int
    discord_id: int
    in_game_name: Optional[str]
    status: str
    admin: bool

    model_config = ConfigDict(from_attributes=True)
