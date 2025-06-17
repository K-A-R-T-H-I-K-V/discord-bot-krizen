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
import json
import sqlite3
import logging
import logging.handlers
from sentence_transformers import SentenceTransformer, util
import asyncio
import os
import io
import traceback

# Configure logging with rotation
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.handlers.RotatingFileHandler('ticket.log', maxBytes=10*1024*1024, backupCount=5),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Default FAQs
DEFAULT_FAQS = {
    "faqs": [
        {
            "question": "What is the server IP?",
            "answer": "The server IP is `play.example.com:25565`.",
            "keywords": ["server ip", "ip address", "connect"]
        },
        {
            "question": "How do I reset my password?",
            "answer": "Visit example.com/reset and follow the instructions.",
            "keywords": ["password", "reset", "login"]
        },
        {
            "question": "Why am I lagging?",
            "answer": "Check your ping with `!ping` or restart your router.",
            "keywords": ["lag", "ping", "connection"]
        }
    ]
}

class TicketSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.tickets = {}
        self.ticket_count = 0
        self.db = sqlite3.connect("moderation.db")
        self.setup_db()
        try:
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("SentenceTransformer model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load SentenceTransformer model: {e}")
            self.model = None
        self.faqs = self.load_faqs()
        self.faq_embeddings = self.compute_faq_embeddings()
        self.staff_role_id = None  # Set to your staff role ID or None for admin-only
        self.log_channel_id = self.load_log_channel_id()
        os.makedirs("ticket_logs", exist_ok=True)
        logger.info("TicketSystem initialized")
        # Register persistent views
        self.bot.add_view(self.TicketCreationView(self))
        self.bot.add_view(self.TicketControlView(self, 0))  # 0 as placeholder for ticket_owner_id

    def setup_db(self):
        try:
            self.db.execute("""
                CREATE TABLE IF NOT EXISTS tickets (
                    ticket_id INTEGER PRIMARY KEY,
                    user_id INTEGER,
                    channel_id INTEGER,
                    reason TEXT,
                    created_at TEXT,
                    closed_at TEXT,
                    status TEXT,
                    log_file TEXT
                )
            """)
            cursor = self.db.cursor()
            cursor.execute("PRAGMA table_info(tickets)")
            columns = [info[1] for info in cursor.fetchall()]
            if 'log_file' not in columns:
                logger.info("Adding log_file column to tickets table")
                self.db.execute("ALTER TABLE tickets ADD COLUMN log_file TEXT")
            self.db.commit()
            cursor.execute("SELECT MAX(ticket_id) FROM tickets")
            max_id = cursor.fetchone()[0]
            self.ticket_count = max_id if max_id is not None else 0
            logger.debug(f"Database setup complete, ticket_count initialized to {self.ticket_count}")
        except Exception as e:
            logger.error(f"Database setup failed: {e}\n{traceback.format_exc()}")

    def load_faqs(self):
        try:
            with open("faqs.json", "r") as f:
                faqs = json.load(f)
                logger.info("Loaded faqs.json")
                return faqs.get("faqs", DEFAULT_FAQS["faqs"])
        except FileNotFoundError:
            logger.warning("faqs.json not found. Creating default")
            with open("faqs.json", "w") as f:
                json.dump(DEFAULT_FAQS, f, indent=2)
            return DEFAULT_FAQS["faqs"]
        except Exception as e:
            logger.error(f"Error loading faqs: {e}\n{traceback.format_exc()}")
            return DEFAULT_FAQS["faqs"]

    def load_log_channel_id(self):
        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                log_channel_id = config.get("log_channel_id")
                logger.info(f"Loaded log_channel_id: {log_channel_id}")
                return log_channel_id
        except FileNotFoundError:
            logger.warning("config.json not found. Creating default")
            with open("config.json", "w") as f:
                json.dump({"log_channel_id": None}, f, indent=2)
            return None
        except Exception as e:
            logger.error(f"Error loading config: {e}\n{traceback.format_exc()}")
            return None

    def save_log_channel_id(self, channel_id):
        try:
            config = {"log_channel_id": channel_id}
            with open("config.json", "w") as f:
                json.dump(config, f, indent=2)
            self.log_channel_id = channel_id
            logger.info(f"Saved log_channel_id: {channel_id}")
        except Exception as e:
            logger.error(f"Error saving log_channel_id: {e}\n{traceback.format_exc()}")

    def compute_faq_embeddings(self):
        if self.model is None:
            logger.warning("SentenceTransformer model not available, skipping FAQ embeddings")
            return None
        try:
            questions = [faq["question"] + " " + " ".join(faq["keywords"]) for faq in self.faqs]
            if not questions:
                logger.error("No FAQ questions available to compute embeddings")
                return None
            embeddings = self.model.encode(questions, batch_size=32, convert_to_tensor=True)
            logger.debug(f"Computed FAQ embeddings for {len(questions)} FAQs")
            return embeddings
        except Exception as e:
            logger.error(f"Error computing FAQ embeddings: {e}\n{traceback.format_exc()}")
            return None

    class TicketCreationView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=None)
            self.cog = cog

        @ui.button(label="Create Ticket", style=ButtonStyle.blurple, emoji="📩", custom_id="persistent_create_ticket")
        async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
            try:
                logger.debug(f"Create ticket button clicked by {interaction.user.id}")
                if interaction.user.id in self.cog.tickets:
                    channel_id = self.cog.tickets[interaction.user.id]
                    try:
                        channel = await interaction.guild.fetch_channel(channel_id)
                        await interaction.response.send_message(embed=discord.Embed(
                            title="❌ Error",
                            description=f"You already have an open ticket: {channel.mention}",
                            color=0xff0000
                        ), ephemeral=True)
                        return
                    except discord.NotFound:
                        logger.warning(f"Channel {channel_id} not found for user {interaction.user.id}. Clearing")
                        del self.cog.tickets[interaction.user.id]
                        self.cog.db.execute(
                            "UPDATE tickets SET status = ?, closed_at = ? WHERE channel_id = ?",
                            ("closed", datetime.now().isoformat(), channel_id)
                        )
                        self.cog.db.commit()

                if not interaction.guild.me.guild_permissions.manage_channels:
                    await interaction.response.send_message(embed=discord.Embed(
                        title="❌ Error",
                        description="Bot lacks 'Manage Channels' permission.",
                        color=0xff0000
                    ), ephemeral=True)
                    return

                modal = self.cog.TicketModal(self.cog)
                await interaction.response.send_modal(modal)
            except Exception as e:
                logger.error(f"Ticket creation failed: {e}\n{traceback.format_exc()}")
                try:
                    if not interaction.response.is_done():
                        await interaction.response.send_message(embed=discord.Embed(
                            title="❌ Error",
                            description="Failed to process interaction. Please try again or contact an admin.",
                            color=0xff0000
                        ), ephemeral=True)
                except Exception as e2:
                    logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

    class TicketModal(ui.Modal, title="Create Support Ticket"):
        def __init__(self, cog):
            super().__init__(timeout=300)
            self.cog = cog
            self.reason = ui.TextInput(
                label="Describe your issue",
                style=TextStyle.short,
                placeholder="Enter the reason for your ticket...",
                required=True
            )
            self.add_item(self.reason)

        async def on_submit(self, interaction: discord.Interaction):
            try:
                await interaction.response.defer(ephemeral=True)
                logger.debug(f"Ticket modal submitted by {interaction.user.id}")
                ticket_channel = await self.cog.create_ticket_channel(
                    interaction.user, interaction.guild, self.reason.value, ""
                )
                if self.cog.model and self.cog.faq_embeddings is not None:
                    suggestion = await self.cog.get_faq_suggestion(self.reason.value)
                    if suggestion:
                        await ticket_channel.send(embed=discord.Embed(
                            title="🤖 AI Suggestion",
                            description=f"Possible solution: {suggestion['answer']}\n\nUse `!suggest` for more or `!close` to close.",
                            color=0x7289da
                        ))
                    else:
                        logger.debug(f"No FAQ suggestion found for reason: {self.reason.value}")
                else:
                    logger.warning("AI model or embeddings unavailable, skipping FAQ suggestion")
                await interaction.followup.send(embed=discord.Embed(
                    title="✅ Ticket Created",
                    description=f"Your ticket has been created: {ticket_channel.mention}",
                    color=0x00ff00
                ), ephemeral=True)
            except Exception as e:
                logger.error(f"Ticket modal failed: {e}\n{traceback.format_exc()}")
                try:
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Error",
                        description="Failed to create ticket. Please try again or contact an admin.",
                        color=0xff0000
                    ), ephemeral=True)
                except Exception as e2:
                    logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

    class TicketControlView(ui.View):
        def __init__(self, cog, ticket_owner_id):
            super().__init__(timeout=None)
            self.cog = cog
            self.ticket_owner_id = ticket_owner_id

        @ui.button(label="Close Ticket", style=ButtonStyle.red, emoji="🔒", custom_id="persistent_close_ticket")
        async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
            try:
                await interaction.response.defer(ephemeral=True)
                logger.debug(f"Close ticket button clicked by {interaction.user.id}")
                is_admin = interaction.user.guild_permissions.administrator
                is_owner = interaction.user.id == self.ticket_owner_id
                is_staff = any(role.id == self.cog.staff_role_id for role in interaction.user.roles) if self.cog.staff_role_id else False

                if not (is_admin or is_owner or is_staff):
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Permission Denied",
                        description="Only staff or the ticket owner can close this ticket",
                        color=0xff0000
                    ), ephemeral=True)
                    return

                confirm_view = self.cog.ConfirmationView(self.cog)
                await interaction.followup.send(embed=discord.Embed(
                    title="⚠ Confirm Closure",
                    description="Are you sure you want to close this ticket?",
                    color=0xffd700
                ), view=confirm_view, ephemeral=True)
                await confirm_view.wait()

                if confirm_view.value:
                    log_text = await self.cog.log_conversation(interaction.channel)
                    await interaction.followup.send(embed=discord.Embed(
                        title="✅ Ticket Closed",
                        description="Ticket closed and logged",
                        color=0x00ff00
                    ), ephemeral=True)
                    await self.cog.close_ticket(interaction.channel, interaction.user, log_text)
                else:
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Cancelled",
                        description="Ticket closure cancelled",
                        color=0x00ff00
                    ), ephemeral=True)
            except Exception as e:
                logger.error(f"Close ticket failed: {e}\n{traceback.format_exc()}")
                if not isinstance(e, discord.errors.HTTPException) or e.code != 10003:
                    try:
                        await interaction.followup.send(embed=discord.Embed(
                            title="❌ Error",
                            description="Failed to close ticket. Please try again.",
                            color=0xff0000
                        ), ephemeral=True)
                    except Exception as e2:
                        logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

    class ConfirmationView(ui.View):
        def __init__(self, cog):
            super().__init__(timeout=30)
            self.cog = cog
            self.value = False

        @ui.button(label="Confirm", style=ButtonStyle.green, emoji="✅")
        async def confirm(self, interaction: discord.Interaction, button: ui.Button):
            try:
                self.value = True
                await interaction.response.defer(ephemeral=True)
                self.stop()
            except Exception as e:
                logger.error(f"Confirmation failed: {e}\n{traceback.format_exc()}")

        @ui.button(label="Cancel", style=ButtonStyle.grey, emoji="🔴")
        async def cancel(self, interaction: discord.Interaction, button: ui.Button):
            try:
                self.value = False
                await interaction.response.defer(ephemeral=True)
                self.stop()
            except Exception as e:
                logger.error(f"Cancel failed: {e}\n{traceback.format_exc()}")

    async def create_ticket_channel(self, user: discord.User, guild: discord.Guild, reason: str, attachment: str):
        try:
            category = await self.get_or_create_category(guild)
            self.ticket_count += 1

            staff_role = guild.get_role(self.staff_role_id) if self.staff_role_id else None
            if not staff_role and self.staff_role_id:
                logger.warning(f"Staff role ID {self.staff_role_id} not found. Using admins only")

            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            if staff_role:
                overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

            ticket_channel = await category.create_text_channel(
                name=f"ticket-{self.ticket_count:04d}",
                overwrites=overwrites,
                topic=f"{user.name} | {reason[:50]}"
            )

            embed = discord.Embed(
                title=f"🎫 Ticket #{self.ticket_count:04d}",
                description=f"**User:** {user.mention}\n**Reason:** {reason}",
                color=0x7289da
            )
            if attachment:
                embed.add_field(name="Attachment", value=attachment, inline=False)
            embed.add_field(
                name="Information",
                value=f"Created: {discord.utils.format_dt(datetime.now(), 'f')}\nStatus: 🟢 Open",
                inline=False
            )

            view = self.TicketControlView(self, user.id)
            content = f"{user.mention} | {staff_role.mention if staff_role else 'Support Team'}"
            await ticket_channel.send(content=content, embed=embed, view=view)
            self.tickets[user.id] = ticket_channel.id

            self.db.execute(
                "INSERT INTO tickets (ticket_id, user_id, channel_id, reason, created_at, status, log_file) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (self.ticket_count, user.id, ticket_channel.id, reason, datetime.now().isoformat(), "open", None)
            )
            self.db.commit()
            logger.info(f"Created ticket #{self.ticket_count} for user {user.id}")
            return ticket_channel
        except Exception as e:
            logger.error(f"Failed to create ticket channel: {e}\n{traceback.format_exc()}")
            raise

    async def close_ticket(self, channel: discord.TextChannel, closer: discord.Member, log_text: str = None):
        try:
            user_id = next((k for k, v in self.tickets.items() if v == channel.id), None)
            if user_id is None:
                logger.error(f"No user found for channel {channel.id}")
                return

            try:
                await channel.fetch_message(channel.last_message_id)
            except discord.NotFound:
                logger.warning(f"Channel {channel.id} already deleted or inaccessible")
                return

            user = await self.bot.fetch_user(user_id)
            closure_embed = discord.Embed(
                title="✅ Ticket Closed",
                description=f"Closed by {closer.mention}. Thank you for contacting support!",
                color=0x00ff00
            )
            try:
                await user.send(embed=closure_embed)
            except:
                logger.warning(f"Failed to DM {user.name}")

            self.db.execute(
                "UPDATE tickets SET status = ?, closed_at = ?, log_file = ? WHERE channel_id = ?",
                ("closed", datetime.now().isoformat(), log_text, channel.id)
            )
            self.db.commit()

            if user_id in self.tickets:
                del self.tickets[user_id]

            try:
                await channel.delete()
                logger.info(f"Closed ticket for user {user_id}")
            except discord.NotFound:
                logger.warning(f"Channel {channel.id} already deleted during closure")
        except Exception as e:
            logger.error(f"Close ticket failed: {e}\n{traceback.format_exc()}")
            raise

    async def log_conversation(self, channel: discord.TextChannel):
        try:
            log_content = f"Ticket: {channel.name}\n"
            log_content += f"Created: {discord.utils.format_dt(channel.created_at, 'f')}\n"
            log_content += f"Topic: {channel.topic or 'No topic'}\n"
            log_content += "\nMessages:\n"
            async for message in channel.history(limit=1000, oldest_first=True):
                timestamp = discord.utils.format_dt(message.created_at, 'f')
                content = message.content or "[Embed or Attachment]"
                log_content += f"[{timestamp}] {message.author.name}: {content}\n"

            if self.log_channel_id:
                try:
                    log_channel = self.bot.get_channel(self.log_channel_id)
                    if log_channel is None:
                        log_channel = await self.bot.fetch_channel(self.log_channel_id)
                    if log_channel:
                        embed = discord.Embed(
                            title=f"📜 Ticket Log: {channel.name}",
                            description=f"Log for ticket #{channel.name.split('-')[-1]}",
                            color=0x7289da
                        )
                        if len(log_content) > 1900:
                            log_file = io.StringIO(log_content)
                            discord_file = discord.File(
                                log_file,
                                filename=f"ticket-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
                            )
                            await log_channel.send(embed=embed, file=discord_file)
                            log_file.close()
                        else:
                            embed.description = log_content[:1900]
                            await log_channel.send(embed=embed)
                        logger.info(f"Sent conversation log to ticket-logs channel {self.log_channel_id}")
                        return f"Sent to channel {self.log_channel_id}"
                    else:
                        logger.warning(f"Ticket-logs channel {self.log_channel_id} not found")
                except Exception as e:
                    logger.error(f"Failed to send log to ticket-logs channel: {e}\n{traceback.format_exc()}")

            log_file = f"ticket_logs/ticket-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
            with open(log_file, "w", encoding="utf-8") as f:
                f.write(log_content)
            logger.info(f"Logged conversation to {log_file}")
            return log_file
        except Exception as e:
            logger.error(f"Failed to log conversation: {e}\n{traceback.format_exc()}")
            raise

    async def get_faq_suggestion(self, reason: str):
        if self.model is None or self.faq_embeddings is None:
            logger.warning("AI model or embeddings unavailable, cannot provide FAQ suggestion")
            return None
        try:
            if not reason.strip():
                logger.warning("Empty reason provided for FAQ suggestion")
                return None
            reason_embedding = self.model.encode(reason, convert_to_tensor=True)
            similarities = util.cos_sim(reason_embedding, self.faq_embeddings)[0]
            max_idx = similarities.argmax().item()
            similarity_score = similarities[max_idx].item()
            logger.debug(f"FAQ suggestion: max similarity {similarity_score:.4f} for FAQ index {max_idx} (question: {self.faqs[max_idx]['question']})")
            if similarity_score > 0.5:
                return self.faqs[max_idx]
            return None
        except Exception as e:
            logger.error(f"Error in get_faq_suggestion: {e}\n{traceback.format_exc()}")
            return None

    async def get_or_create_category(self, guild: discord.Guild):
        try:
            category = discord.utils.get(guild.categories, name="Support Tickets")
            if category:
                return category
            overwrites = {
                guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
                guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
            }
            category = await guild.create_category(name="Support Tickets", overwrites=overwrites)
            logger.info("Created Support Tickets category")
            return category
        except Exception as e:
            logger.error(f"Failed to create category: {e}\n{traceback.format_exc()}")
            raise

    async def check_existing_panel(self, channel: discord.TextChannel):
        try:
            async for message in channel.history(limit=100):
                if message.author == channel.guild.me and message.embeds and "Need Help?" in message.embeds[0].title:
                    return message
            return None
        except Exception as e:
            logger.error(f"Failed to check existing panel: {e}\n{traceback.format_exc()}")
            return None

    @commands.hybrid_command(name="ticketpanel")
    @commands.has_permissions(administrator=True)
    async def ticketpanel(self, ctx: commands.Context):
        """Create the ticket creation panel."""
        try:
            existing_panel = await self.check_existing_panel(ctx.channel)
            if existing_panel:
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="A ticket panel already exists in this channel!",
                    color=0xff0000
                ), ephemeral=True)
                return

            embed = discord.Embed(
                title="📩 Need Help?",
                description="Click below to create a support ticket.",
                color=0x7289da
            )
            embed.add_field(
                name="📜 Guidelines",
                value="• Be specific with your issue\n• Stay respectful\n• No spam",
                inline=False
            )
            await ctx.send(embed=embed, view=self.TicketCreationView(self))
            try:
                await ctx.message.delete()
            except:
                logger.debug("Command message deletion skipped")
        except Exception as e:
            logger.error(f"Ticket panel creation failed: {e}\n{traceback.format_exc()}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="Failed to create ticket panel.",
                color=0xff0000
            ), ephemeral=True)

    @commands.hybrid_command(name="ticketstats")
    @commands.has_permissions(administrator=True)
    async def ticketstats(self, ctx: commands.Context):
        """Show ticket statistics."""
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
            open_count = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
            closed_count = cursor.fetchone()[0]
            embed = discord.Embed(
                title="📊 Ticket Statistics",
                description=f"**Open Tickets:** {open_count}\n**Closed Tickets:** {closed_count}\n**Total Tickets:** {open_count + closed_count}",
                color=0x7289da
            )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Ticket stats failed: {e}\n{traceback.format_exc()}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="Failed to retrieve ticket stats.",
                color=0xff0000
            ), ephemeral=True)

    @commands.hybrid_command(name="suggest")
    async def suggest(self, ctx: commands.Context):
        """Suggest an FAQ answer for the ticket."""
        try:
            if ctx.channel.id not in self.tickets.values():
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="Not a ticket channel!",
                    color=0xff0000
                ), ephemeral=True)
                return
            cursor = self.db.cursor()
            cursor.execute("SELECT reason FROM tickets WHERE channel_id = ?", (ctx.channel.id,))
            result = cursor.fetchone()
            if not result:
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="Ticket reason not found.",
                    color=0xff0000
                ), ephemeral=True)
                return
            reason = result[0]
            suggestion = await self.get_faq_suggestion(reason)
            if suggestion:
                embed = discord.Embed(
                    title="🤖 AI Suggestion",
                    description=f"**Question:** {suggestion['question']}\n\n{suggestion['answer']}",
                    color=0x7289da
                )
                if ctx.author.guild_permissions.administrator:
                    embed.add_field(
                        name="Auto-Close?",
                        value="Reply `!close` to accept this suggestion and close the ticket.",
                        inline=False
                    )
                await ctx.send(embed=embed)
            else:
                await ctx.send(embed=discord.Embed(
                    title="⚠ No Suggestion",
                    description="No matching FAQ found. Please provide more details.",
                    color=0xffd700
                ))
        except Exception as e:
            logger.error(f"Suggest command failed: {e}\n{traceback.format_exc()}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="Failed to provide FAQ suggestion.",
                color=0xff0000
            ), ephemeral=True)

    @commands.hybrid_command(name="close")
    @commands.has_permissions(administrator=True)
    async def close(self, ctx: commands.Context):
        """Close a ticket with AI suggestion (admin only)."""
        try:
            if ctx.channel.id not in self.tickets.values():
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="This is not a ticket channel!",
                    color=0xff0000
                ), ephemeral=True)
                return
            confirm_view = self.ConfirmationView(self)
            await ctx.send(embed=discord.Embed(
                title="⚠ Confirm Closure",
                description="Close ticket? Reply 'yes' to log the conversation, 'no' to close without logging.",
                color=0xffd700
            ), view=confirm_view)
            await confirm_view.wait()
            if confirm_view.value:
                def check(m):
                    return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']
                try:
                    response = await self.bot.wait_for('message', check=check, timeout=30.0)
                    log_content = None
                    if response.content.lower() == 'yes':
                        log_content = await self.log_conversation(ctx.channel)
                    await self.close_ticket(ctx.channel, ctx.author, log_content)
                    await ctx.send(embed=discord.Embed(
                        title="✅ Ticket Closed",
                        description="Ticket closed successfully",
                        color=0x00ff00
                    ), ephemeral=True)
                except asyncio.TimeoutError:
                    await ctx.send(embed=discord.Embed(
                        title="❌ Cancelled",
                        description="Ticket closure cancelled due to timeout",
                        color=0x00ff00
                    ), ephemeral=True)
            else:
                await ctx.send(embed=discord.Embed(
                    title="❌ Cancelled",
                    description="Ticket closure cancelled",
                    color=0x00ff00
                ), ephemeral=True)
        except Exception as e:
            logger.error(f"Close command failed: {e}\n{traceback.format_exc()}")
            try:
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="Failed to close ticket.",
                    color=0xff0000
                ), ephemeral=True)
            except discord.NotFound:
                logger.warning("Channel already deleted, cannot send error message")

    @commands.hybrid_command(name="userclose")
    async def userclose(self, ctx: commands.Context):
        """Close a ticket (ticket owner only)."""
        try:
            if ctx.channel.id not in self.tickets.values():
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="This is not a ticket channel!",
                    color=0xff0000
                ), ephemeral=True)
                return
            user_id = next((k for k, v in self.tickets.items() if v == ctx.channel.id), None)
            if user_id is None or ctx.author.id != user_id:
                await ctx.send(embed=discord.Embed(
                    title="❌ Permission Denied",
                    description="Only the ticket owner can use this command.",
                    color=0xff0000
                ), ephemeral=True)
                return
            confirm_view = self.ConfirmationView(self)
            await ctx.send(embed=discord.Embed(
                title="⚠ Confirm Closure",
                description="Are you sure you want to close this ticket? The conversation will be logged.",
                color=0xffd700
            ), view=confirm_view)
            await confirm_view.wait()
            if confirm_view.value:
                log_text = await self.log_conversation(ctx.channel)
                await self.close_ticket(ctx.channel, ctx.author, log_text)
                await ctx.send(embed=discord.Embed(
                    title="✅ Ticket Closed",
                    description="Ticket closed and logged",
                    color=0x00ff00
                ), ephemeral=True)
            else:
                await ctx.send(embed=discord.Embed(
                    title="❌ Cancelled",
                    description="Ticket closure cancelled",
                    color=0x00ff00
                ), ephemeral=True)
        except Exception as e:
            logger.error(f"Userclose command failed: {e}\n{traceback.format_exc()}")
            try:
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="Failed to close ticket.",
                    color=0xff0000
                ), ephemeral=True)
            except discord.NotFound:
                logger.warning("Channel already deleted, cannot send error message")

    @commands.hybrid_command(name="setlogchannel")
    @commands.has_permissions(administrator=True)
    async def setlogchannel(self, ctx: commands.Context, channel: discord.TextChannel):
        """Set the ticket-logs channel (admin only)."""
        try:
            if not channel.permissions_for(ctx.guild.me).send_messages:
                await ctx.send(embed=discord.Embed(
                    title="❌ Error",
                    description="I don't have permission to send messages in that channel.",
                    color=0xff0000
                ), ephemeral=True)
                return
            self.save_log_channel_id(channel.id)
            await ctx.send(embed=discord.Embed(
                title="✅ Success",
                description=f"Ticket logs will now be sent to {channel.mention}.",
                color=0x00ff00
            ), ephemeral=True)
        except Exception as e:
            logger.error(f"Set log channel failed: {e}\n{traceback.format_exc()}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="Failed to set log channel.",
                color=0xff0000
            ), ephemeral=True)

    @commands.hybrid_command(name="ticketdebug")
    @commands.has_permissions(administrator=True)
    async def ticketdebug(self, ctx: commands.Context):
        """Debug ticket system state."""
        try:
            bot_member = ctx.guild.me
            perms = bot_member.guild_permissions
            embed = discord.Embed(
                title="🔍 Ticket System Debug",
                color=0x7289da
            )
            embed.add_field(
                name="Bot Permissions",
                value=f"Manage Channels: {perms.manage_channels}\nSend Messages: {perms.send_messages}\nManage Messages: {perms.manage_messages}",
                inline=False
            )
            embed.add_field(
                name="Active Tickets",
                value=f"{len(self.tickets)} in memory, {self.db.execute('SELECT COUNT(*) FROM tickets WHERE status = ?', ('open',)).fetchone()[0]} in DB",
                inline=False
            )
            staff_role = ctx.guild.get_role(self.staff_role_id) if self.staff_role_id else None
            embed.add_field(
                name="Staff Role",
                value=f"{'Valid' if staff_role else 'Invalid or None'} (ID: {self.staff_role_id or 'None'})",
                inline=False
            )
            embed.add_field(
                name="AI Model Status",
                value=f"{'Loaded' if self.model else 'Failed to load'}, FAQs: {len(self.faqs) if self.faqs else 0}, Embeddings: {'Loaded' if self.faq_embeddings is not None else 'Failed'}",
                inline=False
            )
            embed.add_field(
                name="Log Channel",
                value=f"ID: {self.log_channel_id or 'Not set'}, Accessible: {'Yes' if self.bot.get_channel(self.log_channel_id) else 'No'}",
                inline=False
            )
            try:
                with open("ticket.log", "r", encoding="utf-8") as f:
                    recent_errors = [line for line in f.readlines()[-100:] if "ERROR" in line]
                embed.add_field(
                    name="Recent Errors",
                    value=f"{len(recent_errors)} errors in last 100 log lines\n" + (
                        "\n".join(recent_errors[-3:])[:1000] or "None"
                    ),
                    inline=False
                )
            except:
                embed.add_field(
                    name="Recent Errors",
                    value="Unable to read log file",
                    inline=False
                )
            await ctx.send(embed=embed, ephemeral=True)
        except Exception as e:
            logger.error(f"Ticket debug failed: {e}\n{traceback.format_exc()}")
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description="Failed to retrieve debug information.",
                color=0xff0000
            ), ephemeral=True)

    @commands.Cog.listener()
    async def on_ready(self):
        try:
            cursor = self.db.cursor()
            cursor.execute("SELECT user_id, channel_id FROM tickets WHERE status = 'open'")
            self.tickets = {row[0]: row[1] for row in cursor.fetchall()}
            cursor.execute("SELECT MAX(ticket_id) FROM tickets")
            self.ticket_count = cursor.fetchone()[0] or 0
            logger.info(f"Ticket system ready! Active tickets: {len(self.tickets)}, ticket_count: {self.ticket_count}")
        except Exception as e:
            logger.error(f"On ready failed: {e}\n{traceback.format_exc()}")

