import discord
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

# Create bot instance
intents = discord.Intents.default()
bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'✅ {bot.user} is now running!')

@bot.command()
async def ping(ctx):
    await ctx.respond("Pong! 🏓")

# Run bot
bot.run(TOKEN)

