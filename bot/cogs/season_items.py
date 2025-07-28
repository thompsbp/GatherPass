# ==============================================================================
# FILE: bot/cogs/season_items.py
# ==============================================================================
# This file contains commands for managing items within a season.

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SeasonItemCog(commands.Cog):
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

    async def search_items(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding items by name."""
        query = ctx.value
        if not query:
            return []
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            items = await self.api_client.get_items(auth=auth, name_query=query)
            return [
                discord.OptionChoice(name=i["name"], value=str(i["id"])) for i in items
            ]
        except Exception:
            return []

    # --- Slash Command ---

    @commands.slash_command(
        name="add_season_item",
        description="Add an item to a season with a specific point value.",
    )
    async def add_season_item(
        self,
        ctx: discord.ApplicationContext,
        item: discord.Option(
            str, "The item to add (start typing to search).", autocomplete=search_items
        ),
        point_value: discord.Option(int, "The number of points this item is worth."),
        season: discord.Option(
            str,
            "Optional: The season to add to. Defaults to the latest season.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Admin-Only) Associates an item with a season."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_item_id = int(item)

            target_season_id: int
            if season:
                target_season_id = int(season)
            else:
                # If no season is specified, fetch the latest one
                latest_season = await self.api_client.get_latest_season(auth=auth)
                target_season_id = latest_season["id"]

            result = await self.api_client.add_item_to_season(
                auth=auth,
                season_id=target_season_id,
                item_id=target_item_id,
                point_value=point_value,
            )

            # Format a nice success message
            success_message = (
                f"✅ Successfully added item **{result['item']['name']}** "
                f"to **{result['season']['name']}** "
                f"with a value of **{result['point_value']}** points."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"🔗 {ctx.author.mention} added **{result['item']['name']}** to **{result['season']['name']}**."
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
            print(f"An unexpected error in /add_season_item command: {e}")

    @commands.slash_command(
        name="season_items",
        description="List all items for a specific season.",
    )
    async def season_items(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str,
            "The season to view items for (start typing to search).",
            autocomplete=search_seasons,
        ),
    ):
        """(Registered Users) Fetches and displays all items for a given season."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_season_id = int(season)

            item_list = await self.api_client.get_items_for_season(
                auth=auth, season_id=target_season_id
            )

            if not item_list:
                await ctx.respond(
                    "No items have been added to this season yet.", ephemeral=True
                )
                return

            # Get the season name from the first item for the title
            season_name = item_list[0]["season"]["name"]

            item_pages = []
            page_content = ""
            for i, season_item in enumerate(item_list, 1):
                item = season_item["item"]
                lodestone_link = (
                    f"<{self.bot.lodestone_base_url}{item['lodestone_id']}>"
                )
                page_content += (
                    f"**{item['name']}** - {season_item['point_value']} points\n"
                    f"Lodestone: {lodestone_link}\n\n"
                )
                if i % 10 == 0 and i != len(item_list):
                    embed = discord.Embed(
                        title=f"Items for {season_name}",
                        description=page_content,
                        color=discord.Color.green(),
                    )
                    item_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title=f"Items for {season_name}",
                    description=page_content,
                    color=discord.Color.green(),
                )
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
            print(f"An unexpected error in /season_items command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SeasonItemCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
