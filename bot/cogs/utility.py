# ==============================================================================
# FILE: bot/cogs/utility.py
# ==============================================================================
# This file contains general-purpose utility and debugging commands.

import discord
from discord.ext import commands


class UtilityCog(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(
        name="ping", description="A simple command to check if the bot is responsive."
    )
    async def ping(self, ctx: discord.ApplicationContext):
        """A simple test command."""
        await ctx.respond("Pong!", ephemeral=True)


# This function is required for the bot to load the cog
def setup(bot: discord.Bot):
    bot.add_cog(UtilityCog(bot))
