# ==============================================================================
# FILE: bot/cogs/season_ranks.py
# ==============================================================================
# This file contains commands for viewing ranks within a season.

from datetime import datetime

import discord
import httpx
from discord.ext import commands
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SeasonRankCog(commands.Cog):
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
        query = ctx.value
        if not query:
            return []
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            seasons = await self.api_client.get_seasons(auth=auth, name_query=query)
            return [
                discord.OptionChoice(name=s["name"], value=str(s["id"]))
                for s in seasons
            ]
        except Exception:
            return []

    # --- Slash Command ---
    @commands.slash_command(
        name="season_ranks",
        description="View the rank progression for a specific season.",
    )
    async def season_ranks(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season you want to view. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Registered Users) Fetches and displays the rank list for a season."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            target_season_id: int
            target_season_name: str

            if season:
                target_season_id = int(season)
                # This is inefficient but necessary without a get_season_by_id client method
                all_seasons = await self.api_client.get_seasons(auth=auth)
                target_season_obj = next(
                    (s for s in all_seasons if s["id"] == target_season_id), None
                )
                target_season_name = (
                    target_season_obj["name"]
                    if target_season_obj
                    else f"Season ID {target_season_id}"
                )
            else:
                latest_season = await self.api_client.get_latest_season(auth=auth)
                target_season_id = latest_season["id"]
                target_season_name = latest_season["name"]

            rank_list = await self.api_client.get_season_ranks(
                auth=auth, season_id=target_season_id
            )

            if not rank_list:
                await ctx.respond(
                    f"No ranks have been added to **{target_season_name}** yet.",
                    ephemeral=True,
                )
                return

            description = ""
            for season_rank in rank_list:
                rank = season_rank["rank"]
                description += (
                    f"**Rank {season_rank['number']}: {rank['name']}**\n"
                    f"Requires: `{season_rank['required_points']:,}` points\n\n"
                )

            embed = discord.Embed(
                title=f"Rank Progression for {target_season_name}",
                description=description,
                color=discord.Color.purple(),
            )
            await ctx.respond(embed=embed, ephemeral=True)

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /season_ranks command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SeasonRankCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
