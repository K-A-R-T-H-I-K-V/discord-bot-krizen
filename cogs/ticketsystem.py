##### VERY BASIC 

# import discord
# from discord.ext import commands
# from discord import ui
# import datetime
# import json
# import io

# class TicketSystem(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.tickets = {}
#         self.log_channel_id = None
#         self.ticket_category_id = None

#     class SaveLogView(ui.View):
#         def __init__(self, cog, transcript):
#             super().__init__(timeout=60)
#             self.cog = cog
#             self.transcript = transcript
#             self.value = None

#         @ui.button(label='Save Log', style=discord.ButtonStyle.green)
#         async def save_log(self, interaction: discord.Interaction, button: ui.Button):
#             if self.cog.log_channel_id is None:
#                 return await interaction.response.send_message("Log channel not configured!", ephemeral=True)

#             log_channel = interaction.guild.get_channel(self.cog.log_channel_id)
#             if log_channel:
#                 file = discord.File(self.transcript, filename=f"transcript-{interaction.channel.name}.txt")
#                 await log_channel.send(f"Ticket log for {interaction.channel.name}", file=file)
#                 await interaction.response.send_message("Log saved successfully!", ephemeral=True)
#             else:
#                 await interaction.response.send_message("Couldn't find log channel!", ephemeral=True)
#             self.value = True
#             self.stop()

#         @ui.button(label='Don\'t Save', style=discord.ButtonStyle.red)
#         async def dont_save(self, interaction: discord.Interaction, button: ui.Button):
#             await interaction.response.send_message("Log not saved.", ephemeral=True)
#             self.value = False
#             self.stop()

#     class TicketView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=None)
#             self.cog = cog

#         @ui.button(label='Resolve Ticket', style=discord.ButtonStyle.green, custom_id='resolve_ticket')
#         async def resolve(self, interaction: discord.Interaction, button: ui.Button):
#             if not interaction.user.guild_permissions.administrator:
#                 return await interaction.response.send_message("Only admins can resolve tickets!", ephemeral=True)

#             transcript = await self.cog.save_transcript(interaction.channel)
#             view = self.cog.SaveLogView(self.cog, transcript)
#             await interaction.response.send_message("Save transcript to logs?", view=view)
#             await view.wait()

#             if interaction.channel.id in self.cog.tickets.values():
#                 user_id = next(k for k, v in self.cog.tickets.items() if v == interaction.channel.id)
#                 del self.cog.tickets[user_id]
#             await interaction.channel.delete(reason="Ticket resolved")

#         @ui.button(label='Keep Pending', style=discord.ButtonStyle.grey, custom_id='pending_ticket')
#         async def pending(self, interaction: discord.Interaction, button: ui.Button):
#             if not interaction.user.guild_permissions.administrator:
#                 return await interaction.response.send_message("Only admins can manage tickets!", ephemeral=True)
#             await interaction.response.send_message("Ticket kept pending.", ephemeral=True)

#     async def save_transcript(self, channel):
#         messages = []
#         async for message in channel.history(oldest_first=True):
#             messages.append(f"{message.created_at.strftime('%Y-%m-%d %H:%M:%S')} {message.author.display_name}: {message.content}")

#         transcript = "\n".join(messages)
#         return io.BytesIO(transcript.encode('utf-8'))

#     @commands.Cog.listener()
#     async def on_ready(self):
#         print(f'Ticket System Cog loaded')

#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def setup_tickets(self, ctx, log_channel: discord.TextChannel = None, category: discord.CategoryChannel = None):
#         # Auto-create channels if not provided
#         if log_channel is None:
#             log_channel = await ctx.guild.create_text_channel(
#                 name="ticket-logs",
#                 reason="Auto-created ticket logs channel"
#             )
        
#         if category is None:
#             category = await ctx.guild.create_category_channel(
#                 name="Support Tickets",
#                 reason="Auto-created tickets category"
#             )

#         self.log_channel_id = log_channel.id
#         self.ticket_category_id = category.id
        
#         # Set permissions for category
#         await category.set_permissions(ctx.guild.default_role, read_messages=False)
        
#         await ctx.send(f"**Ticket System Configured**\n"
#                        f"📁 Category: {category.mention}\n"
#                        f"📜 Log Channel: {log_channel.mention}")

#     @commands.command()
#     async def new(self, ctx):
#         """Create a new support ticket"""
#         if ctx.author.id in self.tickets:
#             return await ctx.send("You already have an open ticket!", ephemeral=True)

