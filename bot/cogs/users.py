import discord
import httpx
from discord.ext import commands, pages
from gatherpass_client import APIClient
from gatherpass_client.auth import BotAuth, BotOnlyAuth


# This class inherits from commands.Cog
class UserCog(commands.Cog):
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

    @commands.slash_command(name="users", description="List all registered users.")
    async def users(self, ctx: discord.ApplicationContext):
        """(Admin-Only) Fetches the user list from the API and displays it."""
        await ctx.defer(ephemeral=True)

        try:
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )
            user_list = await self.api_client.get_users(auth=auth_provider)

            if not user_list:
                await ctx.respond("No users are registered yet.", ephemeral=True)
                return

            user_pages = []
            page_content = ""
            for i, user in enumerate(user_list, 1):
                page_content += (
                    f"**{user['in_game_name']}**\n"
                    f"Status: `{user['status']}` | Admin: `{user['admin']}`\n\n"
                )
                if i % 5 == 0 and i != len(user_list):
                    embed = discord.Embed(
                        title="Registered Users", description=page_content
                    )
                    user_pages.append(embed)
                    page_content = ""

            if page_content:
                embed = discord.Embed(
                    title="Registered Users", description=page_content
                )
                user_pages.append(embed)

            paginator = pages.Paginator(
                pages=user_pages, disable_on_timeout=True, timeout=60
            )
            await paginator.respond(ctx.interaction, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"✅ {ctx.author.mention} used the `/users` command."
                )

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"⚠️ {ctx.author.mention} failed to use the `/users` command. Reason: {error_message}"
                )
        except Exception as e:
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred.", ephemeral=True
            )
            print(f"An unexpected error occurred in /users command: {e}")

    @commands.slash_command(
        name="register",
        description="Register for the Gather Pass event.",
    )
    async def register(
        self,
        ctx: discord.ApplicationContext,
        in_game_name: discord.Option(str, "Your full in-game character name."),
        lodestone_id: discord.Option(str, "The ID from your Lodestone URL."),
    ):
        """Handles the user registration process."""
        await ctx.defer(ephemeral=True)

        try:
            auth_provider = BotOnlyAuth(api_key=self.bot_api_key)
            new_user = await self.api_client.create_user(
                auth=auth_provider,
                discord_id=ctx.author.id,
                in_game_name=in_game_name,
                lodestone_id=lodestone_id,
            )

            success_message = (
                f"🎉 Welcome, **{new_user['in_game_name']}**! You have successfully registered.\n\n"
                f"An admin has been notified and will verify your account shortly. "
                f"You will not be able to participate until your account is verified."
            )
            await ctx.respond(success_message, ephemeral=True)

            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                lodestone_link = (
                    f"{self.bot.lodestone_base_url}character/{new_user['lodestone_id']}"
                )

                log_message = (
                    f"@here New User Registration:\n\n"
                    f"**User:** {ctx.author.mention}\n"
                    f"**In-Game Name:** {new_user['in_game_name']}\n"
                    f"**Lodestone:** <{lodestone_link}>\n\n"
                    f"This user is awaiting verification."
                )
                await admin_channel.send(log_message)

        except httpx.HTTPStatusError as e:
            error_message = e.response.json().get(
                "detail", "An unknown API error occurred."
            )
            await ctx.respond(f"❌ **Error:** {error_message}", ephemeral=True)
        except Exception as e:
            print(e)
            await ctx.respond(
                "❌ **Error:** An unexpected error occurred while trying to register.",
                ephemeral=True,
            )
            print(f"An unexpected error occurred in /register command: {e}")

    async def search_users(self, ctx: discord.AutocompleteContext):
        """
        This is the autocomplete function. It gets called as the admin types in
        the 'user' option of the /verify command.
        """
        # Get what the user has typed so far
        query = ctx.value

        # Don't hit the API if the query is empty
        if not query:
            return []

        try:
            # Create an auth provider for the user running the command
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.interaction.user.id
            )

            # Call the API to get a list of matching users
            user_list = await self.api_client.get_users(
                auth=auth_provider, name_query=query
            )

            # Format the results for Discord's autocomplete list.
            # We display the name, but the value that gets sent is the user's ID.
            return [
                discord.OptionChoice(
                    name=user["in_game_name"], value=str(user["discord_id"])
                )
                for user in user_list
            ]
        except Exception:
            # If the API call fails for any reason, return an empty list
            return []

    @commands.slash_command(
        name="verify", description="Verify a newly registered user."
    )
    async def verify(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(
            str,
            "The user to verify (start typing their in-game name).",
            autocomplete=search_users,
        ),
    ):
        """
        (Admin-Only) Verifies a user, changing their status from 'pending' to 'verified'.
        """
        await ctx.defer(ephemeral=True)

        try:
            # The 'user' variable is the discord_id string from the autocomplete choice.
            # We need to find the user's internal API ID to make the update call.
            target_discord_id = int(user)
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )

            # This is a bit inefficient, but we need to get the full user list
            # to find the internal ID corresponding to the discord ID.
            user_list = await self.api_client.get_users(auth=auth_provider)
            target_user = next(
                (u for u in user_list if u["discord_id"] == target_discord_id), None
            )

            if not target_user:
                await ctx.respond(
                    f"❌ Could not find a user with the Discord ID `{target_discord_id}`.",
                    ephemeral=True,
                )
                return

            if target_user["status"] == "verified":
                await ctx.respond(
                    f"☑️ User **{target_user['in_game_name']}** is already verified.",
                    ephemeral=True,
                )
                return

            # Now, call the update method using the user's internal ID
            updated_user = await self.api_client.update_user(
                auth=auth_provider, user_id=target_user["id"], status="verified"
            )

            success_message = f"✅ User **{updated_user['in_game_name']}** has been successfully verified!"
            await ctx.respond(success_message, ephemeral=True)

            # Log the action to the admin channel
            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"👍 {ctx.author.mention} verified the user **{updated_user['in_game_name']}**."
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
            print(f"An unexpected error in /verify command: {e}")

    @commands.slash_command(
        name="promote_admin", description="Promote a verified user to admin."
    )
    async def promote_admin(
        self,
        ctx: discord.ApplicationContext,
        user: discord.Option(
            str,
            "The user to promote (start typing their in-game name).",
            autocomplete=search_users,  # We reuse the same autocomplete function
        ),
    ):
        """
        (Admin-Only) Promotes a user, giving them admin privileges.
        """
        await ctx.defer(ephemeral=True)

        try:
            target_discord_id = int(user)
            auth_provider = BotAuth(
                api_key=self.bot_api_key, user_discord_id=ctx.author.id
            )

            # Find the target user in the database to get their internal ID
            user_list = await self.api_client.get_users(auth=auth_provider)
            target_user = next(
                (u for u in user_list if u["discord_id"] == target_discord_id), None
            )

            if not target_user:
                await ctx.respond(
                    f"❌ Could not find a user with the Discord ID `{target_discord_id}`.",
                    ephemeral=True,
                )
                return

            if target_user["status"] != "verified":
                await ctx.respond(
                    f"⚠️ User **{target_user['in_game_name']}** must be verified before they can be promoted.",
                    ephemeral=True,
                )
                return

            if target_user["admin"] is True:
                await ctx.respond(
                    f"☑️ User **{target_user['in_game_name']}** is already an admin.",
                    ephemeral=True,
                )
                return

            # Call the update method using the user's internal API ID
            updated_user = await self.api_client.update_user(
                auth=auth_provider, user_id=target_user["id"], is_admin=True
            )

            success_message = f"✅ User **{updated_user['in_game_name']}** has been successfully promoted to admin!"
            await ctx.respond(success_message, ephemeral=True)

            # Log the action to the admin channel
            admin_channel = self.bot.get_channel(self.admin_channel_id)
            if admin_channel:
                await admin_channel.send(
                    f"👑 {ctx.author.mention} promoted **{updated_user['in_game_name']}** to admin."
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
            print(f"An unexpected error in /promote_admin command: {e}")


def setup(bot: discord.Bot):
    bot.add_cog(UserCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key))
