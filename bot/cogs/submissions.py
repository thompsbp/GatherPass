# ==============================================================================
# FILE: bot/cogs/submissions.py
# ==============================================================================
# This file contains the core gameplay command: /submit.

import discord
import httpx
from discord.ext import commands
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SubmissionCog(commands.Cog):
    def __init__(
        self,
        bot: discord.Bot,
        api_client: APIClient,
        admin_channel_id: int,
        bot_api_key: str,
    ):
        self.bot = bot
        self.api_client = api_client
        self.admin_channel_id = admin_channel_id
        self.bot_api_key = bot_api_key

    # --- Autocomplete Functions ---

    async def search_seasons(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding seasons by name."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            seasons = await self.api_client.get_seasons(auth=auth, name_query=ctx.value)
            return [
                discord.OptionChoice(name=s["name"], value=str(s["id"]))
                for s in seasons
            ][:25]
        except Exception:
            return []

    async def search_season_items(self, ctx: discord.AutocompleteContext):
        """Chained autocomplete for items based on the selected season."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            season_id_str = ctx.options.get("season")

            target_season_id: int
            if season_id_str:
                target_season_id = int(season_id_str)
            else:
                current_season = await self.api_client.get_current_season(auth=auth)
                target_season_id = current_season["id"]

            season_items = await self.api_client.get_items_for_season(
                auth=auth, season_id=target_season_id
            )

            query = ctx.value.lower()
            return [
                discord.OptionChoice(name=si["item"]["name"], value=str(si["id"]))
                for si in season_items
                if query in si["item"]["name"].lower()
            ][:25]
        except Exception:
            return []

    async def search_registered_users(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding registered users by in-game name."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            users = await self.api_client.get_users(auth=auth, name_query=ctx.value)
            return [
                discord.OptionChoice(name=u["in_game_name"], value=str(u["id"]))
                for u in users
            ][:25]
        except Exception as e:
            print(f"🚨 ERROR in search_registered_users autocomplete: {e}")
            return []

    # --- Slash Command ---
    @commands.slash_command(
        name="submit", description="Submit an item for points on behalf of a user."
    )
    async def submit(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(
            str,
            "The user to submit for (start typing their in-game name).",
            autocomplete=search_registered_users,
            required=True,
        ),
        item: discord.Option(
            str, "The item you are submitting.", autocomplete=search_season_items
        ),
        quantity: discord.Option(
            int, "The quantity of the item you are submitting.", min_value=1
        ),
        season: discord.Option(
            str,
            "Optional: The season to submit to. Defaults to the current season.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Admin-Only) Handles item submissions for points."""
        await ctx.defer(ephemeral=True)

        try:
            # The auth provider uses the admin's ID for authorization
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            # The 'user' variable from autocomplete is the target user's internal API ID
            target_user_id = int(user)

            # The 'item' value from autocomplete is the season_item_id
            target_season_item_id = int(item)

            result = await self.api_client.create_submission(
                auth=auth,
                user_id=target_user_id,
                season_item_id=target_season_item_id,
                quantity=quantity,
            )

            # Prepare a nice confirmation message
            submitted_item = result["season_item"]["item"]
            season_name = result["season_item"]["season"]["name"]
            points_earned = result["total_point_value"]
            target_user_ign = result["user"]["in_game_name"]

            success_message = (
                f"✅ Submission successful!\n\n"
                f"You submitted **{quantity}x {submitted_item['name']}** "
                f"for **{target_user_ign}** in **{season_name}** for **{points_earned}** points."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                # The log message now correctly identifies the target user by name.
                log_message = (
                    f"📝 {ctx.author.mention} submitted **{quantity}x {submitted_item['name']}** "
                    f"for **{target_user_ign}** in **{season_name}** (+{points_earned} points)."
                )
                await admin_channel.send(log_message)

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /submit command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SubmissionCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
