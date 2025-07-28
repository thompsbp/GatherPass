# ==============================================================================
# FILE: bot/cogs/items.py
# ==============================================================================
# This file contains all item-related commands for the bot.

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class ItemCog(commands.Cog):
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
        name="add_item", description="Add a new item to the database."
    )
    async def add_item(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(str, "The in-game name of the item."),
        lodestone_id: discord.Option(str, "The item's ID from its Lodestone URL."),
    ):
        """
        (Admin-Only) Creates a new item that can be used in seasons.
        """
        await ctx.defer(ephemeral=True)

        try:
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )

            new_item = await self.api_client.create_item(
                auth=auth_provider,
                name=name,
                lodestone_id=lodestone_id,
            )

            success_message = (
                f"✅ Item **{new_item['name']}** (`{new_item['lodestone_id']}`) "
                f"has been successfully added to the database."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"🔩 {ctx.author.mention} added a new item: **{new_item['name']}**."
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
            print(f"An unexpected error in /add_item command: {e}")

    @commands.slash_command(name="items", description="List all available items.")
    async def items(
        self,
        ctx: discord.ApplicationContext,
        name: discord.Option(
            str, "An optional name to filter the item list.", required=False
        ),
    ):
        """
        (Registered Users) Fetches a list of all items from the API, with an
        optional filter, and displays it in a paginated embed.
        """
        await ctx.defer(ephemeral=True)

        try:
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )
            item_list = await self.api_client.get_items(
                auth=auth_provider, name_query=name
            )

            if not item_list:
                await ctx.respond(
                    "No items found matching your criteria.", ephemeral=True
                )
                return

            item_pages = []
            page_content = ""
            for i, item in enumerate(item_list, 1):
                lodestone_link = f"<{self.bot.lodestone_base_url}playguide/db/item/{item['lodestone_id']}>"
                page_content += (
                    f"**{item['name']}**\n"
                    f"- DB ID: `{item['id']}`\n"
                    f"- Lodestone ID: `{item['lodestone_id']}` ({lodestone_link})\n\n"
                )
                if i % 5 == 0 and i != len(item_list):
                    embed = discord.Embed(
                        title="Available Items", description=page_content
                    )
                    item_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(title="Available Items", description=page_content)
                item_pages.append(embed)

            paginator = pages.Paginator(
                pages=item_pages, disable_on_timeout=True, timeout=60
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
            print(f"An unexpected error in /items command: {e}")


# This function is required for the bot to load the cog
def setup(bot: discord.Bot):
    bot.add_cog(ItemCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key))
