# ==============================================================================
# FILE: bot/cogs/seasons.py
# ==============================================================================
# This file contains all season-related commands for the bot.

from datetime import datetime

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SeasonCog(commands.Cog):
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

    @commands.slash_command(name="add_season", description="Create a new event season.")
    async def add_season(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(
            str, "The name of the season (e.g., Season 1: The First Age)."
        ),
        number: discord.Option(int, "The number of the season (e.g., 1)."),
        start_date: discord.Option(str, "The start date in YYYY-MM-DD format."),
        end_date: discord.Option(str, "The end date in YYYY-MM-DD format."),
    ):
        """
        (Admin-Only) Creates a new season in the database.
        """
        await ctx.defer(ephemeral=True)

        try:
            # Append time and timezone to the dates to create valid ISO 8601 strings
            start_iso = f"{start_date}T00:00:00Z"
            end_iso = f"{end_date}T23:59:59Z"

            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )

            new_season = await self.api_client.create_season(
                auth=auth_provider,
                name=name,
                number=number,
                start_date=start_iso,
                end_date=end_iso,
            )

            success_message = (
                f"✅ Season **{new_season['name']}** (Season {new_season['number']}) "
                f"has been successfully created."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"🗓️ {ctx.author.mention} created a new season: **{new_season['name']}**."
                )

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred. Please check the date format (YYYY-MM-DD).",
                ephemeral=True,
            )
            print(f"An unexpected error in /add_season command: {e}")

    @commands.slash_command(name="seasons", description="List all event seasons.")
    async def seasons(self, ctx: discord.ApplicationContext):
        """
        (Registered Users) Fetches a list of all seasons from the API and displays it.
        """
        await ctx.defer(ephemeral=True)

        try:
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )
            season_list = await self.api_client.get_seasons(auth=auth_provider)

            if not season_list:
                await ctx.respond("No seasons have been created yet.", ephemeral=True)
                return

            season_pages = []
            page_content = ""
            for i, season in enumerate(season_list, 1):
                # Parse the ISO date strings from the API into datetime objects
                start_dt = datetime.fromisoformat(
                    season["start_date"].replace("Z", "+00:00")
                )
                end_dt = datetime.fromisoformat(
                    season["end_date"].replace("Z", "+00:00")
                )

                # Convert to integer Unix timestamps and use Discord's markdown format
                start_timestamp = int(start_dt.timestamp())
                end_timestamp = int(end_dt.timestamp())

                page_content += (
                    f"### {season['name']} (Season {season['number']})\n"
                    f"**Duration:** <t:{start_timestamp}:D> to <t:{end_timestamp}:D>\n"
                    f"*DB ID: `{season['id']}`*\n\n"
                )
                if i % 3 == 0 and i != len(season_list):
                    embed = discord.Embed(
                        title="Event Seasons",
                        description=page_content,
                        color=discord.Color.blue(),
                    )
                    season_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title="Event Seasons",
                    description=page_content,
                    color=discord.Color.blue(),
                )
                season_pages.append(embed)

            paginator = pages.Paginator(
                pages=season_pages, disable_on_timeout=True, timeout=60
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
            print(f"An unexpected error in /seasons command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(SeasonCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key))
