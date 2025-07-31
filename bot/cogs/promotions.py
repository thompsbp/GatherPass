# ==============================================================================
# FILE: bot/cogs/promotions.py
# ==============================================================================
# This file contains commands related to user promotions and rank management.

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class PromotionCog(commands.Cog):
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
        name="check_promotions",
        description="Check which users are eligible for a rank promotion in a season.",
    )
    async def check_promotions(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "Optional: The season to check. Defaults to the latest one.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Admin-Only) Checks for users who are eligible for a rank promotion."""
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

            candidates = await self.api_client.check_promotions(
                auth=auth, season_id=target_season_id
            )

            if not candidates:
                await ctx.respond(
                    f"✅ No users are currently eligible for promotion in **{target_season_name}**.",
                    ephemeral=True,
                )
                return

            promo_pages = []
            page_content = ""
            for i, candidate in enumerate(candidates, 1):
                user = candidate["user"]
                current_rank_name = (
                    candidate["current_rank"]["name"]
                    if candidate["current_rank"]
                    else "None"
                )
                eligible_rank_name = candidate["eligible_rank"]["name"]

                page_content += (
                    f"**{user['in_game_name']}**\n"
                    f"Points: `{candidate['total_points']:,}`\n"
                    f"Current Rank: **{current_rank_name}**\n"
                    f"Eligible For: **{eligible_rank_name}**\n\n"
                )
                if i % 5 == 0 and i != len(candidates):
                    embed = discord.Embed(
                        title=f"Promotion Candidates for {target_season_name}",
                        description=page_content,
                        color=discord.Color.orange(),
                    )
                    promo_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title=f"Promotion Candidates for {target_season_name}",
                    description=page_content,
                    color=discord.Color.orange(),
                )
                promo_pages.append(embed)

            paginator = pages.Paginator(
                pages=promo_pages, disable_on_timeout=True, timeout=120
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
            print(f"An unexpected error in /check_promotions command: {e}")


# This function is required for the bot to load the cog
def setup(bot: discord.Bot):
    bot.add_cog(
        PromotionCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
