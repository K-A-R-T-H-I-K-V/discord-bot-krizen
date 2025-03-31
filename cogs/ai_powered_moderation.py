import discord
from discord.ext import commands
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import logging

# ✅ Configure Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Load pretrained model
MODEL_NAME = "unitary/unbiased-toxic-roberta"
tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
model = AutoModelForSequenceClassification.from_pretrained(MODEL_NAME)

# ✅ Dictionary to track warnings and moderation status
user_warnings = {}
mod_enabled = {}  # Track AI moderation status per server

class AI_Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.mod_log_channel = None  # Store log channel

    async def ensure_mod_log_channel(self, guild):
        """Ensures a mod-log channel exists and only admins can view it."""
        logger.info(f"Checking for mod-log channel in {guild.name}")
        existing_channel = discord.utils.get(guild.text_channels, name="mod-logs")
        
        if existing_channel:
            self.mod_log_channel = existing_channel
            logger.info("Existing mod-logs channel found.")
        else:
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(view_channel=False),  # Hide from everyone
                guild.me: discord.PermissionOverwrite(view_channel=True, send_messages=True),  # Bot can access
            }

            # Allow admins to view
            for role in guild.roles:
                if role.permissions.administrator:
                    overwrites[role] = discord.PermissionOverwrite(view_channel=True, send_messages=True)

            self.mod_log_channel = await guild.create_text_channel("mod-logs", overwrites=overwrites)
            logger.info(f"✅ Created 'mod-logs' channel in {guild.name}")

    def is_toxic(self, text):
        logger.info(f"Analyzing message: {text}")
        inputs = tokenizer(text, return_tensors="pt", truncation=True, padding=True)
        with torch.no_grad():
            outputs = model(**inputs)
        scores = torch.nn.functional.softmax(outputs.logits, dim=1)
        toxicity_score = scores[0][1].item()
        logger.info(f"Toxicity score: {toxicity_score}")
        return toxicity_score > 0.6  # Set threshold

    async def log_message(self, message, reason):
        """Logs flagged messages to the mod-logs channel."""
        if self.mod_log_channel:
            embed = discord.Embed(
                title="🚨 Moderation Alert",
                description=f"**User:** {message.author.mention}\n**Message:** {message.content}\n**Reason:** {reason}",
                color=discord.Color.red()
            )
            await self.mod_log_channel.send(embed=embed)
            logger.info(f"Logged message from {message.author.name}: {message.content}")

    async def warn_user(self, message):
        """Issues a warning to a user and logs it."""
        user_id = message.author.id
        user_warnings[user_id] = user_warnings.get(user_id, 0) + 1
        warnings = user_warnings[user_id]

        if warnings < 3:
            await message.channel.send(f"⚠️ {message.author.mention}, this is warning {warnings}/3 for toxic behavior.")
        elif warnings == 3:
            await message.author.timeout(duration=600)  # 10-minute timeout
            await message.channel.send(f"⏳ {message.author.mention} has been muted for 10 minutes due to repeated offenses.")
        elif warnings >= 4:
            await message.author.ban(reason="Repeated toxic behavior")
            await message.channel.send(f"🚫 {message.author.mention} has been banned for repeated violations.")
        logger.info(f"{message.author.name} has received {warnings} warnings.")

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot:
            return  # Ignore bot messages

        guild_id = message.guild.id
        if not mod_enabled.get(guild_id, True):
            return  # Ignore if AI moderation is disabled

        logger.info(f"Message received from {message.author.name}: {message.content}")
        
        if self.is_toxic(message.content):
            await message.delete()
            await self.warn_user(message)
            await self.log_message(message, "Toxic Message")

    @commands.command(name="toggle_ai_moderation")
    @commands.has_permissions(administrator=True)
    async def toggle_ai_moderation(self, ctx):
        """Command to toggle AI moderation on or off."""
        guild_id = ctx.guild.id
        mod_enabled[guild_id] = not mod_enabled.get(guild_id, True)
        status = "enabled" if mod_enabled[guild_id] else "disabled"
        await ctx.send(f"🛠️ AI moderation has been **{status}**.")
        logger.info(f"AI moderation {status} in {ctx.guild.name}")

    @commands.Cog.listener()
    async def on_ready(self):
        """Ensure mod-logs channel is created when the bot starts."""
        logger.info("Bot is ready. Checking mod-log channels...")
        for guild in self.bot.guilds:
            await self.ensure_mod_log_channel(guild)

    @commands.Cog.listener()
    async def on_guild_join(self, guild):
        """Create mod-logs channel when bot joins a new server."""
        logger.info(f"Joined new server: {guild.name}")
        await self.ensure_mod_log_channel(guild)

async def setup(bot):
    await bot.add_cog(AI_Moderation(bot))