async def setup(bot):
    try:
        await bot.add_cog(TicketSystem(bot))
        logger.info("Loaded ticket cog: cogs.ticketsystem")
    except Exception as e:
        logger.error(f"Failed to load ticket cog: {e}\n{traceback.format_exc()}")
        raise e


# working present
# import discord
# from discord.ext import commands
# from discord import ui, TextStyle, ButtonStyle
# from datetime import datetime
# import json
# import sqlite3
# import logging
# import logging.handlers
# from sentence_transformers import SentenceTransformer, util
# import asyncio
# import os
# import io
# import traceback

# # Configure logging with rotation
# logging.basicConfig(
#     level=logging.INFO,
#     format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
#     handlers=[
#         logging.handlers.RotatingFileHandler('ticket.log', maxBytes=10*1024*1024, backupCount=5),
#         logging.StreamHandler()
#     ]
# )
# logger = logging.getLogger(__name__)

# # Default FAQs
# DEFAULT_FAQS = {
#     "faqs": [
#         {
#             "question": "What is the server IP?",
#             "answer": "The server IP is `play.example.com:25565`.",
#             "keywords": ["server ip", "ip address", "connect"]
#         },
#         {
#             "question": "How do I reset my password?",
#             "answer": "Visit example.com/reset and follow the instructions.",
#             "keywords": ["password", "reset", "login"]
#         },
#         {
#             "question": "Why am I lagging?",
#             "answer": "Check your ping with `!ping` or restart your router.",
#             "keywords": ["lag", "ping", "connection"]
#         }
#     ]
# }

