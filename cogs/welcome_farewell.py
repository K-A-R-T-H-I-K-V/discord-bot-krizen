import discord 
from discord.ext import commands
import json
import os
import random
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io  # Import io for BytesIO

class WelcomeFarewell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "logs/welcome_farewell_config.json"
        self.config = self.load_config()
        self.welcome_images = [
            "https://some-welcome-gif1.gif",
            "https://some-welcome-gif2.gif",
            "https://some-welcome-gif3.gif"
        ]
        self.farewell_images = [
            "https://some-goodbye-gif1.gif",
            "https://some-goodbye-gif2.gif",
            "https://some-goodbye-gif3.gif"
        ]

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    async def create_locked_channel(self, guild, name):
        existing_channel = discord.utils.get(guild.text_channels, name=name)
        if existing_channel:
            return existing_channel
        overwrites = {
            guild.default_role: discord.PermissionOverwrite(view_channel=True, send_messages=False),
            guild.me: discord.PermissionOverwrite(send_messages=True)
        }
        channel = await guild.create_text_channel(name, overwrites=overwrites)
        return channel

    async def create_welcome_image(self, member, background_url):
        async with aiohttp.ClientSession() as session:
            async with session.get(background_url) as resp:
                if resp.status == 200:
                    bg_bytes = await resp.read()
                else:
                    return None  # Return None if image fails to load
            
            async with session.get(str(member.display_avatar.url)) as resp:
                if resp.status == 200:
                    pfp_bytes = await resp.read()
                else:
                    return None
        
        bg = Image.open(io.BytesIO(bg_bytes)).convert("RGBA")
        pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((150, 150))
        
        # Create circular mask
        mask = Image.new("L", (150, 150), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, 150, 150), fill=255)
        pfp.putalpha(mask)
        
        # Paste PFP on background
        bg.paste(pfp, (200, 50), pfp)
        draw = ImageDraw.Draw(bg)

        # Use a default font
        try:
            font = ImageFont.truetype("arial.ttf", 40)
        except IOError:
            font = ImageFont.load_default()

        draw.text((180, 220), member.name, (255, 255, 255), font=font)
        output = io.BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return output

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return
        if "welcome_channel" not in self.config[guild_id]:
            channel = await self.create_locked_channel(member.guild, "welcome")
            self.config[guild_id]["welcome_channel"] = channel.id
            self.save_config()
        else:
            channel = self.bot.get_channel(self.config[guild_id]["welcome_channel"])
        
        if not channel:
            return

        message = self.config[guild_id].get("welcome_message", "Welcome, {user}! Enjoy your stay!").replace("{user}", member.mention)
        animation = random.choice(self.welcome_images)
        image = await self.create_welcome_image(member, animation)

        if image:
            file = discord.File(image, filename="welcome.png")
            embed = discord.Embed(description=message, color=discord.Color.blue())
            embed.set_image(url="attachment://welcome.png")
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(message)

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config:
            return
        if "farewell_channel" not in self.config[guild_id]:
            channel = await self.create_locked_channel(member.guild, "farewell")
            self.config[guild_id]["farewell_channel"] = channel.id
            self.save_config()
        else:
            channel = self.bot.get_channel(self.config[guild_id]["farewell_channel"])
        
        if not channel:
            return

        message = self.config[guild_id].get("farewell_message", "Goodbye, {user}! We'll miss you!").replace("{user}", member.mention)
        animation = random.choice(self.farewell_images)
        image = await self.create_welcome_image(member, animation)

        if image:
            file = discord.File(image, filename="farewell.png")
            embed = discord.Embed(description=message, color=discord.Color.red())
            embed.set_image(url="attachment://farewell.png")
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(message)

    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, *, message: str):
        guild_id = str(ctx.guild.id)
        channel = await self.create_locked_channel(ctx.guild, "welcome")
        self.config.setdefault(guild_id, {})["welcome_channel"] = channel.id
        self.config[guild_id]["welcome_message"] = message
        self.save_config()
        await ctx.send(f"✅ Welcome message set for **#{channel.name}**:\n{message}")

    @commands.command(name="setfarewell")
    @commands.has_permissions(administrator=True)
    async def set_farewell(self, ctx, *, message: str):
        guild_id = str(ctx.guild.id)
        channel = await self.create_locked_channel(ctx.guild, "farewell")
        self.config.setdefault(guild_id, {})["farewell_channel"] = channel.id
        self.config[guild_id]["farewell_message"] = message
        self.save_config()
        await ctx.send(f"✅ Farewell message set for **#{channel.name}**:\n{message}")

async def setup(bot):
    await bot.add_cog(WelcomeFarewell(bot))