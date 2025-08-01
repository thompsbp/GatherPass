# ==============================================================================
# FILE: bot/cogs/summaries.py
# ==============================================================================
# This file contains commands for viewing user summaries and progress.

import discord
import httpx
from discord.ext import commands
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SummaryCog(commands.Cog):
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

    @commands.slash_command(
        name="me",
        description="View your personal progress summary for the current season.",
    )
    async def me(self, ctx: discord.ApplicationContext):
        """(Registered Users) Fetches and displays the user's own progress summary."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            current_season = await self.api_client.get_current_season(auth=auth)
            season_id = current_season["id"]
            season_name = current_season["name"]

            summary = await self.api_client.get_my_season_summary(
                auth=auth, season_id=season_id
            )

            embed = discord.Embed(
                title=f"Your Progress in {season_name}",
                color=discord.Color.og_blurple(),
            )
            embed.set_author(
                name=ctx.author.display_name, icon_url=ctx.author.display_avatar.url
            )

            embed.add_field(
                name="Total Points",
                value=f"**{summary['total_points']:,}**",
                inline=False,
            )

            current_rank_name = (
                summary["current_rank"]["name"]
                if summary["current_rank"]
                else "Unranked"
            )
            embed.add_field(
                name="Current Rank", value=f"**{current_rank_name}**", inline=False
            )

            if summary["awarded_prizes"]:
                prize_list = "\n".join(
                    [f"- {prize['description']}" for prize in summary["awarded_prizes"]]
                )
                embed.add_field(name="Prizes Awarded", value=prize_list, inline=False)
            else:
                embed.add_field(name="Prizes Awarded", value="None yet!", inline=False)

            await ctx.respond(embed=embed, ephemeral=True)

        except httpx.HTTPStatusError as e:
            error_detail = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            if "not registered" in error_detail:
                await ctx.respond(
                    f"You have not joined the current season yet! Use `/join_season` to participate.",
                    ephemeral=True,
                )
            else:
                await ctx.respond(f"❌ **Error:** {error_detail}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /me command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(SummaryCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key))
