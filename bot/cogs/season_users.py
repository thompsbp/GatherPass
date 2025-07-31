# ==============================================================================
# FILE: bot/cogs/season_users.py
# ==============================================================================
# This file contains commands for managing user participation in seasons.

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SeasonUserCog(commands.Cog):
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

    # --- Slash Commands ---
    @commands.slash_command(
        name="join_season",
        description="Register yourself to participate in a season.",
    )
    async def join_season(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season you want to join. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Registered Users) Registers the user for a season to begin submitting items."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            target_season_id: int
            if season:
                target_season_id = int(season)
            else:
                latest_season = await self.api_client.get_latest_season(auth=auth)
                target_season_id = latest_season["id"]

            result = await self.api_client.register_user_for_season(
                auth=auth,
                season_id=target_season_id,
                discord_id=ctx.author.id,
            )

            success_message = (
                f"✅ You have successfully joined season **{result['season']['name']}**! "
                f"You can now start submitting items in game."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"✅ {ctx.author.mention} has joined season number {result['season']['number']} **{result['season']['name']}**."
                )

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /join_season command: {e}")

    @commands.slash_command(
        name="season_participants",
        description="View the list of users registered for a season.",
    )
    async def season_participants(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season you want to view. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Registered Users) Fetches and displays the participant list for a season."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            target_season_id: int
            target_season_name: str

            if season:
                target_season_id = int(season)
                all_seasons = await self.api_client.get_seasons(auth=auth)
                target_season = next(
                    (s for s in all_seasons if s["id"] == target_season_id), None
                )
                target_season_name = (
                    target_season["name"]
                    if target_season
                    else f"Season ID {target_season_id}"
                )
            else:
                latest_season = await self.api_client.get_latest_season(auth=auth)
                target_season_id = latest_season["id"]
                target_season_name = latest_season["name"]

            participant_data = await self.api_client.get_season_users(
                auth=auth, season_id=target_season_id
            )

            if not participant_data:
                await ctx.respond(
                    f"No users have joined **{target_season_name}** yet.",
                    ephemeral=True,
                )
                return

            participant_data.sort(key=lambda x: x["user"]["in_game_name"])

            roster_pages = []
            page_content = ""
            for i, season_user in enumerate(participant_data, 1):
                user = season_user["user"]
                page_content += f"• {user['in_game_name']}\n"

                if i % 15 == 0 and i != len(participant_data):
                    embed = discord.Embed(
                        title=f"Participants for {target_season_name}",
                        description=page_content,
                        color=discord.Color.blurple(),
                    )
                    roster_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title=f"Participants for {target_season_name}",
                    description=page_content,
                    color=discord.Color.blurple(),
                )
                roster_pages.append(embed)

            paginator = pages.Paginator(
                pages=roster_pages, disable_on_timeout=True, timeout=60
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
            print(f"An unexpected error in /season_participants command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SeasonUserCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
