import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable necessary intents
intents = discord.Intents.default()
intents.guilds = True
intents.members = True
intents.messages = True
intents.message_content = True  # Required for reading messages

# Use commands.Bot
bot = commands.Bot(command_prefix="!", intents=intents)

# ✅ Event: Bot Ready
@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")

    # Load cogs
    await load_cogs()

# ✅ Function: Load Cogs
async def load_cogs():
    cogs = ["cogs.moderation", "cogs.chat_commands", "cogs.roles", "cogs.events"]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)  # Ensure all cogs are loaded
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Error loading {cog}: {e}")

# ✅ Run the Bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())
