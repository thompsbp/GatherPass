# ==============================================================================
# FILE: api/main.py
# ==============================================================================
# The main entry point for the api.

from contextlib import asynccontextmanager

import auth
import crud
import database
import models
import schemas
from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up API...")
    await database.create_db_and_tables()

    yield
    print("Shutting down API")


app = FastAPI(lifespan=lifespan)


# --- Endpoints ---
@app.get("/health", status_code=200)
def health_check():
    """A simple public endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is healthy and public"}


@app.get("/secure-health", response_model=schemas.Actor)
async def secure_health_check(actor: schemas.Actor = Depends(auth.get_current_actor)):
    """A secure endpoint to test authentication."""
    return actor


@app.post("/users/", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def handle_create_user(
    user_data: schemas.UserCreate,
    actor: schemas.Actor = Depends(auth.get_current_actor),
    db: AsyncSession = Depends(database.get_db),
):
    """Endpoint for the bot to register a new user."""
    if not actor.is_bot:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Unauthorized",
        )

    db_user = await crud.get_user_by_discord_id(db, discord_id=user_data.discord_id)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this Discord ID already exists.",
        )

    return await crud.create_user(db=db, user_data=user_data, actor=actor)
