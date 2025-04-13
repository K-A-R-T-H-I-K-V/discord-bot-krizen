# LOGS
# import discord
# from discord.ext import commands
# import json
# import os
# import random
# from PIL import Image, ImageDraw, ImageFont
# import aiohttp
# import io
# import logging

# # Set up logging
# logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
# logger = logging.getLogger(__name__)

# class WelcomeFarewell(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.config_file = "logs/welcome_farewell_config.json"
#         self.config = self.load_config()
#         self.welcome_images = [
#             "assets/greeting/welcome1.jpg",
#             "assets/greeting/welcome2.jpg",
#             "assets/greeting/welcome3.jpg",
#         ]
#         self.farewell_gifs = ["assets/greeting/goodbye.gif"]

#     def load_config(self):
#         if os.path.exists(self.config_file):
#             with open(self.config_file, "r") as f:
#                 return json.load(f)
#         return {}

#     def save_config(self):
#         with open(self.config_file, "w") as f:
#             json.dump(self.config, f, indent=4)

#     async def create_welcome_image(self, member):
#         try:
#             background_path = random.choice(self.welcome_images)
#             if not os.path.exists(background_path):
#                 logger.error(f"Background image '{background_path}' not found.")
#                 return None

#             logger.info(f"Using background image: {background_path}")

#             # Load Background
#             bg = Image.open(background_path).convert("RGBA")
#             width, height = bg.size

#             # Profile Picture (PFP)
#             pfp_size = int(height * 0.35)
#             pfp_position = ((width - pfp_size) // 2, int(height * 0.05))

#             # Load User Avatar
#             async with aiohttp.ClientSession() as session:
#                 async with session.get(str(member.display_avatar.url)) as resp:
#                     if resp.status == 200:
#                         pfp_bytes = await resp.read()
#                     else:
#                         logger.error(f"Failed to fetch profile picture for {member.name}")
#                         return None

#             pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((pfp_size, pfp_size))

#             # Circular Mask
#             mask = Image.new("L", (pfp_size, pfp_size), 0)
#             draw = ImageDraw.Draw(mask)
#             draw.ellipse((0, 0, pfp_size, pfp_size), fill=255)
#             pfp.putalpha(mask)

#             # Paste PFP
#             bg.paste(pfp, pfp_position, pfp)

#             # Drawing Text
#             draw = ImageDraw.Draw(bg)
#             try:
#                 font_path = "assets/fonts/stylish.ttf"
#                 welcome_font = ImageFont.truetype(font_path, int(height * 0.08))
#                 user_font = ImageFont.truetype(font_path, int(height * 0.05))
#                 count_font = ImageFont.truetype(font_path, int(height * 0.045))
#             except IOError:
#                 logger.warning("Font file not found. Using default font.")
#                 welcome_font = user_font = count_font = ImageFont.load_default()

#             # Welcome Text
#             welcome_text = "WELCOME"
#             text_w = draw.textbbox((0, 0), welcome_text, font=welcome_font)[2]
#             draw.text(((width - text_w) // 2, pfp_position[1] + pfp_size + 30), welcome_text, (255, 255, 255), font=welcome_font)

#             # Username
#             user_text = f"{member.name}#{member.discriminator}"
#             user_w = draw.textbbox((0, 0), user_text, font=user_font)[2]
#             draw.text(((width - user_w) // 2, pfp_position[1] + pfp_size + 90), user_text, (255, 255, 255), font=user_font)

#             # Member Count
#             count_text = f"YOU'RE OUR {member.guild.member_count}TH MEMBER"
#             count_w = draw.textbbox((0, 0), count_text, font=count_font)[2]
#             draw.text(((width - count_w) // 2, pfp_position[1] + pfp_size + 150), count_text, (255, 255, 255), font=count_font)

#             # Save Image
#             output = io.BytesIO()
#             bg.save(output, format="PNG")
#             output.seek(0)

#             logger.info(f"Successfully generated welcome image for {member.name}")
#             return output
#         except Exception as e:
#             logger.error(f"Error generating welcome image: {e}")
#             return None

#     @commands.Cog.listener()
#     async def on_member_join(self, member):
#         logger.info(f"New member joined: {member.name}")

#         channel_id = self.config.get(str(member.guild.id), {}).get("welcome_channel")
#         if not channel_id:
#             logger.warning("No welcome channel configured.")
#             return

#         channel = self.bot.get_channel(channel_id)
#         if not channel:
#             logger.warning("Invalid welcome channel.")
#             return

#         welcome_image = await self.create_welcome_image(member)
#         if welcome_image:
#             file = discord.File(welcome_image, filename="welcome.png")

