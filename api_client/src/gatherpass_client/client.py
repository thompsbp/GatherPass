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

    async def get_users(self, auth: AuthStrategy):
        """Fetches all users from the API using the provided auth strategy."""
        headers = {"Content-Type": "application/json"}
        headers.update(auth.get_headers())

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/users/", headers=headers)
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            raise e

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
