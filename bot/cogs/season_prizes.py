# ==============================================================================
# FILE: bot/cogs/season_prizes.py
# ==============================================================================
# This file contains commands for viewing prizes within a season.

from itertools import groupby

import discord
import httpx
from discord.ext import commands
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SeasonPrizeCog(commands.Cog):
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
        name="season_prizes",
        description="View the prize list for a specific season.",
    )
    async def season_prizes(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season you want to view. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Registered Users) Fetches and displays the prize list for a season."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            target_season_id: int
            target_season_name: str

            if season:
                target_season_id = int(season)
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

            prize_list = await self.api_client.get_season_prizes(
                auth=auth, season_id=target_season_id
            )

            if not prize_list:
                await ctx.respond(
                    f"No prizes have been added to **{target_season_name}** yet.",
                    ephemeral=True,
                )
                return

            description = ""
            # Group prizes by their rank name
            for rank_name, prizes in groupby(
                prize_list, key=lambda p: p["season_rank"]["rank"]["name"]
            ):
                description += f"Rank: **{rank_name}**\n"
                description += f"Prizes:\n"
                for season_prize in prizes:
                    prize = season_prize["prize"]
                    description += f"- {prize['description']}\n"
                description += "\n"

            embed = discord.Embed(
                title=f"Prizes for {target_season_name}",
                description=description,
                color=discord.Color.from_rgb(255, 215, 0),  # Gold color
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
            print(f"An unexpected error in /season_prizes command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SeasonPrizeCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
