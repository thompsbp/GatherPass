# ==============================================================================
# FILE: api/main.py
# ==============================================================================
# We update the main file to apply our new security dependency.

from auth import get_current_actor
from fastapi import Depends, FastAPI
from schemas import Actor

app = FastAPI()


@app.get("/health", status_code=200)
def health_check():
    """
    A simple public endpoint to confirm the API is running.
    This endpoint does NOT require authentication.
    """
    return {"status": "ok", "message": "API is healthy and public"}


@app.get("/secure-health", response_model=Actor)
async def secure_health_check(actor: Actor = Depends(get_current_actor)):
    """
    A new, SECURE endpoint to test our authentication.
    This endpoint is protected by the get_current_actor dependency.
    """
    return actor
