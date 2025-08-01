# ==============================================================================
# FILE: bot/cogs/submissions.py
# ==============================================================================
# This file contains the core gameplay command: /submit.
from datetime import datetime

import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth


class SubmissionCog(commands.Cog):
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

    async def search_season_items(self, ctx: discord.AutocompleteContext):
        """Chained autocomplete for items based on the selected season."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            season_id_str = ctx.options.get("season")

            target_season_id: int
            if season_id_str:
                target_season_id = int(season_id_str)
            else:
                current_season = await self.api_client.get_current_season(auth=auth)
                target_season_id = current_season["id"]

            season_items = await self.api_client.get_items_for_season(
                auth=auth, season_id=target_season_id
            )

            query = ctx.value.lower()
            return [
                discord.OptionChoice(name=si["item"]["name"], value=str(si["id"]))
                for si in season_items
                if query in si["item"]["name"].lower()
            ][:25]
        except Exception:
            return []

    async def search_registered_users(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding registered users by in-game name."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            users = await self.api_client.get_users(auth=auth, name_query=ctx.value)
            return [
                discord.OptionChoice(name=u["in_game_name"], value=str(u["id"]))
                for u in users
            ][:25]
        except Exception as e:
            print(f"🚨 ERROR in search_registered_users autocomplete: {e}")
            return []

    # --- Slash Command ---
    @commands.slash_command(
        name="submit", description="Submit an item for points on behalf of a user."
    )
    async def submit(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(
            str,
            "The user to submit for (start typing their in-game name).",
            autocomplete=search_registered_users,
            required=True,
        ),
        item: discord.Option(
            str, "The item you are submitting.", autocomplete=search_season_items
        ),
        quantity: discord.Option(
            int, "The quantity of the item you are submitting.", min_value=1
        ),
        season: discord.Option(
            str,
            "Optional: The season to submit to. Defaults to the current season.",
            autocomplete=search_seasons,
            required=False,
        ),
    ):
        """(Admin-Only) Handles item submissions for points."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)

            target_user_id = int(user)

            target_season_item_id = int(item)

            result = await self.api_client.create_submission(
                auth=auth,
                user_id=target_user_id,
                season_item_id=target_season_item_id,
                quantity=quantity,
            )

            submitted_item = result["season_item"]["item"]
            season_name = result["season_item"]["season"]["name"]
            points_earned = result["total_point_value"]
            target_user_ign = result["user"]["in_game_name"]

            success_message = (
                f"✅ Submission successful!\n\n"
                f"You submitted **{quantity}x {submitted_item['name']}** "
                f"for **{target_user_ign}** in **{season_name}** for **{points_earned}** points."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                log_message = (
                    f"📝 {ctx.author.mention} submitted **{quantity}x {submitted_item['name']}** "
                    f"for **{target_user_ign}** in **{season_name}** (+{points_earned} points)."
                )
                await admin_channel.send(log_message)

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error in /submit command: {e}")

    async def search_registered_users(self, ctx: discord.AutocompleteContext):
        """Autocomplete for finding registered users by in-game name."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )
            users = await self.api_client.get_users(auth=auth, name_query=ctx.value)
            return [
                discord.OptionChoice(name=u["in_game_name"], value=str(u["id"]))
                for u in users
            ][:25]
        except Exception:
            return []

    async def search_user_submissions(self, ctx: discord.AutocompleteContext):
        """Chained autocomplete for a user's submissions in a selected season."""
        try:
            auth = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )

            # Get the user and season IDs from the other command options
            user_id_str = ctx.options.get("user")
            season_id_str = ctx.options.get("season")

            # If either user or season isn't selected yet, we can't search for submissions.
            if not user_id_str or not season_id_str:
                return [
                    discord.OptionChoice(
                        name="Please select a user and season first.", value="0"
                    )
                ]

            target_user_id = int(user_id_str)
            target_season_id = int(season_id_str)

            submissions = await self.api_client.get_submissions(
                auth=auth, user_id=target_user_id, season_id=target_season_id
            )

            query = ctx.value.lower()

            choices = []
            for sub in submissions:
                item_name = sub["season_item"]["item"]["name"]
                choice_name = f"ID: {sub['id']} - {sub['quantity']}x {item_name} ({sub['total_point_value']} pts)"
                if query in choice_name.lower():
                    choices.append(
                        discord.OptionChoice(name=choice_name, value=str(sub["id"]))
                    )

            return choices[:25]
        except Exception:
            return []

    # --- The New Command ---
    @commands.slash_command(
        name="edit_submission",
        description="Edit the quantity of a previous submission.",
    )
    async def edit_submission(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str, "The season the submission is in.", autocomplete=search_seasons
        ),
        user: discord.Option(
            str,
            "The user whose submission you are editing.",
            autocomplete=search_registered_users,
        ),
        submission: discord.Option(
            str,
            "The specific submission to edit.",
            autocomplete=search_user_submissions,
        ),
        new_quantity: discord.Option(
            int, "The new quantity for the item.", min_value=1
        ),
    ):
        """(Admin-Only) Edits a submission and corrects point totals."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_submission_id = int(submission)

            if target_submission_id == 0:
                await ctx.respond(
                    "❌ Invalid submission selected. Please ensure you select a valid submission from the list.",
                    ephemeral=True,
                )
                return

            updated_submission = await self.api_client.update_submission(
                auth=auth,
                submission_id=target_submission_id,
                new_quantity=new_quantity,
            )

            user_ign = updated_submission["user"]["in_game_name"]
            item_name = updated_submission["season_item"]["item"]["name"]

            success_message = (
                f"✅ Submission updated successfully!\n\n"
                f"**{user_ign}**'s submission of **{item_name}** "
                f"is now **{updated_submission['quantity']}x** "
                f"for a new total of **{updated_submission['total_point_value']}** points."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"✏️ {ctx.author.mention} edited a submission for **{user_ign}**."
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
            print(f"An unexpected error in /edit_submission command: {e}")

    @commands.slash_command(
        name="delete_submission",
        description="Delete a previous submission and correct the user's points.",
    )
    async def delete_submission(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str, "The season the submission is in.", autocomplete=search_seasons
        ),
        user: discord.Option(
            str,
            "The user whose submission you are deleting.",
            autocomplete=search_registered_users,
        ),
        submission: discord.Option(
            str,
            "The specific submission to delete.",
            autocomplete=search_user_submissions,
        ),
    ):
        """(Admin-Only) Deletes a submission and subtracts its points."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_submission_id = int(submission)

            if target_submission_id == 0:
                await ctx.respond(
                    "❌ Invalid submission selected. Please ensure you select a valid submission from the list.",
                    ephemeral=True,
                )
                return

            target_user_id = int(user)
            target_season_id = int(season)
            submissions = await self.api_client.get_submissions(
                auth=auth, user_id=target_user_id, season_id=target_season_id
            )
            sub_to_delete = next(
                (s for s in submissions if s["id"] == target_submission_id), None
            )

            if not sub_to_delete:
                await ctx.respond(
                    "❌ Could not find the specified submission to delete.",
                    ephemeral=True,
                )
                return

            await self.api_client.delete_submission(
                auth=auth,
                submission_id=target_submission_id,
            )

            user_ign = sub_to_delete["user"]["in_game_name"]
            item_name = sub_to_delete["season_item"]["item"]["name"]
            quantity = sub_to_delete["quantity"]
            points = sub_to_delete["total_point_value"]

            success_message = (
                f"✅ Submission deleted successfully!\n\n"
                f"The submission of **{quantity}x {item_name}** for **{user_ign}** has been removed. "
                f"**{points}** points have been subtracted from their total."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"🗑️ {ctx.author.mention} deleted a submission for **{user_ign}** (-{points} points)."
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
            print(f"An unexpected error in /delete_submission command: {e}")

    @commands.slash_command(
        name="get_submissions",
        description="View submissions for a season, optionally filtered by user.",
    )
    async def get_submissions(
        self,
        ctx: discord.ApplicationContext,
        season: discord.Option(
            str, "The season to view submissions for.", autocomplete=search_seasons
        ),
        user: discord.Option(
            str,
            "Optional: Filter submissions for a specific user.",
            autocomplete=search_registered_users,
            required=False,
        ),
    ):
        """(Registered Users) Fetches and displays submissions."""
        await ctx.defer(ephemeral=True)

        try:
            auth = BotAuth(api_key=self.bot_api_key, user_discord_id=ctx.author.id)
            target_season_id = int(season)
            target_user_id = int(user) if user else None

            submission_list = await self.api_client.get_submissions(
                auth=auth, season_id=target_season_id, user_id=target_user_id
            )

            if not submission_list:
                await ctx.respond(
                    "No submissions found matching your criteria.", ephemeral=True
                )
                return

            # Dynamically create the title
            title_season_name = submission_list[0]["season_item"]["season"]["name"]
            title = f"Submissions for {title_season_name}"
            if target_user_id:
                title = f"Submissions by {submission_list[0]['user']['in_game_name']} in {title_season_name}"

            sub_pages = []
            page_content = ""
            for i, sub in enumerate(submission_list, 1):
                user_name = sub["user"]["in_game_name"]
                item_name = sub["season_item"]["item"]["name"]
                created_dt = datetime.fromisoformat(
                    sub["created_at"].replace("Z", "+00:00")
                )
                created_timestamp = int(created_dt.timestamp())

                page_content += (
                    f"**{sub['quantity']}x {item_name}** for **{user_name}** "
                    f"({sub['total_point_value']} pts) - <t:{created_timestamp}:R>\n"
                )

                creator_name = sub.get("creator", {}).get("in_game_name", "Unknown")
                updater_name = sub.get("updater", {}).get("in_game_name", "Unknown")

                page_content += f"  *Added by: {creator_name}*\n"

                if creator_name != updater_name:
                    page_content += f"  *Last updated by: {updater_name}*\n"

                page_content += "\n"

                if i % 5 == 0 and i != len(submission_list):
                    embed = discord.Embed(
                        title=title,
                        description=page_content,
                        color=discord.Color.dark_green(),
                    )
                    sub_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title=title,
                    description=page_content,
                    color=discord.Color.dark_green(),
                )
                sub_pages.append(embed)

            paginator = pages.Paginator(
                pages=sub_pages, disable_on_timeout=True, timeout=120
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
            print(f"An unexpected error in /get_submissions command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(
        SubmissionCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key)
    )