# class TicketSystem(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.tickets = {}
#         self.ticket_count = 0
#         self.db = sqlite3.connect("moderation.db")
#         self.setup_db()
#         try:
#             self.model = SentenceTransformer('all-MiniLM-L6-v2')
#             logger.info("SentenceTransformer model loaded successfully")
#         except Exception as e:
#             logger.error(f"Failed to load SentenceTransformer model: {e}")
#             self.model = None
#         self.faqs = self.load_faqs()
#         self.faq_embeddings = self.compute_faq_embeddings()
#         self.staff_role_id = None  # Set to your staff role ID or None for admin-only
#         self.log_channel_id = self.load_log_channel_id()  # Load from config
#         os.makedirs("ticket_logs", exist_ok=True)
#         logger.info("TicketSystem initialized")

#     def setup_db(self):
#         """Initialize ticket tracking in SQLite and handle schema migrations."""
#         try:
#             self.db.execute("""
#                 CREATE TABLE IF NOT EXISTS tickets (
#                     ticket_id INTEGER PRIMARY KEY,
#                     user_id INTEGER,
#                     channel_id INTEGER,
#                     reason TEXT,
#                     created_at TEXT,
#                     closed_at TEXT,
#                     status TEXT,
#                     log_file TEXT
#                 )
#             """)
#             cursor = self.db.cursor()
#             cursor.execute("PRAGMA table_info(tickets)")
#             columns = [info[1] for info in cursor.fetchall()]
#             if 'log_file' not in columns:
#                 logger.info("Adding log_file column to tickets table")
#                 self.db.execute("ALTER TABLE tickets ADD COLUMN log_file TEXT")
#             self.db.commit()
#             cursor.execute("SELECT MAX(ticket_id) FROM tickets")
#             max_id = cursor.fetchone()[0]
#             self.ticket_count = max_id if max_id is not None else 0
#             logger.debug(f"Database setup complete, ticket_count initialized to {self.ticket_count}")
#         except Exception as e:
#             logger.error(f"Database setup failed: {e}\n{traceback.format_exc()}")

