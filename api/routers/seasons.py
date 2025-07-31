# ==============================================================================
# FILE: api/routers/seasons.py
# ==============================================================================
# This file contains all API endpoints related to season management.

import asyncio
from typing import List

import crud
import models
import schemas
from auth import require_admin_user, require_registered_user
from database import get_db
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter(
    prefix="/seasons",
    tags=["Seasons"],
)


@router.post("/", response_model=schemas.Season, status_code=status.HTTP_201_CREATED)
async def handle_create_season(
    season_data: schemas.SeasonCreate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Creates a new season."""
    return await crud.create_season(db=db, season_data=season_data, actor=admin_user)


@router.get("/", response_model=List[schemas.Season])
async def handle_get_seasons(
    offset: int = 0,
    limit: int = 100,
    name: str | None = None,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Retrieves a list of all seasons."""
    return await crud.get_seasons(db, offset=offset, limit=limit, name=name)


@router.get("/current", response_model=schemas.Season)
async def handle_get_current_season(
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves the currently active season."""
    current_season = await crud.get_current_season(db)
    if current_season is None:
        raise HTTPException(status_code=404, detail="No active season found.")
    return current_season


@router.get("/latest", response_model=schemas.Season)
async def handle_get_latest_season(
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves the season with the highest number."""
    latest_season = await crud.get_latest_season(db)
    if latest_season is None:
        raise HTTPException(status_code=404, detail="No seasons found.")
    return latest_season


@router.get("/{season_id}", response_model=schemas.Season)
async def handle_get_season(
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Retrieves a single season by its ID."""
    season = await crud.get_season_by_id(db, season_id=season_id)
    if season is None:
        raise HTTPException(status_code=404, detail="Season not found")
    return season


@router.get("/{season_id}/prizes", response_model=List[schemas.SeasonPrize])
async def handle_get_prizes_for_season(
    season_id: int,
    registered_user: models.User = Depends(require_registered_user),
    db: AsyncSession = Depends(get_db),
):
    """(Registered Users) Retrieves all prizes for a specific season."""
    return await crud.get_prizes_for_season(db, season_id=season_id)


@router.patch("/{season_id}", response_model=schemas.Season)
async def handle_update_season(
    season_id: int,
    update_data: schemas.SeasonUpdate,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Updates an existing season."""
    season_to_update = await crud.get_season_by_id(db, season_id=season_id)
    if season_to_update is None:
        raise HTTPException(status_code=404, detail="Season not found")

    return await crud.update_season(
        db, season=season_to_update, update_data=update_data, actor=admin_user
    )


@router.delete("/{season_id}", status_code=status.HTTP_204_NO_CONTENT)
async def handle_delete_season(
    season_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """(Admin) Deletes a season."""
    season_to_delete = await crud.get_season_by_id(db, season_id=season_id)
    if season_to_delete is None:
        raise HTTPException(status_code=404, detail="Season not found")

    await crud.delete_season(db, season=season_to_delete)
    return None


@router.get(
    "/{season_id}/promotion-candidates", response_model=List[schemas.PromotionCandidate]
)
async def handle_check_promotions(
    season_id: int,
    admin_user: models.User = Depends(require_admin_user),
    db: AsyncSession = Depends(get_db),
):
    """
    (Admin) Checks for users who are eligible for a rank promotion in a season.
    Returns a list of users whose point totals qualify them for a rank higher
    than the highest rank they have currently been awarded.
    """
    # Fetch all necessary data
    season_ranks_task = crud.get_ranks_for_season(db, season_id=season_id)
    leaderboard_task = crud.get_all_users_for_season(db, season_id=season_id)
    all_awards_task = crud.get_all_awarded_ranks_for_season(db, season_id=season_id)

    season_ranks, leaderboard, all_awards = await asyncio.gather(
        season_ranks_task, leaderboard_task, all_awards_task
    )

    # Create a map of {user_id: highest_awarded_rank_number}
    highest_awarded_ranks = {}
    for award in all_awards:
        user_id = award.user_id
        rank_number = award.season_rank.number
        if (
            user_id not in highest_awarded_ranks
            or rank_number > highest_awarded_ranks[user_id]
        ):
            highest_awarded_ranks[user_id] = rank_number

    # Find the promotion candidates
    promotion_candidates = []
    for season_user in leaderboard:
        user = season_user.user
        total_points = season_user.total_points

        # Determine the user's highest eligible rank based on their points
        eligible_rank = None
        for sr in reversed(season_ranks):  # Iterate from highest rank to lowest
            if total_points >= sr.required_points:
                eligible_rank = sr
                break  # Found the highest one they qualify for

        if not eligible_rank:
            continue  # This user doesn't have enough points for even the first rank

        # Get the user's highest awarded rank number (defaults to 0 if they have none)
        current_rank_number = highest_awarded_ranks.get(user.id, 0)

        # If their eligible rank is higher than their current rank, they are a candidate
        if eligible_rank.number > current_rank_number:
            # Find the full object for their current rank, if any
            current_rank_obj = None
            if current_rank_number > 0:
                # Find the SeasonRank object corresponding to their current rank number
                current_rank_obj = next(
                    (sr for sr in season_ranks if sr.number == current_rank_number),
                    None,
                )

            candidate = schemas.PromotionCandidate(
                user=user,
                total_points=total_points,
                current_rank=current_rank_obj.rank if current_rank_obj else None,
                eligible_rank=eligible_rank.rank,
            )
            promotion_candidates.append(candidate)

    return promotion_candidates
