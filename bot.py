import discord
import os
from discord.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Enable all intents
intents = discord.Intents.default()
intents.messages = True
intents.guilds = True
intents.members = True
intents.messages = True  # Allows bot to read messages
intents.message_content = True  # Required to read the content of messages

# Use commands.Bot instead of discord.Client
bot = commands.Bot(command_prefix="!", intents=intents)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user}")

# Load cogs
async def load_cogs():
    await bot.load_extension("cogs.chat_commands")
    await bot.load_extension("cogs.moderation")
    await bot.load_extension("cogs.roles")
    await bot.load_extension("cogs.events")

# Run the bot
async def main():
    async with bot:
        await load_cogs()
        await bot.start(TOKEN)

import asyncio
asyncio.run(main())