#         # Create category if not exists
#         category = self.bot.get_channel(self.ticket_category_id)
#         if category is None:
#             category = await ctx.guild.create_category_channel("Support Tickets")
#             self.ticket_category_id = category.id

#         # Create ticket channel
#         overwrites = {
#             ctx.guild.default_role: discord.PermissionOverwrite(read_messages=False),
#             ctx.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
#             ctx.guild.me: discord.PermissionOverwrite(read_messages=True)
#         }

#         ticket_channel = await category.create_text_channel(
#             name=f"ticket-{ctx.author.display_name}",
#             overwrites=overwrites
#         )

#         self.tickets[ctx.author.id] = ticket_channel.id

#         # Send initial message with controls
#         view = self.TicketView(self)
#         await ticket_channel.send(
#             f"{ctx.author.mention} created a ticket!\n"
#             f"🔧 **Admin Controls** 🔧",
#             view=view
#         )
#         await ctx.send(f"Ticket created: {ticket_channel.mention}", ephemeral=True)

# async def setup(bot):
#     cog = TicketSystem(bot)
#     await bot.add_cog(cog)
#     bot.add_view(cog.TicketView(cog))


import discord
from discord.ext import commands
from discord import ui, TextStyle, ButtonStyle
from datetime import datetime

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}
        self.ticket_count = 0

    # =====================
    # 🎨 INTERFACE COMPONENTS
    # =====================
    class TicketCreationView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @ui.button(label="Create Ticket", style=ButtonStyle.blurple, 
                  emoji="📩", custom_id="persistent:create_ticket")
        async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
            modal = self.cog.TicketReasonModal(self.cog)
            await interaction.response.send_modal(modal)

    class TicketReasonModal(ui.Modal):
        def __init__(self, cog):
            super().__init__(title="Create Support Ticket", timeout=300)
            self.cog = cog
            self.reason = ui.TextInput(
                label="Describe your issue",
                style=TextStyle.long,
                placeholder="Please explain your problem in detail...",
                required=True
            )
            self.add_item(self.reason)

        async def on_submit(self, interaction: discord.Interaction):
            await interaction.response.defer(ephemeral=True)
            try:
                ticket_channel = await self.cog.create_ticket_channel(interaction.user, interaction.guild, str(self.reason))
                embed = discord.Embed(
                    title="Ticket Created",
                    description=f"Visit your private channel: {ticket_channel.mention}",
                    color=0x00ff00
                )
                await interaction.followup.send(embed=embed, ephemeral=True)
            except Exception as e:
                error_embed = discord.Embed(
                    title="Error",
                    description="Failed to create ticket",
                    color=0xff0000
                )
                await interaction.followup.send(embed=error_embed, ephemeral=True)

    class TicketControlView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @ui.button(label="Close Ticket", style=ButtonStyle.red, 
                  emoji="🔒", custom_id="persistent:close_ticket")
        async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
            if not interaction.user.guild_permissions.administrator:
                embed = discord.Embed(
                    title="Permission Denied",
                    description="Only staff can close tickets",
                    color=0xff0000
                )
                return await interaction.response.send_message(embed=embed, ephemeral=True)
            
            confirm_view = self.cog.ConfirmationView(self.cog)
            await interaction.response.send_message(
                embed=discord.Embed(
                    title="Confirm Closure",
                    description="Are you sure you want to close this ticket?",
                    color=0xffd700
                ),
                view=confirm_view,
                ephemeral=True
            )
            
            await confirm_view.wait()
            
            if confirm_view.value:
                try:
                    await interaction.edit_original_response(
                        embed=discord.Embed(
                            title="Closing Ticket...",
                            color=0x7289da
                        ),
                        view=None
                    )
                    await self.cog.close_ticket(interaction.channel, interaction.user)
                except Exception as e:
                    await interaction.followup.send(
                        embed=discord.Embed(
                            title="Error",
                            description="Failed to close ticket",
                            color=0xff0000
                        ),
                        ephemeral=True
                    )
            else:
                await interaction.edit_original_response(
                    embed=discord.Embed(
                        title="Cancelled",
                        description="Ticket closure cancelled",
                        color=0x00ff00
                    ),
                    view=None
                )

    class ConfirmationView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=30)
            self.cog = cog
            self.value = None

        @ui.button(label="Confirm", style=ButtonStyle.green, emoji="✅")
        async def confirm(self, interaction: discord.Interaction, button: ui.Button):
            self.value = True
            await interaction.response.defer()
            self.stop()

        @ui.button(label="Cancel", style=ButtonStyle.grey, emoji="❌")
        async def cancel(self, interaction: discord.Interaction, button: ui.Button):
            self.value = False
            await interaction.response.defer()
            self.stop()

    # =====================
    # 🛠️ CORE FUNCTIONALITY
    # =====================
    async def create_ticket_channel(self, user: discord.User, guild: discord.Guild, reason: str):
        category = await self.get_or_create_category(guild)
        self.ticket_count += 1

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }

        ticket_channel = await category.create_text_channel(
            name=f"ticket-{self.ticket_count}",
            overwrites=overwrites,
            topic=f"{user.name} | {reason[:50]}"
        )

        embed = discord.Embed(
            title=f"Ticket #{self.ticket_count}",
            description=f"**User:** {user.mention}\n**Reason:** {reason}",
            color=0x7289da
        )
        embed.add_field(
            name="Information",
            value=f"Created: {discord.utils.format_dt(datetime.now(), 'f')}\nStatus: 🟢 Open",
            inline=False
        )
        
        view = self.TicketControlView(self)
        await ticket_channel.send(
            content=f"{user.mention} | Support Team",
            embed=embed,
            view=view
        )
        self.tickets[user.id] = ticket_channel.id
        return ticket_channel

    async def close_ticket(self, channel: discord.TextChannel, closer: discord.Member):
        try:
            user_id = next(k for k, v in self.tickets.items() if v == channel.id)
            user = await self.bot.fetch_user(user_id)
            
            closure_embed = discord.Embed(
                title="Ticket Closed",
                description="Thank you for contacting support!",
                color=0x00ff00
            )
            try:
                await user.send(embed=closure_embed)
            except:
                pass
            
            del self.tickets[user_id]
            try:
                await channel.delete()
            except discord.NotFound:
                pass
        except Exception as e:
            error_embed = discord.Embed(
                title="Error",
                description="Failed to close ticket properly",
                color=0xff0000
            )
            await channel.send(embed=error_embed)

    # =====================
    # ⚙️ UTILITIES
    # =====================
    async def get_or_create_category(self, guild: discord.Guild):
        category = discord.utils.get(guild.categories, name="Support Tickets")
        if category:
            return category

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            guild.me: discord.PermissionOverwrite(read_messages=True)
        }
        return await guild.create_category(
            name="Support Tickets",
            overwrites=overwrites,
            reason="Ticket system setup"
        )

    # =====================
    # 💻 COMMANDS
    # =====================
    @commands.command()
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx: commands.Context):
        """Create the ticket creation panel"""
        embed = discord.Embed(
            title="Need Help?",
            description="Click below to create a support ticket!",
            color=0x7289da
        )
        embed.add_field(
            name="Guidelines",
            value="• Be specific with your issue\n• Stay respectful\n• No spam",
            inline=False
        )
        view = self.TicketCreationView(self)
        await ctx.send(embed=embed, view=view)
        await ctx.message.delete()

    @commands.Cog.listener()
    async def on_ready(self):
        self.bot.add_view(self.TicketCreationView(self))
        self.bot.add_view(self.TicketControlView(self))
        print(f"Ticket system ready! Active tickets: {len(self.tickets)}")

