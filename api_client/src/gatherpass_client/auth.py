# ==============================================================================
# FILE: api_client/auth.py
# ==============================================================================
# This file defines authentication strategy classes for the APIClient.


class AuthStrategy:
    """Base class for authentication strategies."""

    def get_headers(self) -> dict:
        raise NotImplementedError


class BotAuth(AuthStrategy):
    """
    Authentication strategy for the bot acting on behalf of a user.
    """

    def __init__(self, api_key: str, user_discord_id: int):
        self.api_key = api_key
        self.user_discord_id = user_discord_id

    def get_headers(self) -> dict:
        return {
            "X-API-Key": self.api_key,
            "X-User-Discord-ID": str(self.user_discord_id),
        }


class JWTAuth(AuthStrategy):
    """
    Authentication strategy for a user making a direct request with a JWT.
    """

    def __init__(self, jwt_token: str):
        self.jwt_token = jwt_token

    def get_headers(self) -> dict:
        return {"Authorization": f"Bearer {self.jwt_token}"}


class BotOnlyAuth(AuthStrategy):
    """Authentication strategy for actions only the bot can perform, like registration."""

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self) -> dict:
        return {"X-API-Key": self.api_key}
