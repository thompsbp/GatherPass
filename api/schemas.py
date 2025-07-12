# ==============================================================================
# FILE: api/schemas.py
# ==============================================================================
# This file defines the Pydantic models for data validation and serialization.
# We'll add the models needed for our authentication system.

from typing import Optional

from pydantic import BaseModel

# --- Authentication Schemas ---


class Actor(BaseModel):
    """Represents the authenticated entity making the request (bot or user)."""

    id: str
    is_bot: bool


class Token(BaseModel):
    """The structure of a JWT response."""

    access_token: str
    token_type: str


class TokenData(BaseModel):
    """The data contained within the JWT payload."""

    user_id: Optional[str] = None