async def setup(bot):
    await bot.add_cog(TicketSystem(bot))


# ### LOVELY WORKING


# import discord
# from discord.ext import commands, tasks
# from discord import ui, TextStyle, ButtonStyle
# import aiosqlite
# from datetime import datetime
# import io
# from typing import Optional

# class PremiumTicketSystem(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.db = None
#         self.initialize_db.start()
#         self.ticket_count = 0
#         self.logo_url = "https://i.imgur.com/xyz.png"  # Replace with your logo

#     # =====================
#     # 🛠️ Database Setup
#     # =====================
#     @tasks.loop(count=1)
#     async def initialize_db(self):
#         self.db = await aiosqlite.connect('tickets.db')
#         await self.create_tables()

#     async def create_tables(self):
#         await self.db.execute('''
#             CREATE TABLE IF NOT EXISTS tickets (
#                 id INTEGER PRIMARY KEY,
#                 user_id INTEGER,
#                 channel_id INTEGER,
#                 status TEXT DEFAULT 'open',
#                 created_at DATETIME,
#                 closed_at DATETIME,
#                 transcript TEXT
#             )
#         ''')
#         await self.db.commit()

#     # =====================
#     # 🎨 Interactive Components
#     # =====================
#     class TicketCreationView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=None)
#             self.cog = cog