#     def load_faqs(self):
#         """Load or create faqs.json."""
#         try:
#             with open("faqs.json", "r") as f:
#                 faqs = json.load(f)
#                 logger.info("Loaded faqs.json")
#                 return faqs.get("faqs", DEFAULT_FAQS["faqs"])
#         except FileNotFoundError:
#             logger.warning("faqs.json not found. Creating default")
#             with open("faqs.json", "w") as f:
#                 json.dump(DEFAULT_FAQS, f, indent=2)
#             return DEFAULT_FAQS["faqs"]
#         except Exception as e:
#             logger.error(f"Error loading faqs: {e}\n{traceback.format_exc()}")
#             return DEFAULT_FAQS["faqs"]

#     def load_log_channel_id(self):
#         """Load log channel ID from config.json."""
#         try:
#             with open("config.json", "r") as f:
#                 config = json.load(f)
#                 log_channel_id = config.get("log_channel_id")
#                 logger.info(f"Loaded log_channel_id: {log_channel_id}")
#                 return log_channel_id
#         except FileNotFoundError:
#             logger.warning("config.json not found. Creating default")
#             with open("config.json", "w") as f:
#                 json.dump({"log_channel_id": None}, f, indent=2)
#             return None
#         except Exception as e:
#             logger.error(f"Error loading config: {e}\n{traceback.format_exc()}")
#             return None

