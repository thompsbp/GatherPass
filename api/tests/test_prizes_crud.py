# ==============================================================================
# FILE: api/tests/test_prizes_crud.py
# ==============================================================================
# This file contains unit tests for the prize-related functions in crud/prizes.py.

import crud
import pytest
from schemas import PrizeCreate, PrizeUpdate


@pytest.mark.asyncio
async def test_create_prize(async_db_session):
    """Tests that a prize can be created successfully."""
    prize_data = PrizeCreate(
        description="1 Million Gil",
        value=1000000,
        discord_role=123456789012345678,
    )

    new_prize = await crud.create_prize(db=async_db_session, prize_data=prize_data)

    assert new_prize is not None
    assert new_prize.id is not None
    assert new_prize.description == "1 Million Gil"
    assert new_prize.value == 1000000


@pytest.mark.asyncio
async def test_get_prize_by_id(async_db_session):
    """Tests retrieving a prize by its ID."""
    prize_data = PrizeCreate(description="A Cool Mount")
    created_prize = await crud.create_prize(db=async_db_session, prize_data=prize_data)

    found_prize = await crud.get_prize_by_id(
        db=async_db_session, prize_id=created_prize.id
    )

    assert found_prize is not None
    assert found_prize.id == created_prize.id
    assert found_prize.description == "A Cool Mount"


@pytest.mark.asyncio
async def test_get_prizes(async_db_session):
    """Tests retrieving a list of all prizes."""
    await crud.create_prize(
        db=async_db_session, prize_data=PrizeCreate(description="Prize A")
    )
    await crud.create_prize(
        db=async_db_session, prize_data=PrizeCreate(description="Prize B")
    )

    all_prizes = await crud.get_prizes(db=async_db_session)
    assert len(all_prizes) == 2


@pytest.mark.asyncio
async def test_update_prize(async_db_session):
    """Tests updating an existing prize's details."""
    prize_data = PrizeCreate(description="Old Description", value=100)
    prize_to_update = await crud.create_prize(
        db=async_db_session, prize_data=prize_data
    )

    update_data = PrizeUpdate(description="New Grand Prize Description")
    updated_prize = await crud.update_prize(
        db=async_db_session,
        prize=prize_to_update,
        update_data=update_data,
    )

    assert updated_prize.description == "New Grand Prize Description"
    assert updated_prize.value == 100  # Should not have changed


@pytest.mark.asyncio
async def test_delete_prize(async_db_session):
    """Tests that a prize can be deleted successfully."""
    prize_data = PrizeCreate(description="To Be Deleted")
    prize_to_delete = await crud.create_prize(
        db=async_db_session, prize_data=prize_data
    )
    prize_id = prize_to_delete.id

    await crud.delete_prize(db=async_db_session, prize=prize_to_delete)

    # Verify it's gone
    deleted_prize = await crud.get_prize_by_id(db=async_db_session, prize_id=prize_id)
    assert deleted_prize is None