#         @ui.button(label="Create Ticket", style=ButtonStyle.blurple, emoji="📩", custom_id="persistent:create_ticket")
#         async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             modal = self.cog.TicketReasonModal(self.cog)
#             await interaction.response.send_modal(modal)

#     class TicketReasonModal(ui.Modal):
#         def __init__(self, cog):
#             super().__init__(title="Open Support Ticket", timeout=300)
#             self.cog = cog
#             self.reason = ui.TextInput(
#                 label="Reason for contact",
#                 style=TextStyle.long,
#                 placeholder="Describe your issue in detail...",
#                 required=True,
#                 max_length=1000
#             )
#             self.add_item(self.reason)

#         async def on_submit(self, interaction: discord.Interaction):
#             await interaction.response.defer(ephemeral=True)
#             try:
#                 ticket_channel = await self.cog.create_ticket_channel(interaction.user, interaction.guild, str(self.reason))
#                 await interaction.followup.send(f"Ticket created! {ticket_channel.mention}", ephemeral=True)
#             except Exception as e:
#                 await interaction.followup.send("❌ Failed to create ticket. Please contact an admin.", ephemeral=True)
#                 print(f"Ticket creation error: {e}")

#     class TicketControlView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=None)
#             self.cog = cog

#         @ui.button(label="Close Ticket", style=ButtonStyle.red, emoji="🔒", custom_id="persistent:close_ticket")
#         async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             if not interaction.user.guild_permissions.administrator:
#                 return await interaction.response.send_message("❌ Only admins can close tickets!", ephemeral=True)

#             confirm = self.cog.ConfirmationView(self.cog)
#             await interaction.response.send_message(
#                 "Are you sure you want to close this ticket?",
#                 view=confirm,
#                 ephemeral=True
#             )
#             await confirm.wait()
            
#             if confirm.value:
#                 await self.cog.close_ticket(interaction.channel, interaction.user)

#         @ui.button(label="Add User", style=ButtonStyle.green, emoji="👥", custom_id="persistent:add_user")
#         async def add_user(self, interaction: discord.Interaction, button: ui.Button):
#             if not interaction.user.guild_permissions.administrator:
#                 return await interaction.response.send_message("❌ Only admins can manage users!", ephemeral=True)

#             modal = self.cog.AddUserModal(self.cog)
#             await interaction.response.send_modal(modal)

#     class ConfirmationView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=30)
#             self.cog = cog
#             self.value = None

#         @ui.button(label="Confirm", style=ButtonStyle.green, emoji="✅")
#         async def confirm(self, interaction: discord.Interaction, button: ui.Button):
#             self.value = True
#             await interaction.response.defer()
#             self.stop()

#         @ui.button(label="Cancel", style=ButtonStyle.grey, emoji="❌")
#         async def cancel(self, interaction: discord.Interaction, button: ui.Button):
#             self.value = False
#             await interaction.response.defer()
#             self.stop()

#     class AddUserModal(ui.Modal):
#         def __init__(self, cog):
#             super().__init__(title="Add User to Ticket", timeout=300)
#             self.cog = cog
#             self.user = ui.TextInput(
#                 label="User ID or Mention",
#                 placeholder="Enter user ID or @mention",
#                 required=True
#             )
#             self.add_item(self.user)

#         async def on_submit(self, interaction: discord.Interaction):
#             try:
#                 user = await commands.MemberConverter().convert(interaction, str(self.user))
#                 await interaction.channel.set_permissions(user, read_messages=True)
#                 await interaction.response.send_message(f"✅ Added {user.mention} to the ticket!", ephemeral=True)
#             except:
#                 await interaction.response.send_message("❌ Couldn't find that user!", ephemeral=True)

#     # =====================
#     # 🚀 Core Functionality
#     # =====================
#     async def create_ticket_channel(self, user: discord.User, guild: discord.Guild, reason: str):
#         category = await self.get_or_create_category(guild)
#         log_channel = await self.get_log_channel(guild.id)

#         overwrites = {
#             guild.default_role: discord.PermissionOverwrite(read_messages=False),
#             user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
#             guild.me: discord.PermissionOverwrite(read_messages=True)
#         }