#     def save_log_channel_id(self, channel_id):
#         """Save log channel ID to config.json."""
#         try:
#             config = {"log_channel_id": channel_id}
#             with open("config.json", "w") as f:
#                 json.dump(config, f, indent=2)
#             self.log_channel_id = channel_id
#             logger.info(f"Saved log_channel_id: {channel_id}")
#         except Exception as e:
#             logger.error(f"Error saving log_channel_id: {e}\n{traceback.format_exc()}")

#     def compute_faq_embeddings(self):
#         """Compute embeddings for FAQs."""
#         if self.model is None:
#             logger.warning("SentenceTransformer model not available, skipping FAQ embeddings")
#             return None
#         try:
#             questions = [faq["question"] + " " + " ".join(faq["keywords"]) for faq in self.faqs]
#             if not questions:
#                 logger.error("No FAQ questions available to compute embeddings")
#                 return None
#             embeddings = self.model.encode(questions, batch_size=32, convert_to_tensor=True)
#             logger.debug(f"Computed FAQ embeddings for {len(questions)} FAQs")
#             return embeddings
#         except Exception as e:
#             logger.error(f"Error computing FAQ embeddings: {e}\n{traceback.format_exc()}")
#             return None

#     # =====================
#     # 🎨 INTERFACE COMPONENTS
#     # =====================
#     class TicketCreationView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=None)
#             self.cog = cog

#         @ui.button(label="Create Ticket", style=ButtonStyle.blurple, emoji="📩", custom_id="persistent_create_ticket")
#         async def create_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             try:
#                 logger.debug(f"Create ticket button clicked by {interaction.user.id}")
#                 if interaction.user.id in self.cog.tickets:
#                     channel_id = self.cog.tickets[interaction.user.id]
#                     try:
#                         channel = await interaction.guild.fetch_channel(channel_id)
#                         await interaction.response.send_message(embed=discord.Embed(
#                             title="Error",
#                             description=f"You already have an open ticket: {channel.mention}",
#                             color=0xff0000
#                         ), ephemeral=True)
#                         return
#                     except discord.NotFound:
#                         logger.warning(f"Channel {channel_id} not found for user {interaction.user.id}. Clearing")
#                         del self.cog.tickets[interaction.user.id]
#                         self.cog.db.execute(
#                             "UPDATE tickets SET status = ?, closed_at = ? WHERE channel_id = ?",
#                             ("closed", datetime.now().isoformat(), channel_id)
#                         )
#                         self.cog.db.commit()

#                 modal = self.cog.TicketModal(self.cog)
#                 await interaction.response.send_modal(modal)
#             except Exception as e:
#                 logger.error(f"Ticket creation failed: {e}\n{traceback.format_exc()}")
#                 try:
#                     await interaction.response.send_message(embed=discord.Embed(
#                         title="Error",
#                         description="Failed to process interaction. Please try again.",
#                         color=0xff0000
#                     ), ephemeral=True)
#                 except Exception as e2:
#                     logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

#     class TicketModal(ui.Modal, title="Create Support Ticket"):
#         def __init__(self, cog):
#             super().__init__(timeout=300)
#             self.cog = cog
#             self.reason = ui.TextInput(
#                 label="Describe your issue",
#                 style=TextStyle.short,
#                 placeholder="Enter the reason for your ticket...",
#                 required=True
#             )
#             self.add_item(self.reason)

#         async def on_submit(self, interaction: discord.Interaction):
#             try:
#                 await interaction.response.defer(ephemeral=True)
#                 logger.debug(f"Ticket modal submitted by {interaction.user.id}")
#                 ticket_channel = await self.cog.create_ticket_channel(
#                     interaction.user, interaction.guild, self.reason.value, ""
#                 )
#                 if self.cog.model and self.cog.faq_embeddings is not None:
#                     suggestion = await self.cog.get_faq_suggestion(self.reason.value)
#                     if suggestion:
#                         await ticket_channel.send(embed=discord.Embed(
#                             title="AI Suggestion",
#                             description=f"Possible solution: {suggestion['answer']}\n\nUse `!suggest` for more or `!close` to close.",
#                             color=0x7289da
#                         ))
#                     else:
#                         logger.debug(f"No FAQ suggestion found for reason: {self.reason.value}")
#                 else:
#                     logger.warning("AI model or embeddings unavailable, skipping FAQ suggestion")
#                 await interaction.followup.send(embed=discord.Embed(
#                     title="Ticket Created",
#                     description=f"Your ticket has been created: {ticket_channel.mention}",
#                     color=0x00cc00
#                 ), ephemeral=True)
#             except Exception as e:
#                 logger.error(f"Ticket modal failed: {e}\n{traceback.format_exc()}")
#                 try:
#                     await interaction.followup.send(embed=discord.Embed(
#                         title="Error",
#                         description="Failed to create ticket. Please try again.",
#                         color=0xff0000
#                     ), ephemeral=True)
#                 except Exception as e2:
#                     logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

#     class TicketControlView(ui.View):
#         def __init__(self, cog, ticket_owner_id):
#             super().__init__(timeout=None)
#             self.cog = cog
#             self.ticket_owner_id = ticket_owner_id

