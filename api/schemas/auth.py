# ==============================================================================
# FILE: api/schemas/auth.py
# ==============================================================================
# This file defines the Pydantic models for Authentication data validation.

from typing import Optional

from pydantic import BaseModel


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

    user_uuid: Optional[str] = None


class TokenRequest(BaseModel):
    """Schema for requesting a token for a specific user."""

    discord_id: int