#         self.ticket_count += 1
#         ticket_channel = await category.create_text_channel(
#             name=f"ticket-{self.ticket_count}",
#             overwrites=overwrites,
#             topic=f"User: {user} | ID: {user.id} | Reason: {reason[:50]}"
#         )

#         embed = discord.Embed(
#             title=f"Ticket #{self.ticket_count}",
#             description=f"**User:** {user.mention}\n**Reason:** {reason}",
#             color=0x00ff00
#         )
#         embed.set_thumbnail(url=self.logo_url)
#         embed.add_field(name="Status", value="🟢 Open", inline=True)
#         embed.add_field(name="Created At", value=discord.utils.format_dt(datetime.now(), "F"), inline=True)
#         embed.set_footer(text="Support Team")

#         view = self.TicketControlView(self)
#         await ticket_channel.send(content=f"{user.mention} | Support Team", embed=embed, view=view)

#         async with self.db.cursor() as cursor:
#             await cursor.execute(
#                 'INSERT INTO tickets (user_id, channel_id, created_at) VALUES (?, ?, ?)',
#                 (user.id, ticket_channel.id, datetime.now())
#             )
#             await self.db.commit()

#         return ticket_channel

#     async def close_ticket(self, channel: discord.TextChannel, closer: discord.Member):
#         try:
#             transcript = await self.generate_transcript(channel)
            
#             async with self.db.cursor() as cursor:
#                 await cursor.execute(
#                     'UPDATE tickets SET status=?, closed_at=?, transcript=? WHERE channel_id=?',
#                     ('closed', datetime.now(), transcript, channel.id)
#                 )
#                 await cursor.execute('SELECT user_id FROM tickets WHERE channel_id=?', (channel.id,))
#                 user_id = (await cursor.fetchone())[0]
#                 await self.db.commit()

#             log_channel = self.bot.get_channel(await self.get_log_channel(channel.guild.id))
#             if log_channel:
#                 file = discord.File(io.BytesIO(transcript.encode()), filename=f"transcript-{channel.name}.txt")
#                 embed = discord.Embed(
#                     title=f"Ticket Closed #{self.ticket_count}",
#                     color=0xff0000,
#                     description=f"Closed by {closer.mention}"
#                 )
#                 await log_channel.send(embed=embed, file=file)

#             user = await self.bot.fetch_user(user_id)
#             closure_embed = discord.Embed(
#                 title="Ticket Closed",
#                 description="Thank you for contacting support!",
#                 color=0x00ff00
#             )
#             await user.send(embed=closure_embed)

#             await channel.delete(reason=f"Closed by {closer}")
#         except Exception as e:
#             print(f"Error closing ticket: {e}")
#             if channel:
#                 await channel.send("❌ Error closing ticket. Please contact an admin.")

#     # =====================
#     # 🔧 Utilities
#     # =====================
#     async def get_or_create_category(self, guild: discord.Guild) -> discord.CategoryChannel:
#         category = discord.utils.get(guild.categories, name="Support Tickets")
#         if category:
#             return category

#         overwrites = {
#             guild.default_role: discord.PermissionOverwrite(read_messages=False),
#             guild.me: discord.PermissionOverwrite(read_messages=True)
#         }
#         admin_roles = [role for role in guild.roles if role.permissions.administrator]
#         for role in admin_roles:
#             overwrites[role] = discord.PermissionOverwrite(read_messages=True)

#         return await guild.create_category_channel(
#             name="Support Tickets",
#             overwrites=overwrites,
#             reason="Ticket system setup"
#         )

#     async def get_log_channel(self, guild_id: int) -> int:
#         guild = self.bot.get_guild(guild_id)
#         log_channel = discord.utils.get(guild.text_channels, name="ticket-logs")
        
#         if log_channel:
#             return log_channel.id

#         overwrites = {
#             guild.default_role: discord.PermissionOverwrite(read_messages=False),
#             guild.me: discord.PermissionOverwrite(read_messages=True)
#         }
#         admin_roles = [role for role in guild.roles if role.permissions.administrator]
#         for role in admin_roles:
#             overwrites[role] = discord.PermissionOverwrite(read_messages=True)

#         new_channel = await guild.create_text_channel(
#             name="ticket-logs",
#             overwrites=overwrites,
#             reason="Ticket system setup"
#         )
#         return new_channel.id