#         @ui.button(label="Close Ticket", style=ButtonStyle.red, emoji="🔒", custom_id="persistent_close_ticket")
#         async def close_ticket(self, interaction: discord.Interaction, button: ui.Button):
#             try:
#                 await interaction.response.defer(ephemeral=True)
#                 logger.debug(f"Close ticket button clicked by {interaction.user.id}")
#                 is_admin = interaction.user.guild_permissions.administrator
#                 is_owner = interaction.user.id == self.ticket_owner_id

#                 if not (is_admin or is_owner):
#                     await interaction.followup.send(embed=discord.Embed(
#                         title="Permission Denied",
#                         description="Only staff or the ticket owner can close this ticket",
#                         color=0xff0000
#                     ), ephemeral=True)
#                     return

#                 confirm_view = self.cog.ConfirmationView(self.cog)
#                 await interaction.followup.send(embed=discord.Embed(
#                     title="Confirm Closure",
#                     description="Are you sure you want to close this ticket?",
#                     color=0xffd700
#                 ), view=confirm_view, ephemeral=True)
#                 await confirm_view.wait()

#                 if confirm_view.value:
#                     log_text = await self.cog.log_conversation(interaction.channel)
#                     await interaction.followup.send(embed=discord.Embed(
#                         title="Ticket Closed",
#                         description="Ticket closed and logged",
#                         color=0x00cc00
#                     ), ephemeral=True)
#                     await self.cog.close_ticket(interaction.channel, interaction.user, log_text)
#                 else:
#                     await interaction.followup.send(embed=discord.Embed(
#                         title="Cancelled",
#                         description="Ticket closure cancelled",
#                         color=0x00cc00
#                     ), ephemeral=True)
#             except Exception as e:
#                 logger.error(f"Close ticket failed: {e}\n{traceback.format_exc()}")
#                 if not isinstance(e, discord.errors.HTTPException) or e.code != 10003:
#                     try:
#                         await interaction.followup.send(embed=discord.Embed(
#                             title="Error",
#                             description="Failed to close ticket. Please try again.",
#                             color=0xff0000
#                         ), ephemeral=True)
#                     except Exception as e2:
#                         logger.error(f"Failed to send error message: {e2}\n{traceback.format_exc()}")

#     class ConfirmationView(ui.View):
#         def __init__(self, cog):
#             super().__init__(timeout=30)
#             self.cog = cog
#             self.value = False

#         @ui.button(label="Confirm", style=ButtonStyle.green, emoji="✅")
#         async def confirm(self, interaction: discord.Interaction, button: ui.Button):
#             try:
#                 self.value = True
#                 await interaction.response.defer(ephemeral=True)
#                 self.stop()
#             except Exception as e:
#                 logger.error(f"Confirmation failed: {e}\n{traceback.format_exc()}")

#         @ui.button(label="Cancel", style=ButtonStyle.grey, emoji="🔴")
#         async def cancel(self, interaction: discord.Interaction, button: ui.Button):
#             try:
#                 self.value = False
#                 await interaction.response.defer(ephemeral=True)
#                 self.stop()
#             except Exception as e:
#                 logger.error(f"Cancel failed: {e}\n{traceback.format_exc()}")

#     # =====================
#     # 🛠️ CORE FUNCTIONALITY
#     # =====================
#     async def create_ticket_channel(self, user: discord.User, guild: discord.Guild, reason: str, attachment: str):
#         try:
#             category = await self.get_or_create_category(guild)
#             self.ticket_count += 1

#             staff_role = guild.get_role(self.staff_role_id) if self.staff_role_id else None
#             if not staff_role and self.staff_role_id:
#                 logger.warning(f"Staff role ID {self.staff_role_id} not found. Using admins only")

#             overwrites = {
#                 guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
#                 user: discord.PermissionOverwrite(read_messages=True, send_messages=True),
#                 guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
#             }
#             if staff_role:
#                 overwrites[staff_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)

#             ticket_channel = await category.create_text_channel(
#                 name=f"ticket-{self.ticket_count:04d}",
#                 overwrites=overwrites,
#                 topic=f"{user.name} | {reason[:50]}"
#             )

#             embed = discord.Embed(
#                 title=f"Ticket #{self.ticket_count:04d}",
#                 description=f"**User:** {user.mention}\n**Reason:** {reason}",
#                 color=0x7289da
#             )
#             if attachment:
#                 embed.add_field(name="Attachment", value=attachment, inline=False)
#             embed.add_field(
#                 name="Information",
#                 value=f"Created: {discord.utils.format_dt(datetime.now(), 'f')}\nStatus: 🟢 Open",
#                 inline=False
#             )

#             view = self.TicketControlView(self, user.id)
#             content = f"{user.mention} | {staff_role.mention if staff_role else 'Support Team'}"
#             await ticket_channel.send(content=content, embed=embed, view=view)
#             self.tickets[user.id] = ticket_channel.id

#             self.db.execute(
#                 "INSERT INTO tickets (ticket_id, user_id, channel_id, reason, created_at, status, log_file) VALUES (?, ?, ?, ?, ?, ?, ?)",
#                 (self.ticket_count, user.id, ticket_channel.id, reason, datetime.now().isoformat(), "open", None)
#             )
#             self.db.commit()
#             logger.debug(f"Created ticket #{self.ticket_count} for user {user.id}")
#             return ticket_channel
#         except Exception as e:
#             logger.error(f"Failed to create ticket channel: {e}\n{traceback.format_exc()}")
#             raise

#     async def close_ticket(self, channel: discord.TextChannel, closer: discord.Member, log_text: str = None):
#         try:
#             user_id = next((k for k, v in self.tickets.items() if v == channel.id), None)
#             if user_id is None:
#                 logger.error(f"No user found for channel {channel.id}")
#                 return

#             try:
#                 await channel.fetch_message(channel.last_message_id)
#             except discord.NotFound:
#                 logger.warning(f"Channel {channel.id} already deleted or inaccessible")
#                 return

#             user = await self.bot.fetch_user(user_id)
#             closure_embed = discord.Embed(
#                 title="Ticket Closed",
#                 description=f"Closed by {closer.mention}. Thank you for contacting support!",
#                 color=0x00cc00
#             )
#             try:
#                 await user.send(embed=closure_embed)
#             except:
#                 logger.warning(f"Failed to DM {user.name}")

#             self.db.execute(
#                 "UPDATE tickets SET status = ?, closed_at = ?, log_file = ? WHERE channel_id = ?",
#                 ("closed", datetime.now().isoformat(), log_text, channel.id)
#             )
#             self.db.commit()

#             if user_id in self.tickets:
#                 del self.tickets[user_id]

#             try:
#                 await channel.delete()
#                 logger.debug(f"Closed ticket for user {user_id}")
#             except discord.NotFound:
#                 logger.warning(f"Channel {channel.id} already deleted during closure")
#         except Exception as e:
#             logger.error(f"Close ticket failed: {e}\n{traceback.format_exc()}")
#             raise

#     async def log_conversation(self, channel: discord.TextChannel):
#         try:
#             log_content = f"Ticket: {channel.name}\n"
#             log_content += f"Created: {discord.utils.format_dt(channel.created_at, 'f')}\n"
#             log_content += f"Topic: {channel.topic or 'No topic'}\n"
#             log_content += "\nMessages:\n"
#             async for message in channel.history(limit=1000, oldest_first=True):
#                 timestamp = discord.utils.format_dt(message.created_at, 'f')
#                 content = message.content or "[Embed or Attachment]"
#                 log_content += f"[{timestamp}] {message.author.name}: {content}\n"

