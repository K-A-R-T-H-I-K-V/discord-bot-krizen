import discord
import os
import asyncio
from discord.ext import commands
from dotenv import load_dotenv
from keep_alive import keep_alive

# Load environment variables
load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")
# Add under the intents setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
intents.guilds = True  # Add this line
intents.guild_messages = True  # Add this line

bot = commands.Bot(
    command_prefix="!",
    intents=intents,
    #help_command=None  # Disable default help command
)

# Add this error handler
@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound):
        return
    await ctx.send(f"❌ Error: {str(error)}")

# Add this before main()
@bot.event
async def on_guild_join(guild):
    await bot.tree.sync(guild=guild)

@bot.event
async def on_ready():
    print(f"✅ Logged in as {bot.user} ({bot.user.id})")
    await load_cogs()
    await bot.tree.sync()  # Sync slash commands
    print("✅ Slash commands synced!")

@bot.command()
@commands.is_owner()
async def sync(ctx):
    await bot.tree.sync()
    await ctx.send("✅ Commands synced!")

async def load_cogs():
    cogs = [
        "cogs.moderation",
        "cogs.chat_commands",
        "cogs.roles",
        "cogs.events",
        "cogs.welcome_farewell",
        "cogs.ai_powered_moderation",
        "cogs.ticketsystem"
    ]
    
    for cog in cogs:
        try:
            await bot.load_extension(cog)
            print(f"✅ Loaded cog: {cog}")
        except Exception as e:
            print(f"❌ Error loading {cog}: {e}")

async def main():
    async with bot:
        await bot.start(TOKEN)

if __name__ == "__main__":
    keep_alive()
    asyncio.run(main())
