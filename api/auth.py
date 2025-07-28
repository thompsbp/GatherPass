# ==============================================================================
# FILE: api/auth.py
# ==============================================================================
# This file contains all authentication and authorization logic.

import uuid
from datetime import datetime, timedelta, timezone
from typing import Literal, Optional, Tuple

import crud
import models
from database import get_db
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import APIKeyHeader, OAuth2PasswordBearer
from jose import JWTError, jwt
from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession


# Pydantic settings model to load secrets from .env.api
class Settings(BaseSettings):
    bot_api_key: str
    jwt_secret_key: str
    algorithm: str
    access_token_expire_minutes: int
    root_admin_id: int

    class Config:
        env_file = ".env.api"


settings = Settings()  # type: ignore

# Define security schemes
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


async def _authenticate_request(
    token: Optional[str] = Depends(oauth2_scheme),
    api_key: Optional[str] = Depends(api_key_header),
    user_discord_id: Optional[int] = Header(None, alias="X-User-Discord-ID"),
) -> Optional[Tuple[Literal["uuid", "discord_id"], str | int]]:
    """
    Internal-only authentication function. It validates credentials and
    returns the type and value of the user's identifier.
    """
    # Case 1: Direct access with a user's JWT (This takes precedence)
    if token:
        try:
            payload = jwt.decode(
                token, settings.jwt_secret_key, algorithms=[settings.algorithm]
            )
            user_uuid: Optional[str] = payload.get("sub")
            if user_uuid:
                return ("uuid", user_uuid)
        except JWTError:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Case 2: Bot access on behalf of a user
    elif api_key and api_key == settings.bot_api_key:
        if user_discord_id:
            return ("discord_id", user_discord_id)

    return None


async def require_registered_user(
    auth_details: Optional[Tuple] = Depends(_authenticate_request),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    """
    Dependency for endpoints that require any valid, registered user
    with an active status.
    """
    if auth_details is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    id_type, id_value = auth_details
    user: Optional[models.User] = None

    if id_type == "uuid":
        user = await crud.get_user_by_uuid(db, user_uuid=str(id_value))
    elif id_type == "discord_id":
        user = await crud.get_user_by_discord_id(db, discord_id=int(id_value))

    if user is None:
        raise HTTPException(status_code=403, detail="User not found or access denied")

    if getattr(user, "status") == "pending":
        raise HTTPException(
            status_code=403, detail="User account is pending verification."
        )
    if getattr(user, "status") == "banned":
        raise HTTPException(status_code=403, detail="Access Denied.")

    return user


async def require_admin_user(
    auth_details: Optional[Tuple] = Depends(_authenticate_request),
    db: AsyncSession = Depends(get_db),
) -> models.User:
    """
    Dependency for endpoints that require an admin user with an active status.
    Includes a special bootstrap case for the ROOT_ADMIN_ID.
    """
    if auth_details is None:
        raise HTTPException(status_code=401, detail="Authentication required")

    id_type, id_value = auth_details
    user: Optional[models.User] = None

    # Bootstrap Case: If the request is for the root admin, we handle it specially.
    if id_type == "discord_id" and int(id_value) == settings.root_admin_id:
        user = await crud.get_user_by_discord_id(db, discord_id=int(id_value))
        if user is None:
            return models.User(
                id=-1,
                uuid=str(uuid.uuid4()),
                discord_id=settings.root_admin_id,
                admin=True,
            )
        return user

    # Normal Case: Look up the user based on their authenticated identifier.
    if user is None:
        if id_type == "uuid":
            user = await crud.get_user_by_uuid(db, user_uuid=str(id_value))
        elif id_type == "discord_id":
            user = await crud.get_user_by_discord_id(db, discord_id=int(id_value))

    # Authorization Checks
    if user is None:
        raise HTTPException(status_code=403, detail="User not found or access denied")

    if getattr(user, "status") == "pending":
        raise HTTPException(
            status_code=403, detail="User account is pending verification."
        )
    if getattr(user, "status") == "banned":
        raise HTTPException(status_code=403, detail="Access Denied.")

    if user.admin is not True:
        raise HTTPException(status_code=403, detail="Admin privileges required")

    return user


async def require_bot_auth(
    api_key: Optional[str] = Depends(api_key_header),
) -> bool:
    """
    A simple dependency that requires the request to have the bot's secret
    API key. Returns True if authenticated, otherwise raises an error.
    """
    if api_key and api_key == settings.bot_api_key:
        return True

    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="This action can only be performed by the bot.",
    )
