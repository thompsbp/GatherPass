# ==============================================================================
# FILE: api/tests/test_items_crud.py
# ==============================================================================
# This file contains unit tests for the item-related functions in crud/items.py.

import crud
import pytest
from schemas import Actor, ItemCreate, ItemUpdate

# A mock actor for audit purposes
mock_actor = Actor(id="test_runner", is_bot=True)


@pytest.mark.asyncio
async def test_create_item(async_db_session):
    """Tests that an item can be created successfully."""
    item_data = ItemCreate(name="Iron Ore", lodestone_id="5051")

    new_item = await crud.create_item(db=async_db_session, item_data=item_data)

    assert new_item is not None
    assert new_item.id is not None
    assert new_item.name == "Iron Ore"
    assert new_item.lodestone_id == "5051"


@pytest.mark.asyncio
async def test_create_item_fail_duplicate(async_db_session):
    """Tests that creating an item with a duplicate lodestone_id returns None."""
    # Create the first item
    item_data1 = ItemCreate(name="Copper Ore", lodestone_id="5050")
    await crud.create_item(db=async_db_session, item_data=item_data1)

    # Attempt to create a second item with the same lodestone_id
    item_data2 = ItemCreate(name="Another Ore", lodestone_id="5050")
    duplicate_item = await crud.create_item(db=async_db_session, item_data=item_data2)

    assert duplicate_item is None


@pytest.mark.asyncio
async def test_get_item_by_id(async_db_session):
    """Tests retrieving an item by its ID."""
    item_data = ItemCreate(name="Silver Ore", lodestone_id="5052")
    created_item = await crud.create_item(db=async_db_session, item_data=item_data)

    found_item = await crud.get_item_by_id(db=async_db_session, item_id=created_item.id)

    assert found_item is not None
    assert found_item.id == created_item.id
    assert found_item.name == "Silver Ore"


@pytest.mark.asyncio
async def test_get_items(async_db_session):
    """Tests retrieving a list of all items."""
    await crud.create_item(
        db=async_db_session, item_data=ItemCreate(name="Item A", lodestone_id="1")
    )
    await crud.create_item(
        db=async_db_session, item_data=ItemCreate(name="Item B", lodestone_id="2")
    )

    all_items = await crud.get_items(db=async_db_session)
    assert len(all_items) == 2


@pytest.mark.asyncio
async def test_update_item(async_db_session):
    """Tests updating an existing item's details."""
    item_data = ItemCreate(name="Old Name", lodestone_id="1234")
    item_to_update = await crud.create_item(db=async_db_session, item_data=item_data)

    update_data = ItemUpdate(name="New Shiny Name")
    updated_item = await crud.update_item(
        db=async_db_session,
        item=item_to_update,
        update_data=update_data,
    )

    assert updated_item.name == "New Shiny Name"
    assert updated_item.lodestone_id == "1234"  # Should not have changed


@pytest.mark.asyncio
async def test_delete_item(async_db_session):
    """Tests that an item can be deleted successfully."""
    item_data = ItemCreate(name="To Be Deleted", lodestone_id="9999")
    item_to_delete = await crud.create_item(db=async_db_session, item_data=item_data)
    item_id = item_to_delete.id

    await crud.delete_item(db=async_db_session, item=item_to_delete)

    # Verify it's gone
    deleted_item = await crud.get_item_by_id(db=async_db_session, item_id=item_id)
    assert deleted_item is None
