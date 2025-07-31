# ==============================================================================
# FILE: api/routers/submissions.py
# ==============================================================================
# This file contains the API endpoints for creating and viewing submissions.

from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

user_season_submissions_router = APIRouter(
    prefix="/users/{user_id}/seasons/{season_id}/submissions",
    tags=["Submissions"],
)


@router.post("/", response_model=schemas.Submission)
async def handle_create_submission(
    submission_data: schemas.SubmissionCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    (Admin-Only) Creates a new submission for a user.
    """
    new_submission = await crud.create_submission(
        db, submission_data=submission_data, actor=admin_user
    )

    if new_submission is None:
        raise HTTPException(
            status_code=400,
            detail="Submission failed. The item may not exist, or the user may not be registered for this season.",
        )
    return new_submission


@user_season_submissions_router.get("/", response_model=List[schemas.Submission])
async def handle_get_submissions_for_user_in_season(
    user_id: int,
    season_id: int,
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all submissions for a user in a season."""
    return await crud.get_submissions_for_user_in_season(
        db, user_id=user_id, season_id=season_id
    )
