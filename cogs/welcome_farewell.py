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
from PIL import Image, ImageDraw, ImageFont
import aiohttp
import io

class WelcomeFarewell(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.config_file = "logs/welcome_farewell_config.json"
        self.config = self.load_config()
        self.welcome_images = [
            "assets/greeting/welcome1.jpg",
            "assets/greeting/welcome2.jpg",
            "assets/greeting/welcome3.jpg",
        ]
        self.farewell_gifs = ["assets/greeting/goodbye.gif"]

    def load_config(self):
        if os.path.exists(self.config_file):
            with open(self.config_file, "r") as f:
                return json.load(f)
        return {}

    def save_config(self):
        with open(self.config_file, "w") as f:
            json.dump(self.config, f, indent=4)

    async def create_welcome_image(self, member):
        background_path = random.choice(self.welcome_images)
        if not os.path.exists(background_path):
            print(f"Error: Background image '{background_path}' not found.")
            return None

        bg = Image.open(background_path).convert("RGBA")
        pfp_size = int(bg.height * 0.45)  # Even Bigger Avatar (45% of image height)
        pfp_position = ((bg.width - pfp_size) // 2, int(bg.height * 0.10))  # Centered

        # Get avatar image
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(str(member.display_avatar.url)) as resp:
                    if resp.status == 200:
                        pfp_bytes = await resp.read()
                    else:
                        return None
            except:
                return None
        
        pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((pfp_size, pfp_size))

        # Circular mask for PFP
        mask = Image.new("L", (pfp_size, pfp_size), 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0, pfp_size, pfp_size), fill=255)
        pfp.putalpha(mask)
        
        # Paste PFP onto background
        bg.paste(pfp, pfp_position, pfp)

        draw = ImageDraw.Draw(bg)

        # Load Stylish Font
        try:
            font_path = "assets/fonts/stylish.ttf"
            font = ImageFont.truetype(font_path, int(pfp_size * 0.30))  # 30% of PFP size
        except IOError:
            font = ImageFont.load_default()

        # Print Username Below Avatar
        username_text = member.name
        text_width = draw.textlength(username_text, font=font)
        text_x = (bg.width - text_width) // 2
        text_y = pfp_position[1] + pfp_size + 30  # Below PFP

        draw.text((text_x, text_y), username_text, (255, 255, 255), font=font)

        # Print Join Position (User is 123rd member)
        join_position = member.guild.member_count
        position_text = f"🎉 You are the {join_position}{'st' if join_position % 10 == 1 and join_position != 11 else 'nd' if join_position % 10 == 2 and join_position != 12 else 'rd' if join_position % 10 == 3 and join_position != 13 else 'th'} member!"
        
        try:
            position_font = ImageFont.truetype(font_path, int(pfp_size * 0.18))  # Smaller than name but clear
        except IOError:
            position_font = ImageFont.load_default()

        position_text_width = draw.textlength(position_text, font=position_font)
        position_x = (bg.width - position_text_width) // 2
        position_y = text_y + int(pfp_size * 0.35)  # Below name

        draw.text((position_x, position_y), position_text, (255, 255, 255), font=position_font)

        output = io.BytesIO()
        bg.save(output, format="PNG")
        output.seek(0)
        return output

    @commands.Cog.listener()
    async def on_member_join(self, member):
        guild_id = str(member.guild.id)
        if guild_id not in self.config or "welcome_channel" not in self.config[guild_id]:
            return
        
        channel = self.bot.get_channel(self.config[guild_id]["welcome_channel"])
        if not channel:
            return
        
        message = self.config[guild_id].get("welcome_message", "Welcome, {user}! 🎉").replace("{user}", member.mention)
        
        image = await self.create_welcome_image(member)
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
        if guild_id not in self.config or "farewell_channel" not in self.config[guild_id]:
            return

        channel = self.bot.get_channel(self.config[guild_id]["farewell_channel"])
        if not channel:
            return

        remaining_members = member.guild.member_count
        message = self.config[guild_id].get("farewell_message", "Goodbye, {user}! We'll miss you! 😢").replace("{user}", member.mention)
        message += f"\n👥 Members left: **{remaining_members}**"

        gif = random.choice(self.farewell_gifs)
        if os.path.exists(gif):
            file = discord.File(gif, filename="farewell.gif")
            embed = discord.Embed(description=message, color=discord.Color.red())
            embed.set_image(url="attachment://farewell.gif")
            await channel.send(embed=embed, file=file)
        else:
            await channel.send(message)

    @commands.command(name="setwelcome")
    @commands.has_permissions(administrator=True)
    async def set_welcome(self, ctx, *, message: str):
        guild_id = str(ctx.guild.id)
        self.config.setdefault(guild_id, {})["welcome_channel"] = ctx.channel.id
        self.config[guild_id]["welcome_message"] = message
        self.save_config()
        await ctx.send(f"✅ Welcome message set for **#{ctx.channel.name}**:\n{message}")

    @commands.command(name="setfarewell")
    @commands.has_permissions(administrator=True)
    async def set_farewell(self, ctx, *, message: str):
        guild_id = str(ctx.guild.id)
        self.config.setdefault(guild_id, {})["farewell_channel"] = ctx.channel.id
        self.config[guild_id]["farewell_message"] = message
        self.save_config()
        await ctx.send(f"✅ Farewell message set for **#{ctx.channel.name}**:\n{message}")

async def setup(bot):
    await bot.add_cog(WelcomeFarewell(bot))


# import discord
# from discord.ext import commands
# import json
# import os
# import random
# from PIL import Image, ImageDraw, ImageFont
# import aiohttp
# import io

# class WelcomeFarewell(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.config_file = "logs/welcome_farewell_config.json"
#         self.config = self.load_config()
#         self.welcome_images = [
#             "assets/greeting/welcome1.jpg",
#             "assets/greeting/welcome2.jpg",
#             "assets/greeting/welcome3.jpg",
#             "assets/greeting/welcome4.jpg",
#             "assets/greeting/welcome5.jpg",
#             "assets/greeting/welcome6.jpg",
#         ]
#         self.farewell_gifs = [
#             "assets/greeting/goodbye.gif"
#         ]

#     def load_config(self):
#         if os.path.exists(self.config_file):
#             with open(self.config_file, "r") as f:
#                 return json.load(f)
#         return {}

#     def save_config(self):
#         with open(self.config_file, "w") as f:
#             json.dump(self.config, f, indent=4)

#     async def create_welcome_image(self, member):
#         background_path = random.choice(self.welcome_images)
        
#         if not os.path.exists(background_path):
#             print(f"Error: Background image '{background_path}' not found.")
#             return None
        
#         bg = Image.open(background_path).convert("RGBA")
#         pfp_size = min(bg.width, bg.height) // 3  # Make PFP size proportional to image
#         pfp_position = ((bg.width - pfp_size) // 2, (bg.height - pfp_size) // 3)  # Centered horizontally, 1/3 from top
        
#         # Get avatar image
#         async with aiohttp.ClientSession() as session:
#             try:
#                 async with session.get(str(member.display_avatar.url)) as resp:
#                     if resp.status == 200:
#                         pfp_bytes = await resp.read()
#                     else:
#                         return None
#             except:
#                 return None
        
#         pfp = Image.open(io.BytesIO(pfp_bytes)).convert("RGBA").resize((pfp_size, pfp_size))

#         # Create circular mask for PFP
#         mask = Image.new("L", (pfp_size, pfp_size), 0)
#         draw = ImageDraw.Draw(mask)
#         draw.ellipse((0, 0, pfp_size, pfp_size), fill=255)
#         pfp.putalpha(mask)
        
#         # Paste PFP onto background
#         bg.paste(pfp, pfp_position, pfp)

#         draw = ImageDraw.Draw(bg)
        
#         # Use a stylish font (fallback to default if not available)
#         try:
#             font = ImageFont.truetype("assets/fonts/coolfont.ttf", pfp_size // 5)
#         except IOError:
#             font = ImageFont.load_default()

#         # Get member count
#         member_count = member.guild.member_count

#         # Center text properly
#         username_text = member.name
#         member_count_text = f"You’re the {member_count}th member!"

#         text_x = (bg.width - draw.textlength(username_text, font=font)) // 2
#         text_y = pfp_position[1] + pfp_size + 20

#         count_x = (bg.width - draw.textlength(member_count_text, font=font)) // 2
#         count_y = text_y + 50

#         draw.text((text_x, text_y), username_text, (255, 255, 255), font=font)
#         draw.text((count_x, count_y), member_count_text, (255, 255, 255), font=font)

#         output = io.BytesIO()
#         bg.save(output, format="PNG")
#         output.seek(0)
#         return output

#     @commands.Cog.listener()
#     async def on_member_join(self, member):
#         guild_id = str(member.guild.id)
#         if guild_id not in self.config:
#             return
#         if "welcome_channel" not in self.config[guild_id]:
#             return
        
#         channel = self.bot.get_channel(self.config[guild_id]["welcome_channel"])
#         if not channel:
#             return
        
#         message = self.config[guild_id].get("welcome_message", "Welcome, {user}! Enjoy your stay!").replace("{user}", member.mention)
        
#         image = await self.create_welcome_image(member)
#         if image:
#             file = discord.File(image, filename="welcome.png")
#             embed = discord.Embed(description=message, color=discord.Color.blue())
#             embed.set_image(url="attachment://welcome.png")
#             await channel.send(embed=embed, file=file)
#         else:
#             await channel.send(message)

#     @commands.Cog.listener()
#     async def on_member_remove(self, member):
#         guild_id = str(member.guild.id)
#         if guild_id not in self.config:
#             return
#         if "farewell_channel" not in self.config[guild_id]:
#             return

#         channel = self.bot.get_channel(self.config[guild_id]["farewell_channel"])
#         if not channel:
#             return

#         remaining_members = member.guild.member_count
#         message = self.config[guild_id].get("farewell_message", "Goodbye, {user}! We'll miss you!").replace("{user}", member.mention)
#         message += f"\nThere are now {remaining_members} members left."

#         gif = random.choice(self.farewell_gifs)
#         if os.path.exists(gif):
#             file = discord.File(gif, filename="farewell.gif")
#             embed = discord.Embed(description=message, color=discord.Color.red())
#             embed.set_image(url="attachment://farewell.gif")
#             await channel.send(embed=embed, file=file)
#         else:
#             await channel.send(message)

#     @commands.command(name="setwelcome")
#     @commands.has_permissions(administrator=True)
#     async def set_welcome(self, ctx, *, message: str):
#         guild_id = str(ctx.guild.id)
#         self.config.setdefault(guild_id, {})["welcome_channel"] = ctx.channel.id
#         self.config[guild_id]["welcome_message"] = message
#         self.save_config()
#         await ctx.send(f"✅ Welcome message set for **#{ctx.channel.name}**:\n{message}")

#     @commands.command(name="setfarewell")
#     @commands.has_permissions(administrator=True)
#     async def set_farewell(self, ctx, *, message: str):
#         guild_id = str(ctx.guild.id)
#         self.config.setdefault(guild_id, {})["farewell_channel"] = ctx.channel.id
#         self.config[guild_id]["farewell_message"] = message
#         self.save_config()
#         await ctx.send(f"✅ Farewell message set for **#{ctx.channel.name}**:\n{message}")

# async def setup(bot):
#     await bot.add_cog(WelcomeFarewell(bot))