#             if self.log_channel_id:
#                 try:
#                     log_channel = self.bot.get_channel(self.log_channel_id)
#                     if log_channel is None:
#                         log_channel = await self.bot.fetch_channel(self.log_channel_id)
#                     if log_channel:
#                         embed = discord.Embed(
#                             title=f"Ticket Log: {channel.name}",
#                             description=f"Log for ticket #{channel.name.split('-')[-1]}",
#                             color=0x7289da
#                         )
#                         if len(log_content) > 1900:
#                             log_file = io.StringIO(log_content)
#                             discord_file = discord.File(
#                                 log_file,
#                                 filename=f"ticket-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
#                             )
#                             await log_channel.send(embed=embed, file=discord_file)
#                             log_file.close()
#                         else:
#                             embed.description = log_content[:1900]
#                             await log_channel.send(embed=embed)
#                         logger.info(f"Sent conversation log to ticket-logs channel {self.log_channel_id}")
#                         return f"Sent to channel {self.log_channel_id}"
#                     else:
#                         logger.warning(f"Ticket-logs channel {self.log_channel_id} not found")
#                 except Exception as e:
#                     logger.error(f"Failed to send log to ticket-logs channel: {e}\n{traceback.format_exc()}")

#             log_file = f"ticket_logs/ticket-{channel.name}-{datetime.now().strftime('%Y%m%d-%H%M%S')}.txt"
#             with open(log_file, "w", encoding="utf-8") as f:
#                 f.write(log_content)
#             logger.info(f"Logged conversation to {log_file}")
#             return log_file
#         except Exception as e:
#             logger.error(f"Failed to log conversation: {e}\n{traceback.format_exc()}")
#             raise

#     async def get_faq_suggestion(self, reason: str):
#         if self.model is None or self.faq_embeddings is None:
#             logger.warning("AI model or embeddings unavailable, cannot provide FAQ suggestion")
#             return None
#         try:
#             if not reason.strip():
#                 logger.warning("Empty reason provided for FAQ suggestion")
#                 return None
#             reason_embedding = self.model.encode(reason, convert_to_tensor=True)
#             similarities = util.cos_sim(reason_embedding, self.faq_embeddings)[0]
#             max_idx = similarities.argmax().item()
#             similarity_score = similarities[max_idx].item()
#             logger.debug(f"FAQ suggestion: max similarity {similarity_score:.4f} for FAQ index {max_idx} (question: {self.faqs[max_idx]['question']})")
#             if similarity_score > 0.5:
#                 return self.faqs[max_idx]
#             return None
#         except Exception as e:
#             logger.error(f"Error in get_faq_suggestion: {e}\n{traceback.format_exc()}")
#             return None

#     # =====================
#     # ⚙️ UTILITIES
#     # =====================
#     async def get_or_create_category(self, guild: discord.Guild):
#         try:
#             category = discord.utils.get(guild.categories, name="Support Tickets")
#             if category:
#                 return category
#             overwrites = {
#                 guild.default_role: discord.PermissionOverwrite(read_messages=False, send_messages=False),
#                 guild.me: discord.PermissionOverwrite(read_messages=True, send_messages=True, manage_channels=True)
#             }
#             category = await guild.create_category(name="Support Tickets", overwrites=overwrites)
#             logger.debug("Created Support Tickets category")
#             return category
#         except Exception as e:
#             logger.error(f"Failed to create category: {e}\n{traceback.format_exc()}")
#             raise

#     async def check_existing_panel(self, channel: discord.TextChannel):
#         try:
#             async for message in channel.history(limit=100):
#                 if message.author == channel.guild.me and message.embeds and "Need Help?" in message.embeds[0].title:
#                     return message
#             return None
#         except Exception as e:
#             logger.error(f"Failed to check existing panel: {e}\n{traceback.format_exc()}")
#             return None

#     # =====================
#     # 💻 COMMANDS
#     # =====================
#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def ticketpanel(self, ctx: commands.Context):
#         """Create the ticket creation panel."""
#         try:
#             existing_panel = await self.check_existing_panel(ctx.channel)
#             if existing_panel:
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="A ticket panel already exists in this channel!",
#                     color=0xff0000
#                 ), delete_after=10)
#                 return

#             embed = discord.Embed(
#                 title="Need Help?",
#                 description="Click below to create a support ticket.",
#                 color=0x7289da
#             )
#             embed.add_field(
#                 name="Guidelines",
#                 value="• Be specific with your issue\n• Stay respectful\n• No spam",
#                 inline=False
#             )
#             await ctx.send(embed=embed, view=self.TicketCreationView(self))
#             try:
#                 await ctx.message.delete()
#             except:
#                 logger.debug("Command message deletion skipped")
#         except Exception as e:
#             logger.error(f"Ticket panel creation failed: {e}\n{traceback.format_exc()}")
#             await ctx.send(embed=discord.Embed(
#                 title="Error",
#                 description="Failed to create ticket panel.",
#                 color=0xff0000
#             ), delete_after=10)

#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def ticketstats(self, ctx: commands.Context):
#         """Show ticket statistics."""
#         try:
#             cursor = self.db.cursor()
#             cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'open'")
#             open_count = cursor.fetchone()[0]
#             cursor.execute("SELECT COUNT(*) FROM tickets WHERE status = 'closed'")
#             closed_count = cursor.fetchone()[0]
#             embed = discord.Embed(
#                 title="📊 Ticket Statistics",
#                 description=f"**Open Tickets:** {open_count}\n**Closed Tickets:** {closed_count}\n**Total Tickets:** {open_count + closed_count}",
#                 color=0x7289da
#             )
#             await ctx.send(embed=embed, delete_after=30)
#         except Exception as e:
#             logger.error(f"Ticket stats failed: {e}\n{traceback.format_exc()}")
#             await ctx.send(embed=discord.Embed(
#                 title="Error",
#                 description="Failed to retrieve ticket stats.",
#                 color=0xff0000
#             ), delete_after=10)

#     @commands.command()
#     async def suggest(self, ctx: commands.Context):
#         """Suggest an FAQ answer for the ticket."""
#         try:
#             if ctx.channel.id not in self.tickets.values():
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="Not a ticket channel!",
#                     color=0xff0000
#                 ), delete_after=30)
#                 return
#             cursor = self.db.cursor()
#             cursor.execute("SELECT reason FROM tickets WHERE channel_id = ?", (ctx.channel.id,))
#             result = cursor.fetchone()
#             if not result:
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="Ticket reason not found.",
#                     color=0xff0000
#                 ), delete_after=30)
#                 return
#             reason = result[0]
#             suggestion = await self.get_faq_suggestion(reason)
#             if suggestion:
#                 embed = discord.Embed(
#                     title="AI Suggestion",
#                     description=f"**Question:** {suggestion['question']}\n\n{suggestion['answer']}",
#                     color=0x7289da
#                 )
#                 if ctx.author.guild_permissions.administrator:
#                     embed.add_field(
#                         name="Auto-Close?",
#                         value="Reply `!close` to accept this suggestion and close the ticket.",
#                         inline=False
#                     )
#                 await ctx.send(embed=embed)
#             else:
#                 await ctx.send(embed=discord.Embed(
#                     title="No Suggestion",
#                     description="No matching FAQ found. Please provide more details.",
#                     color=0xffd700
#                 ))
#         except Exception as e:
#             logger.error(f"Suggest command failed: {e}\n{traceback.format_exc()}")
#             await ctx.send(embed=discord.Embed(
#                 title="Error",
#                 description="Failed to provide FAQ suggestion.",
#                 color=0xff0000
#             ), delete_after=30)

