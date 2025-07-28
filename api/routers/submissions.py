# ==============================================================================
# FILE: api/routers/submissions.py
# ==============================================================================
# This file contains the API endpoints for creating and viewing submissions.

from typing import List

import crud
import models
import schemas
from auth import require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

# Router for the primary action of creating a submission
router = APIRouter(
    prefix="/submissions",
    tags=["Submissions"],
)

# A second router for the nested GET endpoint to view a user's history
user_season_submissions_router = APIRouter(
    prefix="/users/{user_id}/seasons/{season_id}/submissions",
    tags=["Submissions"],
)


@router.post("/", response_model=schemas.Submission)
async def handle_create_submission(
    submission_data: schemas.SubmissionCreate,
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Creates a new submission for a user.
    - A regular user can only submit for themself.
    - An admin can submit on behalf of any user.
    """
    # Authorization: Ensure the user is either an admin or is submitting for themself.
    if not (
        current_user.admin is True or int(current_user.id) == submission_data.user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="Not authorized to create a submission for another user.",
        )

    new_submission = await crud.create_submission(
        db, submission_data=submission_data, actor=current_user
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
