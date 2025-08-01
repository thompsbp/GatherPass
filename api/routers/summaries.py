# ==============================================================================
# FILE: api/routers/summaries.py
# ==============================================================================
# This file contains endpoints for generating summary data.

import crud
import models
import schemas
from auth import require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    tags=["Summaries"],
)


@router.get("/me/seasons/{season_id}/summary", response_model=schemas.UserSeasonSummary)
async def handle_get_my_season_summary(
    season_id: int,
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves the current user's progress summary for a season."""
    # The user is identified by the token/headers via the dependency.
    # We use their ID directly to fetch the summary.
    summary = await crud.get_user_season_summary(
        db, user_id=int(current_user.id), season_id=season_id
    )

    if summary is None:
        raise HTTPException(
            status_code=404, detail="You are not registered for this season."
        )

    return summary