#             embed = discord.Embed(
#                 title="🎉 Welcome to the Server!",
#                 description=f"Hey {member.mention}, we're glad to have you here!",
#                 color=discord.Color.green()
#             )
#             embed.set_image(url="attachment://welcome.png")  # Embed the image
#             embed.set_footer(text=f"Member #{member.guild.member_count}")

#             await channel.send(embed=embed, file=file)
#         else:
#             await channel.send(content=f"Welcome {member.mention}! 🚀")

#     @commands.Cog.listener()
#     async def on_member_remove(self, member):
#         logger.info(f"Member left: {member.name}")

#         channel_id = self.config.get(str(member.guild.id), {}).get("farewell_channel")
#         if not channel_id:
#             logger.warning("No farewell channel configured.")
#             return

#         channel = self.bot.get_channel(channel_id)
#         if not channel:
#             logger.warning("Invalid farewell channel.")
#             return

#         farewell_gif = random.choice(self.farewell_gifs)
#         if os.path.exists(farewell_gif):
#             file = discord.File(farewell_gif, filename="farewell.gif")

#             embed = discord.Embed(
#                 title="😢 Goodbye!",
#                 description=f"Goodbye {member.mention}! We'll miss you.",
#                 color=discord.Color.red()
#             )
#             embed.set_image(url="attachment://farewell.gif")

#             await channel.send(embed=embed, file=file)
#         else:
#             await channel.send(content=f"Goodbye {member.mention}! We'll miss you. 😢")

# # ✅ Fixed setup function
# async def setup(bot):
#     await bot.add_cog(WelcomeFarewell(bot))


import discord
from discord.ext import commands
import json
import os
import random
import logging
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io
import asyncio

logger = logging.getLogger(__name__)

