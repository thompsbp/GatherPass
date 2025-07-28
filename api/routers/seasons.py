# ==============================================================================
# FILE: api/routers/seasons.py
# ==============================================================================
# This file contains all API endpoints related to season management.

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
