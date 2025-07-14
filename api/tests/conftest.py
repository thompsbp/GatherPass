# ==============================================================================
# FILE: api/tests/conftest.py
# ==============================================================================
# This file contains shared fixtures for pytest. It sets up a temporary,
# in-memory async SQLite database for each test session.

import asyncio
import os
import sys
from pathlib import Path
from typing import AsyncGenerator

# --- IMPORTANT: Set test environment variables BEFORE other imports ---
# This ensures that modules like `auth` will see these values when they are first imported.
os.environ["BOT_API_KEY"] = "test_bot_api_key"
os.environ["JWT_SECRET_KEY"] = "test_jwt_secret"
os.environ["ALGORITHM"] = "HS256"
os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"] = "30"


# Add the project root to the Python path to resolve imports
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))


import pytest
import pytest_asyncio
from database import Base, get_db
from httpx import ASGITransport, AsyncClient
from main import app
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

# Use an async in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

engine = create_async_engine(SQLALCHEMY_DATABASE_URL)

AsyncTestingSessionLocal = async_sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)


# Override the main get_db dependency to use the test database
async def override_get_db() -> AsyncGenerator:
    async with AsyncTestingSessionLocal() as session:
        yield session


app.dependency_overrides[get_db] = override_get_db


# --- Fixtures ---


@pytest_asyncio.fixture(scope="function")
async def async_db_session():
    """
    Pytest fixture to create and clean up the database for each test function.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    db = AsyncTestingSessionLocal()
    try:
        yield db
    finally:
        await db.close()
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest_asyncio.fixture(scope="function")
async def test_client() -> AsyncGenerator[AsyncClient, None]:
    """
    Pytest fixture that creates an AsyncClient for making API requests.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
