# ==============================================================================
# FILE: api/main.py
# ==============================================================================
# This is the main entry point for the FastAPI application.
# It initializes the app, includes the routers, and defines global endpoints.

import sys
from contextlib import asynccontextmanager

import database
from fastapi import FastAPI
from routers import users  # pyright: ignore [reportMissingImports]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Handles application startup and shutdown events."""
    print("Starting up API...")
    await database.create_db_and_tables()
    yield
    print("Shutting down API")


# Initialize the FastAPI app
app = FastAPI(lifespan=lifespan)

# --- Include Routers ---
app.include_router(users.router)


# --- Global Endpoints ---
@app.get("/health", status_code=200, tags=["Health"])
def health_check():
    """A simple public endpoint to confirm the API is running."""
    return {"status": "ok", "message": "API is healthy"}