#     async def generate_transcript(self, channel: discord.TextChannel) -> str:
#         transcript = [f"Transcript for {channel.name}\n{'='*30}"]
#         async for message in channel.history(oldest_first=True):
#             transcript.append(
#                 f"[{message.created_at.strftime('%Y-%m-%d %H:%M:%S')}] "
#                 f"{message.author.display_name}: "
#                 f"{message.content}"
#             )
#         return "\n".join(transcript)

#     # =====================
#     # 💻 Commands
#     # =====================
#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def setup_tickets(self, ctx: commands.Context):
#         """Initialize the ticket system"""
#         await self.get_or_create_category(ctx.guild)
#         await self.get_log_channel(ctx.guild.id)
#         await ctx.send("✅ Ticket system initialized! Use `!ticketpanel` to create the creation panel")

#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     @commands.cooldown(1, 60, commands.BucketType.guild)
#     async def ticketpanel(self, ctx: commands.Context):
#         """Create the ticket creation panel"""
#         embed = discord.Embed(
#             title="📨 Need Help?",
#             description="Click the button below to create a support ticket!",
#             color=0x00ff00
#         )
#         embed.set_thumbnail(url=self.logo_url)
#         view = self.TicketCreationView(self)
#         await ctx.send(embed=embed, view=view)
#         await ctx.message.delete()

#     @commands.Cog.listener()
#     async def on_ready(self):
#         self.bot.add_view(self.TicketCreationView(self))
#         self.bot.add_view(self.TicketControlView(self))
#         print(f"Premium Ticket System loaded!")

# async def setup(bot):
#     await bot.add_cog(PremiumTicketSystem(bot))



##### NOT TESTED

# # import discord
# from discord.ext import commands, tasks
# from discord import ui, SelectOption, TextStyle
# import aiosqlite
# from datetime import datetime
# import io
# from typing import List

# class EnterpriseTicketSystem(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.db = None
#         self.initialize_db.start()

#     # =====================
#     # 🗃️ Database Setup
#     # =====================
#     @tasks.loop(count=1)
#     async def initialize_db(self):
#         self.db = await aiosqlite.connect('enterprise_tickets.db')
#         await self.create_tables()

#     async def create_tables(self):
#         await self.db.execute('''
#             CREATE TABLE IF NOT EXISTS tickets (
#                 ticket_id INTEGER PRIMARY KEY AUTOINCREMENT,
#                 creator_id INTEGER,
#                 channel_id INTEGER UNIQUE,
#                 status TEXT DEFAULT 'open',
#                 created_at DATETIME,
#                 closed_at DATETIME
#             )
#         ''')
#         await self.db.execute('''
#             CREATE TABLE IF NOT EXISTS ticket_users (
#                 ticket_id INTEGER,
#                 user_id INTEGER,
#                 PRIMARY KEY (ticket_id, user_id),
#                 FOREIGN KEY(ticket_id) REFERENCES tickets(ticket_id)
#             )
#         ''')
#         await self.db.commit()

#     # =====================
#     # 🎨 Interactive Views
#     # =====================
#     class TicketCreationView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=None)
#             self.cog = cog

#         @ui.button(label="🚀 Create New Ticket", style=discord.ButtonStyle.blurple, custom_id="create_ticket")
#         async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             modal = self.cog.TicketDetailsModal(self.cog)
#             await interaction.response.send_modal(modal)

#     class TicketDetailsModal(ui.Modal):
#         def __init__(self, cog):
#             super().__init__(title="📝 Create Support Ticket", timeout=300)
#             self.cog = cog
#             self.topic = ui.TextInput(
#                 label="Ticket Subject",
#                 placeholder="Briefly describe your issue...",
#                 style=TextStyle.short,
#                 required=True
#             )
#             self.details = ui.TextInput(
#                 label="Detailed Description",
#                 placeholder="Provide all relevant details...",
#                 style=TextStyle.long,
#                 required=True
#             )
#             self.add_item(self.topic)
#             self.add_item(self.details)

#         async def on_submit(self, interaction: discord.Interaction):
#             await interaction.response.defer(ephemeral=True)
#             ticket_id, channel = await self.cog.create_ticket(
#                 interaction.user,
#                 interaction.guild,
#                 str(self.topic),
#                 str(self.details)
#             )
#             await interaction.followup.send(
#                 f"🎉 Ticket #{ticket_id} created! {channel.mention}",
#                 ephemeral=True
#             )

