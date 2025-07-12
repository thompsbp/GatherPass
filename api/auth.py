# ==============================================================================
# FILE: api/auth.py
# ==============================================================================
# This file contains all authentication and authorization logic.

from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic_settings import BaseSettings
from schemas import Actor, TokenData


class Settings(BaseSettings):
    """Loads settings from the .env.api file."""

    bot_api_key: str
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env.api"


settings = Settings()

# Define the two security schemes we'll accept.
# auto_error=False is crucial. It tells FastAPI not to raise an error
# if a scheme is missing, allowing our dependency to check for the other one.
api_key_header = APIKeyHeader(name="X-API-Key", auto_error=False)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token", auto_error=False)


def create_access_token(data: dict):
    """Creates a new JWT."""
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.access_token_expire_minutes
    )
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.algorithm
    )
    return encoded_jwt


async def get_current_actor(
    api_key: Optional[str] = Depends(api_key_header),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Actor:
    """
    A single dependency to handle both API Key and JWT authentication.
    This function will be the guard on all protected endpoints.
    """
    # First, try to validate using the API Key (for the bot)
    if api_key and api_key == settings.bot_api_key:
        return Actor(id="bot", is_bot=True)

    # If no valid API Key, try to validate using the JWT (for users)
    if token:
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.algorithm]
            )
            user_id: str = payload.get("sub")
            if user_id is None:
                # The token is valid but doesn't contain the user ID.
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload",
                )
            return Actor(id=f"user:{user_id}", is_bot=False)
        except JWTError:
            # The token is malformed or expired.
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate token",
            )

    # If neither an API Key nor a JWT was provided or was valid, deny access.
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not authenticated",
        headers={"WWW-Authenticate": "Bearer"},
    )
