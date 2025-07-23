# ==============================================================================
# FILE: api/routers/token.py
# ==============================================================================
# This file contains the API endpoint for generating JWTs for users.

import models
import schemas
from auth import create_access_token, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/token",
    tags=["Token"],
)


@router.post("/", response_model=schemas.Token)
async def handle_generate_token(
    current_user: models.User = Depends(require_registered_user),
):
    """
    Generates a JWT for the authenticated user.

    This endpoint can be called in two ways:
    1. By the bot on behalf of a user (using API Key + X-User-Discord-ID header).
    2. By a user who already has a valid (but perhaps expiring) JWT.

    The `require_registered_user` dependency handles both cases and ensures
    the user is active and verified before a token is issued.
    """
    # The dependency has already validated the user. We just need to create the token.
    access_token = create_access_token(data={"sub": current_user.uuid})
    return {"access_token": access_token, "token_type": "bearer"}
