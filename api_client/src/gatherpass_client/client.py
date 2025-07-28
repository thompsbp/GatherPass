# ==============================================================================
# FILE: api_client/client.py
# ==============================================================================
# This file contains the standalone client for interacting with the Gather Pass API.

import httpx

from .auth import AuthStrategy


class APIClient:
    """An async client for the Gather Pass API."""

    def __init__(self, base_url: str):
        self.base_url = base_url.rstrip("/")

    async def get_users(self, auth: AuthStrategy, name_query: str | None = None):
        """
        Fetches users from the API using the provided auth strategy.
        Optionally filters by the start of an in-game name.
        """
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        params = {}
        if name_query:
            params["in_game_name"] = name_query

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/users/", headers=headers, params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    # --- Users ---
    async def create_user(
        self, auth: AuthStrategy, discord_id: int, in_game_name: str, lodestone_id: str
    ):
        """Creates a new user via the API using the provided auth strategy."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        payload = {
            "discord_id": discord_id,
            "in_game_name": in_game_name,
            "lodestone_id": lodestone_id,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/users/", headers=headers, json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def update_user(
        self,
        auth: AuthStrategy,
        user_id: int,
        status: str | None = None,
        is_admin: bool | None = None,
    ):
        """Updates a user's record via the API."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        payload = {}
        if status is not None:
            payload["status"] = status
        if is_admin is not None:
            payload["admin"] = is_admin

        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/users/{user_id}", headers=headers, json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    # --- Items ---
    async def get_items(self, auth: AuthStrategy, name_query: str | None = None):
        """
        Fetches items from the API using the provided auth strategy.
        Optionally filters by the start of an item name.
        """
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        params = {}
        if name_query:
            params["name"] = name_query

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/items/", headers=headers, params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def create_item(self, auth: AuthStrategy, name: str, lodestone_id: str):
        """Creates a new item via the API."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        payload = {"name": name, "lodestone_id": lodestone_id}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/items/", headers=headers, json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    # --- Seasons ---
    async def create_season(
        self,
        auth: AuthStrategy,
        name: str,
        number: int,
        start_date: str,
        end_date: str,
    ):
        """Creates a new season via the API."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        payload = {
            "name": name,
            "number": number,
            "start_date": start_date,
            "end_date": end_date,
        }

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/seasons/", headers=headers, json=payload
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def get_seasons(self, auth: AuthStrategy, name_query: str | None = None):
        """Fetches seasons from the API, with an optional name filter."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        params = {}
        if name_query:
            params["name"] = name_query

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seasons/", headers=headers, params=params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def get_current_season(self, auth: AuthStrategy):
        """Fetches the season with the highest number from the API."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seasons/current", headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def get_latest_season(self, auth: AuthStrategy):
        """Fetches the season with the highest number from the API."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seasons/latest", headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    # --- Season Items ---
    async def add_item_to_season(
        self, auth: AuthStrategy, season_id: int, item_id: int, point_value: int
    ):
        """Adds an item to a season with a specific point value."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        payload = {"item_id": item_id, "point_value": point_value}

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/seasons/{season_id}/items",
                    headers=headers,
                    json=payload,
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

    async def get_items_for_season(self, auth: AuthStrategy, season_id: int):
        """Fetches all items for a specific season, sorted by name."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/seasons/{season_id}/items", headers=headers
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e
