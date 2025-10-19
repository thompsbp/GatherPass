# ==============================================================================
# FILE: bot/cogs/leaderboard.py
# ==============================================================================
# This file contains the /leaderboard command for viewing season progress.

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class LeaderboardCog(commands.Cog):
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

    # --- Slash Command ---
    @commands.slash_command(
        name="leaderboard",
        description="View the points leaderboard for a season.",
    )
    async def leaderboard(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season you want to view. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Registered Users) Fetches and displays the points leaderboard for a season."""
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

            leaderboard_data = await self.api_client.get_season_users(
                auth=auth, season_id=target_season_id, order="points_desc"
            )

            if not leaderboard_data:
                await ctx.respond(
                    f"No users have joined **{target_season_name}** yet.",
                    ephemeral=True,
                )
                return

            leaderboard_pages = []
            page_content = ""
            for i, season_user in enumerate(leaderboard_data, 1):
                user = season_user["user"]
                rank_emoji = ""
                if i == 1:
                    rank_emoji = "🥇 "
                elif i == 2:
                    rank_emoji = "🥈 "
                elif i == 3:
                    rank_emoji = "🥉 "

                page_content += f"{rank_emoji}**{i}. {user['in_game_name']}** - {season_user['total_points']:,} points\n"

                if i % 10 == 0 and i != len(leaderboard_data):
                    embed = discord.Embed(
                        title=f"Leaderboard for {target_season_name}",
                        description=page_content,
                        color=discord.Color.gold(),
                    )
                    leaderboard_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title=f"Leaderboard for {target_season_name}",
                    description=page_content,
                    color=discord.Color.gold(),
                )
                leaderboard_pages.append(embed)

            paginator = pages.Paginator(
                pages=leaderboard_pages, disable_on_timeout=True, timeout=120
            )
            await paginator.respond(ctx.interaction, ephemeral=True)

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /leaderboard command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        LeaderboardCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