class WelcomeFarewell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "logs/welcome_farewell_config.json"
        self.config = self.load_config()
        self.welcome_images = self._validate_assets("assets/greeting/welcome", [".jpg", ".png"])
        self.farewell_gifs = self._validate_assets("assets/greeting/goodbye", [".gif"])
        
        # Font configuration (keep your original font settings)
        self.font_paths = [
            "assets/fonts/Quebab-Shadow-ffp.ttf",
            "assets/fonts/Milkyway Free.ttf",
            "assets/fonts/StreetLookRegular.ttf",
            "assets/fonts/Creator's Collection Demo.ttf",
            "assets/fonts/Frostrex.ttf"
        ]

    def _validate_assets(self, directory, extensions):
        try:
            return [os.path.join(directory, f) for f in os.listdir(directory) 
                   if any(f.lower().endswith(ext) for ext in extensions)]
        except FileNotFoundError:
            logger.error(f"Asset directory not found: {directory}")
            return []

    def load_config(self):
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, "r") as f:
                    return json.load(f)
            return {}
        except Exception as e:
            logger.error(f"Config error: {str(e)}")
            return {}

    def save_config(self):
        try:
            with open(self.config_file, "w") as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            logger.error(f"Config save error: {str(e)}")

    async def create_welcome_image(self, member):
        """Maintain original image composition with improved error handling"""
        try:
            if not self.welcome_images:
                return None

            # Original background selection
            bg_path = random.choice(self.welcome_images)
            bg = Image.open(bg_path).convert("RGBA")

            # Original avatar sizing calculations
            pfp_size = int(bg.height * 0.45)
            pfp_position = ((bg.width - pfp_size) // 2, int(bg.height * 0.10))

            # Fetch avatar with retry logic
            async with aiohttp.ClientSession() as session:
                for attempt in range(3):
                    try:
                        async with session.get(str(member.display_avatar.url)) as resp:
                            if resp.status == 200:
                                pfp_bytes = await resp.read()
                                break
                    except Exception:
                        if attempt == 2: return None
                        await asyncio.sleep(1)
                else:
                    return None

            # Original avatar processing
            pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((pfp_size, pfp_size))
            mask = Image.new("L", (pfp_size, pfp_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse((0, 0, pfp_size, pfp_size), fill=255)
            pfp.putalpha(mask)

            # Original border implementation
            border_thickness = int(pfp_size * 0.08)
            border_size = pfp_size + (border_thickness * 2)
            border_img = Image.new("RGBA", (border_size, border_size), (255, 255, 255, 0))
            border_draw = ImageDraw.Draw(border_img)
            border_draw.ellipse(
                (border_thickness // 2, border_thickness // 2, 
                 border_size - border_thickness // 2, border_size - border_thickness // 2),
                outline=(255, 255, 255, 255),
                width=border_thickness
            )

            # Original positioning
            border_img.paste(pfp, (border_thickness, border_thickness), pfp)
            bg.paste(border_img, (pfp_position[0] - border_thickness, pfp_position[1] - border_thickness), border_img)

            # Text handling with original positioning
            draw = ImageDraw.Draw(bg)
            text_y = pfp_position[1] + pfp_size + 30
            
            # Original font loading
            font_size = int(pfp_size * 0.30)
            try:
                font = ImageFont.truetype(self.font_paths[0], font_size)
            except IOError:
                font = ImageFont.load_default()

            # Original text positioning
            username = member.name
            text_width = draw.textlength(username, font=font)
            text_x = (bg.width - text_width) // 2
            draw.text((text_x, text_y), username, (255, 255, 255), font=font)

            # Member position text (original implementation)
            join_position = member.guild.member_count
            position_text = f"🎉 You are the {join_position}{'st' if join_position % 10 == 1 and join_position != 11 else 'nd' if join_position % 10 == 2 and join_position != 12 else 'rd' if join_position % 10 == 3 and join_position != 13 else 'th'} member!"
            
            position_font_size = int(pfp_size * 0.18)
            try:
                position_font = ImageFont.truetype(self.font_paths[0], position_font_size)
            except IOError:
                position_font = ImageFont.load_default()

            position_width = draw.textlength(position_text, font=position_font)
            position_x = (bg.width - position_width) // 2
            position_y = text_y + int(pfp_size * 0.35)
            draw.text((position_x, position_y), position_text, (255, 255, 255), font=position_font)

            # Save to bytes
            output = io.BytesIO()
            bg.save(output, format="PNG")
            output.seek(0)
            return output

        except Exception as e:
            logger.error(f"Image error: {str(e)}")
            return None

    async def _send_safe(self, channel, content=None, embed=None, file=None):
        """Improved sending with error handling"""
        for attempt in range(3):
            try:
                return await channel.send(content=content, embed=embed, file=file)
            except Exception as e:
                if attempt == 2:
                    logger.error(f"Failed to send message: {str(e)}")
                await asyncio.sleep(1)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if not self.config.get(guild_id, {}).get("welcome_channel"):
            return

        channel = self.bot.get_channel(self.config[guild_id]["welcome_channel"])
        if not channel:
            return

        try:
            message = self.config[guild_id].get("welcome_message", "Welcome, {user}! 🎉").replace("{user}", member.mention)
            image = await self.create_welcome_image(member)
            
            if image:
                file = discord.File(image, filename="welcome.png")
                embed = discord.Embed(description=message, color=discord.Color.blue())
                embed.set_image(url="attachment://welcome.png")
                await self._send_safe(channel, embed=embed, file=file)
            else:
                await self._send_safe(channel, message)
        except Exception as e:
            logger.error(f"Join error: {str(e)}")

    @commands.Cog.listener()
    async def on_member_remove(self, member):
        guild_id = str(member.guild.id)
        if not self.config.get(guild_id, {}).get("farewell_channel"):
            return

        channel = self.bot.get_channel(self.config[guild_id]["farewell_channel"])
        if not channel:
            return

        try:
            message = self.config[guild_id].get("farewell_message", "Goodbye, {user}! 😢").replace("{user}", member.mention)
            message += f"\n👥 Members left: **{member.guild.member_count}**"

            if self.farewell_gifs:
                gif_path = random.choice(self.farewell_gifs)
                try:
                    with open(gif_path, "rb") as f:
                        file = discord.File(f, filename="farewell.gif")
                        embed = discord.Embed(description=message, color=discord.Color.red())
                        embed.set_image(url="attachment://farewell.gif")
                        await self._send_safe(channel, embed=embed, file=file)
                        return
                except Exception as e:
                    logger.error(f"GIF error: {str(e)}")

            await self._send_safe(channel, message)
        except Exception as e:
            logger.error(f"Leave error: {str(e)}")

    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, *, message: str):
        """Original command logic with validation"""
        if len(message) > 1000:
            return await ctx.send("❌ Message too long (max 1000 chars)")
            
        guild_id = str(ctx.guild.id)
        self.config.setdefault(guild_id, {})["welcome_channel"] = ctx.channel.id
        self.config[guild_id]["welcome_message"] = message
        self.save_config()
        await ctx.send(f"✅ Welcome message set in {ctx.channel.mention}")

    @commands.command(name="setfarewell")
    @commands.has_permissions(administrator=True)
    async def set_farewell(self, ctx, *, message: str):
        """Original command logic with validation"""
        if len(message) > 1000:
            return await ctx.send("❌ Message too long (max 1000 chars)")
            
        guild_id = str(ctx.guild.id)
        self.config.setdefault(guild_id, {})["farewell_channel"] = ctx.channel.id
        self.config[guild_id]["farewell_message"] = message
        self.save_config()
        await ctx.send(f"✅ Farewell message set in {ctx.channel.mention}")

async def setup(bot):
    await bot.add_cog(WelcomeFarewell(bot))