#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def close(self, ctx: commands.Context):
#         """Close a ticket with AI suggestion (admin only)."""
#         try:
#             if ctx.channel.id not in self.tickets.values():
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="This is not a ticket channel!",
#                     color=0xff0000
#                 ), delete_after=10)
#                 return
#             confirm_view = self.ConfirmationView(self)
#             await ctx.send(embed=discord.Embed(
#                 title="Confirm Closure",
#                 description="Close ticket? Reply 'yes' to log the conversation, 'no' to close without logging.",
#                 color=0xffd700
#             ), view=confirm_view)
#             await confirm_view.wait()
#             if confirm_view.value:
#                 def check(m):
#                     return m.author == ctx.author and m.channel == ctx.channel and m.content.lower() in ['yes', 'no']
#                 try:
#                     response = await self.bot.wait_for('message', check=check, timeout=30.0)
#                     log_content = None
#                     if response.content.lower() == 'yes':
#                         log_content = await self.log_conversation(ctx.channel)
#                     await self.close_ticket(ctx.channel, ctx.author, log_content)
#                     await ctx.send(embed=discord.Embed(
#                         title="Ticket Closed",
#                         description="Ticket closed successfully",
#                         color=0x00cc00
#                     ), delete_after=10)
#                 except asyncio.TimeoutError:
#                     await ctx.send(embed=discord.Embed(
#                         title="Cancelled",
#                         description="Ticket closure cancelled due to timeout",
#                         color=0x00cc00
#                     ), delete_after=10)
#             else:
#                 await ctx.send(embed=discord.Embed(
#                     title="Cancelled",
#                     description="Ticket closure cancelled",
#                     color=0x00cc00
#                 ), delete_after=10)
#         except Exception as e:
#             logger.error(f"Close command failed: {e}\n{traceback.format_exc()}")
#             try:
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="Failed to close ticket.",
#                     color=0xff0000
#                 ), delete_after=10)
#             except discord.NotFound:
#                 logger.warning("Channel already deleted, cannot send error message")

#     @commands.command()
#     async def userclose(self, ctx: commands.Context):
#         """Close a ticket (ticket owner only)."""
#         try:
#             if ctx.channel.id not in self.tickets.values():
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="This is not a ticket channel!",
#                     color=0xff0000
#                 ), delete_after=10)
#                 return
#             user_id = next((k for k, v in self.tickets.items() if v == ctx.channel.id), None)
#             if user_id is None or ctx.author.id != user_id:
#                 await ctx.send(embed=discord.Embed(
#                     title="Permission Denied",
#                     description="Only the ticket owner can use this command.",
#                     color=0xff0000
#                 ), delete_after=10)
#                 return
#             confirm_view = self.ConfirmationView(self)
#             await ctx.send(embed=discord.Embed(
#                 title="Confirm Closure",
#                 description="Are you sure you want to close this ticket? The conversation will be logged.",
#                 color=0xffd700
#             ), view=confirm_view)
#             await confirm_view.wait()
#             if confirm_view.value:
#                 log_text = await self.log_conversation(ctx.channel)
#                 await self.close_ticket(ctx.channel, ctx.author, log_text)
#                 await ctx.send(embed=discord.Embed(
#                     title="Ticket Closed",
#                     description="Ticket closed and logged",
#                     color=0x00cc00
#                 ), delete_after=10)
#             else:
#                 await ctx.send(embed=discord.Embed(
#                     title="Cancelled",
#                     description="Ticket closure cancelled",
#                     color=0x00cc00
#                 ), delete_after=10)
#         except Exception as e:
#             logger.error(f"Userclose command failed: {e}\n{traceback.format_exc()}")
#             try:
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="Failed to close ticket.",
#                     color=0xff0000
#                 ), delete_after=10)
#             except discord.NotFound:
#                 logger.warning("Channel already deleted, cannot send error message")

#     @commands.command()
#     @commands.is_owner()
#     async def setlogchannel(self, ctx: commands.Context, channel: discord.TextChannel):
#         """Set the ticket-logs channel (server owner only)."""
#         try:
#             if not channel.permissions_for(ctx.guild.me).send_messages:
#                 await ctx.send(embed=discord.Embed(
#                     title="Error",
#                     description="I don't have permission to send messages in that channel.",
#                     color=0xff0000
#                 ), delete_after=10)
#                 return
#             self.save_log_channel_id(channel.id)
#             await ctx.send(embed=discord.Embed(
#                 title="Success",
#                 description=f"Ticket logs will now be sent to {channel.mention}.",
#                 color=0x00cc00
#             ), delete_after=10)
#         except Exception as e:
#             logger.error(f"Set log channel failed: {e}\n{traceback.format_exc()}")
#             await ctx.send(embed=discord.Embed(
#                 title="Error",
#                 description="Failed to set log channel.",
#                 color=0xff0000
#             ), delete_after=10)

#     @commands.command()
#     @commands.has_permissions(administrator=True)
#     async def ticketdebug(self, ctx: commands.Context):
#         """Debug ticket system state."""
#         try:
#             bot_member = ctx.guild.me
#             perms = bot_member.guild_permissions
#             embed = discord.Embed(
#                 title="Ticket System Debug",
#                 color=0x7289da
#             )
#             embed.add_field(
#                 name="Bot Permissions",
#                 value=f"Manage Channels: {perms.manage_channels}\nSend Messages: {perms.send_messages}\nManage Messages: {perms.manage_messages}",
#                 inline=False
#             )
#             embed.add_field(
#                 name="Active Tickets",
#                 value=f"{len(self.tickets)} in memory, {self.db.execute('SELECT COUNT(*) FROM tickets WHERE status = ?', ('open',)).fetchone()[0]} in DB",
#                 inline=False
#             )
#             staff_role = ctx.guild.get_role(self.staff_role_id) if self.staff_role_id else None
#             embed.add_field(
#                 name="Staff Role",
#                 value=f"{'Valid' if staff_role else 'Invalid or None'} (ID: {self.staff_role_id or 'None'})",
#                 inline=False
#             )
#             embed.add_field(
#                 name="AI Model Status",
#                 value=f"{'Loaded' if self.model else 'Failed to load'}, FAQs: {len(self.faqs) if self.faqs else 0}, Embeddings: {'Loaded' if self.faq_embeddings is not None else 'Failed'}",
#                 inline=False
#             )
#             embed.add_field(
#                 name="Log Channel",
#                 value=f"ID: {self.log_channel_id or 'Not set'}, Accessible: {'Yes' if self.bot.get_channel(self.log_channel_id) else 'No'}",
#                 inline=False
#             )
#             try:
#                 with open("ticket.log", "r", encoding="utf-8") as f:
#                     recent_errors = [line for line in f.readlines()[-100:] if "ERROR" in line]
#                 embed.add_field(
#                     name="Recent Errors",
#                     value=f"{len(recent_errors)} errors in last 100 log lines\n" + (
#                         "\n".join(recent_errors[-3:])[:1000] or "None"
#                     ),
#                     inline=False
#                 )
#             except:
#                 embed.add_field(
#                     name="Recent Errors",
#                     value="Unable to read log file",
#                     inline=False
#                 )
#             await ctx.send(embed=embed, delete_after=30)
#         except Exception as e:
#             logger.error(f"Ticket debug failed: {e}\n{traceback.format_exc()}")
#             await ctx.send(embed=discord.Embed(
#                 title="Error",
#                 description="Failed to retrieve debug information.",
#                 color=0xff0000
#             ), delete_after=10)

#     @commands.Cog.listener()
#     async def on_ready(self):
#         try:
#             cursor = self.db.cursor()
#             cursor.execute("SELECT user_id, channel_id FROM tickets WHERE status = 'open'")
#             self.tickets = {row[0]: row[1] for row in cursor.fetchall()}
#             cursor.execute("SELECT MAX(ticket_id) FROM tickets")
#             self.ticket_count = cursor.fetchone()[0] or 0
#             logger.info(f"Ticket system ready! Active tickets: {len(self.tickets)}, ticket_count: {self.ticket_count}")
#         except Exception as e:
#             logger.error(f"On ready failed: {e}\n{traceback.format_exc()}")

# async def setup(bot):
#     try:
#         await bot.add_cog(TicketSystem(bot))
#         logger.info("Loaded ticket cog: cogs.ticketsystem")
#     except Exception as e:
#         logger.error(f"Failed to load ticket cog: {e}\n{traceback.format_exc()}")
#         raise e

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