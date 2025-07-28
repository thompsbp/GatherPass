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
                print("HERE")
                lodestone_link = (
                    f"{self.bot.lodestone_base_url}{new_user['lodestone_id']}"
                )

                print("HERE2")
                log_message = (
                    f"@here New User Registration:\n\n"
                    f"**User:** {ctx.author.mention}\n"
                    f"**In-Game Name:** {new_user['in_game_name']}\n"
                    f"**Lodestone:** <{lodestone_link}>\n\n"
                    f"This user is awaiting verification."
                )
                print("HERE3")
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


def setup(bot: discord.Bot):
    bot.add_cog(UserCog(bot, bot.api_client, bot.admin_channel_id, bot.bot_api_key))