#     class TicketManagementView(ui.View):
#         def __init__(self, cog, ticket_id: int):
#             super().__init__(timeout=None)
#             self.cog = cog
#             self.ticket_id = ticket_id

#         @ui.button(label="🔒 Close Ticket", style=discord.ButtonStyle.red)
#         async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             await self.cog.close_ticket(self.ticket_id, interaction.user)
#             await interaction.response.send_message(
#                 f"✅ Ticket #{self.ticket_id} closed!", 
#                 ephemeral=True
#             )

#         @ui.button(label="👥 Manage Users", style=discord.ButtonStyle.green)
#         async def manage_users(self, interaction: discord.Interaction, button: ui.Button):
#             await interaction.response.send_message(
#                 view=self.cog.UserManagementView(self.cog, self.ticket_id),
#                 ephemeral=True
#             )

#     class UserManagementView(ui.View):
#         def __init__(self, cog, ticket_id: int):
#             super().__init__(timeout=60)
#             self.cog = cog
#             self.ticket_id = ticket_id

#         @ui.select(
#             placeholder="Select users to add/remove",
#             min_values=0,
#             max_values=25,
#             options=[],  # Dynamically populated
#             custom_id="user_selector"
#         )
#         async def user_select(self, interaction: discord.Interaction, select: ui.Select):
#             current_users = await self.cog.get_ticket_users(self.ticket_id)
#             selected_ids = [int(v) for v in select.values]
            
#             # Update permissions
#             for user in interaction.guild.members:
#                 if user.id in selected_ids and user.id not in current_users:
#                     await self.cog.add_user_to_ticket(self.ticket_id, user)
#                 elif user.id not in selected_ids and user.id in current_users:
#                     await self.cog.remove_user_from_ticket(self.ticket_id, user)
            
#             await interaction.response.send_message(
#                 "✅ User permissions updated!", 
#                 ephemeral=True
#             )

#         async def populate_users(self, guild: discord.Guild):
#             current_users = await self.cog.get_ticket_users(self.ticket_id)
#             options = []
            
#             for member in guild.members:
#                 if not member.bot and member.guild_permissions.administrator:
#                     options.append(SelectOption(
#                         label=f"{member.display_name} {'⭐' if member.id in current_users else ''}",
#                         value=str(member.id),
#                         emoji="👤" if member.id in current_users else "➕"
#                     ))
            
#             self.user_select.options = options

#     # =====================
#     # 🚀 Core Functionality
#     # =====================
#     async def create_ticket(self, creator: discord.User, guild: discord.Guild, topic: str, details: str):
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 INSERT INTO tickets (creator_id, channel_id, created_at)
#                 VALUES (?, ?, ?)
#             ''', (creator.id, None, datetime.now()))
#             await self.db.commit()
#             ticket_id = cursor.lastrowid

#         channel = await self._create_ticket_channel(guild, ticket_id, topic)
#         await self._init_ticket_permissions(channel, creator)
#         await self._send_ticket_embed(channel, ticket_id, creator, topic, details)
        
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 UPDATE tickets SET channel_id = ? WHERE ticket_id = ?
#             ''', (channel.id, ticket_id))
#             await self.db.commit()

#         return ticket_id, channel

#     async def _create_ticket_channel(self, guild: discord.Guild, ticket_id: int, topic: str):
#         category = await self._get_ticket_category(guild)
#         return await category.create_text_channel(
#             name=f"ticket-{ticket_id}",
#             topic=f"#{ticket_id} - {topic[:50]}"
#         )

#     async def _init_ticket_permissions(self, channel: discord.TextChannel, creator: discord.User):
#         await channel.set_permissions(creator, read_messages=True, send_messages=True)
#         await channel.set_permissions(guild.default_role, read_messages=False)

#     async def _send_ticket_embed(self, channel: discord.TextChannel, ticket_id: int, 
#                                creator: discord.User, topic: str, details: str):
#         embed = discord.Embed(
#             title=f"📌 Ticket #{ticket_id} - {topic}",
#             description=details,
#             color=0x00ff00
#         )
#         embed.set_author(name=creator.display_name, icon_url=creator.display_avatar)
#         embed.add_field(name="Status", value="🟢 Open", inline=True)
#         embed.add_field(name="Created At", value=discord.utils.format_dt(datetime.now(), "F"), inline=True)
#         embed.set_footer(text=f"Ticket ID: {ticket_id}")

