# ==============================================================================
# FILE: api/auth.py
# ==============================================================================
# This file contains all authentication and authorization logic.

import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import crud
from database import get_db
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic_settings import BaseSettings
from schemas import Actor, TokenData
from sqlalchemy.ext.asyncio import AsyncSession


class Settings(BaseSettings):
    """Loads settings from the .env.api file."""

    bot_api_key: str
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int

    class Config:
        env_file = ".env.api"


settings = Settings()

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
    request: Request,
    db: AsyncSession = Depends(get_db),
    api_key: Optional[str] = Depends(api_key_header),
    token: Optional[str] = Depends(oauth2_scheme),
) -> Actor:
    """
    A single dependency to handle both API Key and JWT authentication.
    This function will be the guard on all protected endpoints.
    """
    if api_key:
        if api_key == settings.bot_api_key:
            return Actor(id="bot", is_bot=True)
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Denied",
            )

    if token:
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.algorithm]
            )
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Access Denied",
                )
            return Actor(id=f"user:{user_id}", is_bot=False)
        except JWTError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Access Denied",
            )

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Access Denied",
        headers={"WWW-Authenticate": "Bearer"},
    )
