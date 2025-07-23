# ==============================================================================
# FILE: api/tests/test_ranks_crud.py
# ==============================================================================
# This file contains unit tests for the rank-related functions in crud/ranks.py.

import crud
import pytest
from schemas import RankCreate, RankUpdate


@pytest.mark.asyncio
async def test_create_rank(async_db_session):
    """Tests that a rank can be created successfully."""
    rank_data = RankCreate(name="Bronze", badge_url="http://example.com/bronze.png")

    new_rank = await crud.create_rank(db=async_db_session, rank_data=rank_data)

    assert new_rank is not None
    assert new_rank.id is not None
    assert new_rank.name == "Bronze"
    assert new_rank.badge_url == "http://example.com/bronze.png"


@pytest.mark.asyncio
async def test_get_rank_by_id(async_db_session):
    """Tests retrieving a rank by its ID."""
    rank_data = RankCreate(name="Silver", badge_url="http://example.com/silver.png")
    created_rank = await crud.create_rank(db=async_db_session, rank_data=rank_data)

    found_rank = await crud.get_rank_by_id(db=async_db_session, rank_id=created_rank.id)

    assert found_rank is not None
    assert found_rank.id == created_rank.id
    assert found_rank.name == "Silver"


@pytest.mark.asyncio
async def test_get_ranks(async_db_session):
    """Tests retrieving a list of all ranks."""
    await crud.create_rank(db=async_db_session, rank_data=RankCreate(name="Gold"))
    await crud.create_rank(db=async_db_session, rank_data=RankCreate(name="Platinum"))

    all_ranks = await crud.get_ranks(db=async_db_session)
    assert len(all_ranks) == 2


@pytest.mark.asyncio
async def test_update_rank(async_db_session):
    """Tests updating an existing rank's details."""
    rank_data = RankCreate(name="Old Rank Name", badge_url="http://example.com/old.png")
    rank_to_update = await crud.create_rank(db=async_db_session, rank_data=rank_data)

    update_data = RankUpdate(name="New Rank Name")
    updated_rank = await crud.update_rank(
        db=async_db_session,
        rank=rank_to_update,
        update_data=update_data,
    )

    assert updated_rank.name == "New Rank Name"
    assert (
        updated_rank.badge_url == "http://example.com/old.png"
    )  # Should not have changed


@pytest.mark.asyncio
async def test_delete_rank(async_db_session):
    """Tests that a rank can be deleted successfully."""
    rank_data = RankCreate(name="To Be Deleted")
    rank_to_delete = await crud.create_rank(db=async_db_session, rank_data=rank_data)
    rank_id = rank_to_delete.id

    await crud.delete_rank(db=async_db_session, rank=rank_to_delete)

    # Verify it's gone
    deleted_rank = await crud.get_rank_by_id(db=async_db_session, rank_id=rank_id)
    assert deleted_rank is None