#         view = self.TicketManagementView(self, ticket_id)
#         await channel.send(f"{creator.mention} | Support Team", embed=embed, view=view)

#     async def close_ticket(self, ticket_id: int, closer: discord.Member):
#         # Database operations
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 UPDATE tickets SET status = 'closed', closed_at = ?
#                 WHERE ticket_id = ?
#             ''', (datetime.now(), ticket_id))
#             await self.db.commit()

#         # Channel cleanup
#         channel_id = await self.get_ticket_channel(ticket_id)
#         if channel := self.bot.get_channel(channel_id):
#             await channel.delete(reason=f"Closed by {closer}")

#         # Generate transcript
#         await self._log_transcript(ticket_id, closer)

#     async def _log_transcript(self, ticket_id: int, closer: discord.Member):
#         log_channel = await self._get_log_channel(closer.guild)
#         transcript = await self.generate_transcript(ticket_id)
        
#         embed = discord.Embed(
#             title=f"📁 Ticket #{ticket_id} Closed",
#             description=f"Closed by {closer.mention}",
#             color=0xff0000
#         )
#         file = discord.File(io.BytesIO(transcript.encode()), filename=f"ticket-{ticket_id}.md")
        
#         await log_channel.send(embed=embed, file=file)

#     # =====================
#     # 🔧 User Management
#     # =====================
#     async def add_user_to_ticket(self, ticket_id: int, user: discord.Member):
#         channel_id = await self.get_ticket_channel(ticket_id)
#         channel = self.bot.get_channel(channel_id)
        
#         await channel.set_permissions(user, read_messages=True)
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 INSERT OR IGNORE INTO ticket_users VALUES (?, ?)
#             ''', (ticket_id, user.id))
#             await self.db.commit()

#     async def remove_user_from_ticket(self, ticket_id: int, user: discord.Member):
#         channel_id = await self.get_ticket_channel(ticket_id)
#         channel = self.bot.get_channel(channel_id)
        
#         await channel.set_permissions(user, overwrite=None)
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 DELETE FROM ticket_users WHERE ticket_id = ? AND user_id = ?
#             ''', (ticket_id, user.id))
#             await self.db.commit()

#     async def get_ticket_users(self, ticket_id: int) -> List[int]:
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 SELECT user_id FROM ticket_users WHERE ticket_id = ?
#             ''', (ticket_id,))
#             return [row[0] for row in await cursor.fetchall()]

#     # =====================
#     # 🛠️ Utility Functions
#     # =====================
#     async def get_ticket_channel(self, ticket_id: int) -> int:
#         async with self.db.cursor() as cursor:
#             await cursor.execute('''
#                 SELECT channel_id FROM tickets WHERE ticket_id = ?
#             ''', (ticket_id,))
#             return (await cursor.fetchone())[0]

#     async def generate_transcript(self, ticket_id: int) -> str:
#         channel_id = await self.get_ticket_channel(ticket_id)
#         channel = self.bot.get_channel(channel_id)
        
#         transcript = [f"# Transcript of Ticket #{ticket_id}\n"]
#         async for message in channel.history(oldest_first=True):
#             transcript.append(
#                 f"**{message.author.display_name}** ({message.created_at:%Y-%m-%d %H:%M}):\n"
#                 f"{message.content}\n"
#                 f"{'-'*40}"
#             )
#         return "\n".join(transcript)

#     async def _get_ticket_category(self, guild: discord.Guild) -> discord.CategoryChannel:
#         # Implementation to get/create category
#         pass

#     async def _get_log_channel(self, guild: discord.Guild) -> discord.TextChannel:
#         # Implementation to get/create log channel
#         pass

#     # =====================
#     # 💻 Commands & Setup
#     # =====================
#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def ticket_panel(self, ctx: commands.Context):
#         """Create the ticket creation panel"""
#         embed = discord.Embed(
#             title="📨 Create Support Ticket",
#             description="Click below to create a new support ticket!",
#             color=0x7289da
#         )
#         view = self.TicketCreationView(self)
#         await ctx.send(embed=embed, view=view)

#     @commands.Cog.listener()
#     async def on_ready(self):
#         self.bot.add_view(self.TicketCreationView(self))
#         print("Enterprise Ticket System initialized!")

# async def setup(bot):
#    await bot.add_cog(EnterpriseTicketSystem(bot))