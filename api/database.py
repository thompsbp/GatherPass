# ==============================================================================
# FILE: api/database.py
# ==============================================================================
# This file contains all the SQL Alchemy functions that interact directly with the database.

from typing import AsyncGenerator

from pydantic_settings import BaseSettings
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base


class Settings(BaseSettings):
    """Loads the DATABASE_URL from the .env.api file."""

    database_url: str

    class Config:
        env_file = ".env.api"


settings = Settings()

engine = create_async_engine(settings.database_url, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, expire_on_commit=False)

Base = declarative_base()


async def create_db_and_tables():
    """
    Connects to the database and creates all tables defined in models.py
    if they don't already exist. This is called once on application startup.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    A FastAPI dependency that provides a database session for a single request.
    This version explicitly handles rollbacks on exceptions
    """
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
