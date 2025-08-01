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
from fastapi import APIRouter, Depends, HTTPException, Query, status
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


@router.get("/", response_model=List[schemas.Submission])
async def handle_get_submissions(
    season_id: int = Query(...),
    user_id: int | None = Query(None),
    current_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieves submissions for a season.
    - Admins can view any user's submissions.
    - Regular users can only view their own.
    """
    if user_id is not None:
        if user_id != int(current_user.id) and not (current_user.admin is True):
            raise HTTPException(
                status_code=403,
                detail="Not authorized to view another user's submissions.",
            )
    else:
        if current_user.admin is False:
            user_id = int(current_user.id)

    return await crud.get_submissions(db, season_id=season_id, user_id=user_id)


@router.patch("/{submission_id}", response_model=schemas.Submission)
async def handle_update_submission(
    submission_id: int,
    update_data: schemas.SubmissionUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin-Only) Updates a submission's quantity and corrects the user's points."""
    submission_to_update = await crud.get_submission_by_id(
        db, submission_id=submission_id
    )
    if submission_to_update is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    # The CRUD function handles all the logic of updating points.
    return await crud.update_submission(
        db, submission=submission_to_update, update_data=update_data, actor=admin_user
    )


@router.delete("/{submission_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_delete_submission(
    submission_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin-Only) Deletes a submission and subtracts its points from the user's total."""
    submission_to_delete = await crud.get_submission_by_id(
        db, submission_id=submission_id
    )
    if submission_to_delete is None:
        raise HTTPException(status_code=404, detail="Submission not found")

    await crud.delete_submission(db, submission=submission_to_delete)
    return None
