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

    async def search_registered_users(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding registered users by in-game name."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            users = await self.api_client.get_users(auth=auth, name_query=ctx.value)
            # The value is the user's internal API ID, which the promotion endpoint needs.
            return [
                discord.OptionChoice(name=u["in_game_name"], value=str(u["id"]))
                for u in users
            ][:25]
        except Exception:
            return []

    async def search_season_ranks(self, ctx: discord.AutocompleteContext):
        """
        Chained autocomplete for ranks, dependent on the selected season.
        """
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )

            # Get the season ID from the 'season' option the user has already filled out.
            season_id_str = ctx.options.get("season")
            if not season_id_str:
                return [
                    discord.OptionChoice(
                        name="Please select a season first.", value="0"
                    )
                ]

            season_ranks = await self.api_client.get_season_ranks(
                auth=auth, season_id=int(season_id_str)
            )

            query = ctx.value.lower()
            # The value is the season_rank's unique ID.
            return [
                discord.OptionChoice(name=sr["rank"]["name"], value=str(sr["id"]))
                for sr in season_ranks
                if query in sr["rank"]["name"].lower()
            ][:25]
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

    @commands.slash_command(
        name="promote_user",
        description="Promote a user to a rank, backfilling any missed ranks.",
    )
    async def promote_user(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str, "The season for this promotion.", autocomplete=search_seasons
        ),
        user: discord.Option(
            str, "The user to promote.", autocomplete=search_registered_users
        ),
        rank: discord.Option(
            str,
            "The target rank to promote the user to.",
            autocomplete=search_season_ranks,
        ),
    ):
        """(Admin-Only) Promotes a user to a target rank."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_season_id = int(season)
            target_user_id = int(user)
            target_season_rank_id = int(rank)

            if target_season_rank_id == 0:
                await ctx.respond(
                    "❌ Invalid rank selected. Please ensure you select a season first.",
                    ephemeral=True,
                )
                return

            promotion_result = await self.api_client.promote_user_to_rank(
                auth=auth,
                user_id=target_user_id,
                season_id=target_season_id,
                season_rank_id=target_season_rank_id,
            )

            awarded_ranks = promotion_result["awarded_ranks"]
            awarded_prizes = promotion_result["awarded_prizes"]

            all_users = await self.api_client.get_users(auth=auth)
            target_user_obj = next(
                (u for u in all_users if u["id"] == target_user_id), None
            )
            user_name = (
                target_user_obj["in_game_name"] if target_user_obj else "Unknown User"
            )

            all_seasons = await self.api_client.get_seasons(auth=auth)
            target_season_obj = next(
                (s for s in all_seasons if s["id"] == target_season_id), None
            )
            season_name = (
                target_season_obj["name"] if target_season_obj else "Unknown Season"
            )

            awarded_rank_names = [
                f"**{award['season_rank']['rank']['name']}**" for award in awarded_ranks
            ]

            success_message = (
                f"✅ **{user_name}** has been promoted in **{season_name}**!\n\n"
                f"Newly Awarded Ranks:\n" + ", ".join(awarded_rank_names)
            )
            if awarded_prizes:
                awarded_prize_names = [
                    f"- {prize['season_prize']['prize']['description']}"
                    for prize in awarded_prizes
                ]
                success_message += "\n\n**Prizes Awarded:**\n" + "\n".join(
                    awarded_prize_names
                )

            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                final_rank_name = awarded_ranks[-1]["season_rank"]["rank"]["name"]
                await admin_channel.send(
                    f"🏆 {ctx.author.mention} promoted **{user_name}** to **{final_rank_name}** in **{season_name}**."
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
            print(f"An unexpected error in /promote_user command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        PromotionCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
