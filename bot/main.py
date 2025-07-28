# ==============================================================================
# FILE: bot/main.py
# ==============================================================================
# This file is the main entry point for the bot. It handles setup,
# loading extensions (cogs), and connecting to Discord.

import os

import discord
from dotenv import load_dotenv
from gatherpass_client import APIClient

# --- Load Environment Variables ---
load_dotenv()

DISCORD_BOT_TOKEN = os.getenv("DISCORD_BOT_TOKEN")
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))
API_URL = os.getenv("API_URL")
BOT_API_KEY = os.getenv("BOT_API_KEY")
LODESTONE_BASE_URL = "https://na.finalfantasyxiv.com/lodestone/"

# --- Bot Setup ---
intents = discord.Intents.default()
intents.members = True
bot = discord.Bot(intents=intents)

# --- Attach Helper Clients to the Bot ---
bot.api_client = APIClient(base_url=API_URL)
bot.admin_channel_id = ADMIN_CHANNEL_ID
bot.bot_api_key = BOT_API_KEY
bot.lodestone_base_url = LODESTONE_BASE_URL


# --- Bot Events ---
@bot.event
async def on_ready():
    """Called once the bot has successfully connected to Discord."""
    print(f"✅ Bot is ready and logged in as {bot.user}")

    admin_channel = bot.get_channel(ADMIN_CHANNEL_ID)

    if admin_channel:
        await admin_channel.send("Bot is online and ready for commands.")
    else:
        print(f"⚠️ Could not find admin channel with ID: {ADMIN_CHANNEL_ID}")


# -- Load Cogs ---
for filename in os.listdir("./cogs"):
    if filename.endswith(".py"):
        bot.load_extension(f"cogs.{filename[:-3]}")
        print(f"🔩 Loaded Cog: {filename}")


# --- Run the Bot ---
if __name__ == "__main__":
    if not DISCORD_BOT_TOKEN:
        print("❌ ERROR: DISCORD_BOT_TOKEN is not set in the environment.")
    else:
        bot.run(DISCORD_BOT_TOKEN)
