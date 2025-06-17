# import discord
# from discord.ext import commands

# class Roles(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def addrole(self, ctx, member: discord.Member, *, role_name):
#         """Assign a role to a user."""
#         role = discord.utils.get(ctx.guild.roles, name=role_name)
#         if not role:
#             await ctx.send("⚠️ Role not found.")
#             return
#         await member.add_roles(role)
#         await ctx.send(f"✅ {member.name} has been given the role **{role_name}**.")

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def removerole(self, ctx, member: discord.Member, *, role_name):
#         """Remove a role from a user."""
#         role = discord.utils.get(ctx.guild.roles, name=role_name)
#         if not role:
#             await ctx.send("⚠️ Role not found.")
#             return
#         await member.remove_roles(role)
#         await ctx.send(f"❌ {member.name} has been removed from the role **{role_name}**.")

# async def setup(bot):
#     await bot.add_cog(Roles(bot))

#### working cool

# import discord
# from discord.ext import commands
# from discord import ui, SelectOption
# from datetime import datetime

# class RoleView(ui.View):
#     def __init__(self, role_options, max_roles=5):
#         super().__init__(timeout=120)
#         self.add_item(RoleDropdown(role_options, max_roles))

# class RoleDropdown(ui.Select):
#     def __init__(self, role_options, max_roles):
#         options = [SelectOption(label=role.name, value=str(role.id)) for role in role_options]
#         super().__init__(
#             placeholder="Select roles to add/remove...",
#             min_values=0,
#             max_values=max_roles,
#             options=options,
#             custom_id="role_selector"
#         )

#     async def callback(self, interaction: discord.Interaction):
#         selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.values]
#         current_roles = set(interaction.user.roles)
        
#         added = []
#         removed = []
        
#         for role in selected_roles:
#             if role not in current_roles:
#                 await interaction.user.add_roles(role)
#                 added.append(role.name)
        
#         for role in current_roles - set(selected_roles):
#             if role in self.options and role != interaction.guild.default_role:
#                 await interaction.user.remove_roles(role)
#                 removed.append(role.name)
        
#         embed = discord.Embed(color=0x2b2d31)
#         if added:
#             embed.add_field(name="Added Roles", value="\n".join(added), inline=False)
#         if removed:
#             embed.add_field(name="Removed Roles", value="\n".join(removed), inline=False)
        
#         await interaction.response.send_message(embed=embed, ephemeral=True)

# class AdvancedRoles(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot
#         self.role_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)
#         self.allowed_roles = {}  # Store allowed roles per guild

#     async def send_role_embed(self, ctx, title, description, color=0x2b2d31):
#         embed = discord.Embed(
#             title=title,
#             description=description,
#             color=color,
#             timestamp=datetime.now()
#         )
#         embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
#         await ctx.send(embed=embed)

#     @commands.Cog.listener()
#     async def on_ready(self):
#         # Initialize allowed roles for each guild (you can load from database)
#         for guild in self.bot.guilds:
#             self.allowed_roles[guild.id] = [role.id for role in guild.roles if not role.managed and role < guild.me.top_role]

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def rolemenu(self, ctx, *, category: str = None):
#         """Create an interactive role selection menu"""
#         if category:
#             roles = [role for role in ctx.guild.roles 
#                     if role.name.lower().startswith(category.lower()) 
#                     and role.id in self.allowed_roles.get(ctx.guild.id, [])]
#         else:
#             roles = [ctx.guild.get_role(rid) for rid in self.allowed_roles.get(ctx.guild.id, [])]
        
#         if not roles:
#             return await self.send_role_embed(ctx, "⚠️ No Roles Available", 
#                                             "No self-assignable roles found.", 0xffcc4d)
        
#         view = RoleView(roles[:25], max_roles=5)  # Discord's select menu limit
#         embed = discord.Embed(
#             title="🔮 Role Selector",
#             description="Choose your roles from the dropdown below!\n"
#                        "You can select multiple roles at once.",
#             color=0x7289da
#         )
#         if category:
#             embed.set_author(name=f"Category: {category.title()}")
#         embed.set_thumbnail(url=ctx.guild.icon.url)
#         await ctx.send(embed=embed, view=view)

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def addrole(self, ctx, member: discord.Member, *, role_name):
#         """Assign a role to a user (Advanced)"""
#         bucket = self.role_cooldown.get_bucket(ctx.message)
#         if bucket.update_rate_limit():
#             return await self.send_role_embed(ctx, "⏳ Cooldown Active",
#                                             "Please wait before using this command again.", 0xffcc4d)
        
#         try:
#             role = discord.utils.get(ctx.guild.roles, name=role_name)
#             if not role:
#                 return await self.send_role_embed(ctx, "⚠️ Role Not Found",
#                                                 f"Couldn't find role '{role_name}'", 0xffcc4d)
            
#             if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
#                 return await self.send_role_embed(ctx, "⛔ Permission Denied",
#                                                 "You can't assign roles equal to or higher than yours.", 0xdd2e44)
            
#             await member.add_roles(role)
#             embed = discord.Embed(
#                 title="✅ Role Added",
#                 description=f"{member.mention} has received the **{role.name}** role!",
#                 color=0x77b255
#             )
#             embed.add_field(name="Assigned By", value=ctx.author.mention)
#             await ctx.send(embed=embed)
        
#         except discord.Forbidden:
#             await self.send_role_embed(ctx, "❌ Missing Permissions",
#                                       "I don't have permission to assign roles!", 0xdd2e44)

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def removerole(self, ctx, member: discord.Member, *, role_name):
#         """Remove a role from a user (Advanced)"""
#         try:
#             role = discord.utils.get(ctx.guild.roles, name=role_name)
#             if not role:
#                 return await self.send_role_embed(ctx, "⚠️ Role Not Found",
#                                                 f"Couldn't find role '{role_name}'", 0xffcc4d)
            
#             await member.remove_roles(role)
#             embed = discord.Embed(
#                 title="❌ Role Removed",
#                 description=f"{member.mention} has lost the **{role.name}** role!",
#                 color=0xdd2e44
#             )
#             embed.add_field(name="Removed By", value=ctx.author.mention)
#             await ctx.send(embed=embed)
        
#         except discord.Forbidden:
#             await self.send_role_embed(ctx, "❌ Missing Permissions",
#                                       "I don't have permission to remove roles!", 0xdd2e44)

#     @commands.Cog.listener()
#     async def on_member_join(self, member):
#         """Auto-role on member join"""
#         autorole_id = self.allowed_roles.get(member.guild.id, [{}])[0]  # Get first allowed role
#         if autorole_id:
#             role = member.guild.get_role(autorole_id)
#             await member.add_roles(role)

#     @commands.command()
#     @commands.has_permissions(manage_roles=True)
#     async def roleinfo(self, ctx, *, role: discord.Role):
#         """Get detailed information about a role"""
#         embed = discord.Embed(title=f"📚 Role Info: {role.name}", color=role.color)
#         embed.add_field(name="Members", value=len(role.members))
#         embed.add_field(name="Color", value=str(role.color).upper())
#         embed.add_field(name="Position", value=role.position)
#         embed.add_field(name="Created At", value=role.created_at.strftime("%b %d, %Y"))
#         embed.add_field(name="Mentionable", value=role.mentionable)
#         embed.add_field(name="Hoisted", value=role.hoist)
#         embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{str(role.color).strip('#')}/400x100")
#         await ctx.send(embed=embed)

# async def setup(bot):
#     await bot.add_cog(AdvancedRoles(bot))

import discord
from discord.ext import commands
from discord import ui, SelectOption, ButtonStyle, app_commands
import json
import os
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('roles.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Components
class RoleSelectView(ui.View):
    def __init__(self, target_user: discord.Member, action: str):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.action = action
        self.add_item(RoleSelectDropdown(action))

class RoleSelectDropdown(ui.Select):
    def __init__(self, action: str):
        options = []  # Populated dynamically
        super().__init__(
            placeholder=f"Select roles to {action}...",
            min_values=0,
            max_values=25,
            options=options,
            custom_id=f"role_select_{action}"
        )
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.values]
            selected_roles = [role for role in selected_roles if role]  # Filter None
            if not selected_roles:
                await interaction.followup.send(embed=discord.Embed(
                    title="❌ No Valid Roles",
                    description="Selected roles are invalid!",
                    color=0xff0000
                ), ephemeral=True)
                return

            current_roles = self.view.target_user.roles
            if self.action == "add":
                new_roles = list(set(current_roles) | set(selected_roles))
                action_text = "added to"
            else:
                new_roles = list(set(current_roles) - set(selected_roles))
                action_text = "removed from"
            
            await self.view.target_user.edit(roles=new_roles)
            
            embed = discord.Embed(
                title="✅ Roles Updated",
                description=f"{len(selected_roles)} roles {action_text} {self.view.target_user.mention}",
                color=0x00ff00 if self.action == "add" else 0xff0000
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.debug(f"Roles {action_text} {self.view.target_user.id}")
            
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ Error",
                description=f"Error: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Role select failed: {e}")

class RoleCreationWizard(ui.Modal):
    def __init__(self):
        super().__init__(title="🔧 Role Creation Wizard", timeout=600)
        self.name = ui.TextInput(label="Role Name", style=discord.TextStyle.short)
        self.color = ui.TextInput(label="HEX Color", placeholder="#RRGGBB", required=False)
        self.permissions = ui.TextInput(
            label="Permissions (comma separated)",
            placeholder="manage_messages, kick_members, ...",
            required=False,
            style=discord.TextStyle.paragraph
        )
        self.add_item(self.name)
        self.add_item(self.color)
        self.add_item(self.permissions)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            perms = discord.Permissions()
            for perm in [p.strip() for p in (self.permissions.value or "").split(",") if p.strip()]:
                if hasattr(perms, perm):
                    setattr(perms, perm, True)
            
            role = await interaction.guild.create_role(
                name=str(self.name),
                color=discord.Color.from_str(self.color.value) if self.color.value else discord.Color.default(),
                permissions=perms,
                reason=f"Created by {interaction.user}"
            )
            
            await role.edit(position=interaction.guild.me.top_role.position-1)
            
            embed = discord.Embed(
                title="✅ Role Created",
                description=f"{role.mention} created successfully!",
                color=role.color
            )
            await interaction.followup.send(embed=embed, ephemeral=True)
            logger.info(f"Role {role.name} created by {interaction.user.id}")
            
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ Error",
                description=f"Error: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Role creation failed: {e}")

class ReactionRoleSetupModal(ui.Modal, title="🎭 Reaction Role Setup"):
    def __init__(self, role: discord.Role):
        super().__init__(timeout=600)
        self.role = role
        self.message = ui.TextInput(
            label="Message Content (for new message)",
            placeholder="React to get the role!",
            style=discord.TextStyle.paragraph,
            required=False
        )
        self.message_id = ui.TextInput(
            label="Message ID (for existing message)",
            placeholder="Enter message ID or leave blank",
            style=discord.TextStyle.short,
            required=False
        )
        self.emoji = ui.TextInput(
            label="Emoji",
            placeholder="✅ or custom emoji name",
            max_length=100,
            required=True
        )
        self.add_item(self.message)
        self.add_item(self.message_id)
        self.add_item(self.emoji)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            await interaction.response.defer(ephemeral=True)
            emoji = self.emoji.value
            # Validate emoji
            if not (len(emoji) == 1 or emoji.startswith("<:") or emoji.isdigit()):
                await interaction.followup.send(embed=discord.Embed(
                    title="❌ Invalid Emoji",
                    description="Use a standard emoji (e.g., ✅) or custom emoji (e.g., <:name:ID>)",
                    color=0xff0000
                ), ephemeral=True)
                return

            message = None
            if self.message_id.value:
                # Use existing message
                try:
                    message_id = int(self.message_id.value)
                    channel = interaction.channel
                    message = await channel.fetch_message(message_id)
                except (ValueError, discord.NotFound):
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Invalid Message ID",
                        description="Message not found or invalid ID!",
                        color=0xff0000
                    ), ephemeral=True)
                    logger.error(f"Invalid message ID {self.message_id.value} by {interaction.user.id}")
                    return
                except discord.Forbidden:
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Permission Error",
                        description="Cannot access the message!",
                        color=0xff0000
                    ), ephemeral=True)
                    logger.error(f"Permission error accessing message {self.message_id.value}")
                    return
            else:
                # Create new message
                if not self.message.value:
                    await interaction.followup.send(embed=discord.Embed(
                        title="❌ Missing Message",
                        description="Provide a message content or message ID!",
                        color=0xff0000
                    ), ephemeral=True)
                    return
                embed = discord.Embed(
                    title="🎭 Reaction Role",
                    description=str(self.message),
                    color=self.role.color
                )
                message = await interaction.channel.send(embed=embed)

            # Add reaction
            try:
                await message.add_reaction(emoji)
            except:
                await interaction.followup.send(embed=discord.Embed(
                    title="❌ Invalid Emoji",
                    description="Could not add emoji to message!",
                    color=0xff0000
                ), ephemeral=True)
                if not self.message_id.value:  # Delete new message if created
                    await message.delete()
                return
            
            # Save to reaction_roles.json
            data = load_reaction_roles()
            if str(interaction.guild.id) not in data:
                data[str(interaction.guild.id)] = []
            data[str(interaction.guild.id)].append({
                "message_id": message.id,
                "channel_id": message.channel.id,
                "emoji": emoji,
                "role_id": self.role.id
            })
            save_reaction_roles(data)
            
            await interaction.followup.send(embed=discord.Embed(
                title="✅ Reaction Role Set",
                description=f"Users reacting with {emoji} will get {self.role.mention} on message ID {message.id}",
                color=0x00ff00
            ), ephemeral=True)
            logger.info(f"Reaction role set for {self.role.name} by {interaction.user.id} on message {message.id}")
        
        except Exception as e:
            await interaction.followup.send(embed=discord.Embed(
                title="❌ Error",
                description=f"Error: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Reaction role setup failed: {e}")

class ReactionRoleSelectView(ui.View):
    def __init__(self):
        super().__init__(timeout=60)
        self.add_item(ReactionRoleSelectDropdown())

class ReactionRoleSelectDropdown(ui.Select):
    def __init__(self):
        super().__init__(
            placeholder="Select a role for reaction...",
            min_values=1,
            max_values=1,
            options=[],
            custom_id="reaction_role_select"
        )

    async def callback(self, interaction: discord.Interaction):
        try:
            role_id = int(self.values[0])
            role = interaction.guild.get_role(role_id)
            if not role:
                await interaction.response.send_message(embed=discord.Embed(
                    title="❌ Invalid Role",
                    description="Selected role no longer exists!",
                    color=0xff0000
                ), ephemeral=True)
                logger.error(f"Invalid role ID {role_id} selected by {interaction.user.id}")
                return
            modal = ReactionRoleSetupModal(role)
            await interaction.response.send_modal(modal)
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ Error",
                description=f"Error: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Reaction role select failed: {e}")

# Utility functions
def load_reaction_roles():
    try:
        with open("reaction_roles.json", "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except Exception as e:
        logger.error(f"Error loading reaction_roles.json: {e}")
        return {}

def save_reaction_roles(data):
    try:
        with open("reaction_roles.json", "w") as f:
            json.dump(data, f, indent=2)
        logger.debug("Saved reaction_roles.json")
    except Exception as e:
        logger.error(f"Error saving reaction_roles.json: {e}")

class AdvancedRoleSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("AdvancedRoleSystem initialized")

    @commands.hybrid_command(name="addrole")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def add_role(self, ctx: commands.Context, member: discord.Member):
        """Add roles to a member"""
        available_roles = [
            role for role in ctx.guild.roles 
            if role < ctx.guild.me.top_role and role not in member.roles and not role.managed and role != ctx.guild.default_role
        ]
        
        if not available_roles:
            await ctx.send(embed=discord.Embed(
                title="❌ No Roles Available",
                description="No roles can be added to this member!",
                color=0xff0000
            ), ephemeral=True)
            return
        
        view = RoleSelectView(member, "add")
        view.children[0].options = [
            SelectOption(label=role.name, value=str(role.id)) for role in available_roles[:25]
        ]
        await ctx.send(
            f"Select roles to add to {member.mention}",
            view=view,
            ephemeral=True
        )
        logger.debug(f"Add role view sent for {member.id}")

    @commands.hybrid_command(name="removerole")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def remove_role(self, ctx: commands.Context, member: discord.Member):
        """Remove roles from a member"""
        removable_roles = [
            role for role in member.roles 
            if role < ctx.guild.me.top_role and not role.managed and role != ctx.guild.default_role
        ]
        
        if not removable_roles:
            await ctx.send(embed=discord.Embed(
                title="❌ No Roles Available",
                description="No roles can be removed from this member!",
                color=0xff0000
            ), ephemeral=True)
            return
        
        view = RoleSelectView(member, "remove")
        view.children[0].options = [
            SelectOption(label=role.name, value=str(role.id)) for role in removable_roles[:25]
        ]
        await ctx.send(
            f"Select roles to remove from {member.mention}",
            view=view,
            ephemeral=True
        )
        logger.debug(f"Remove role view sent for {member.id}")

    @commands.hybrid_command(name="roleinfo")
    async def role_info(self, ctx: commands.Context, role: discord.Role):
        """Get detailed role information"""
        embed = discord.Embed(title=f"📊 Role Analytics: {role.name}", color=role.color)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Color", value=str(role.color).upper(), inline=True)
        embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        
        perms = "\n".join([perm[0].replace('_', ' ').title() for perm in role.permissions if perm[1]])
        embed.add_field(name="Key Permissions", value=perms or "No special permissions", inline=False)
        
        await ctx.send(embed=embed)
        logger.debug(f"Role info requested for {role.name}")

    @commands.hybrid_command(name="rolecleanup")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def role_cleanup(self, ctx: commands.Context):
        """Remove unused roles"""
        count = 0
        for role in ctx.guild.roles:
            if len(role.members) == 0 and not role.managed and role != ctx.guild.default_role:
                try:
                    await role.delete()
                    count += 1
                except:
                    continue
                
        await ctx.send(embed=discord.Embed(
            title="🧹 Role Cleanup",
            description=f"Cleaned up {count} unused roles",
            color=0x00ff00
        ))
        logger.info(f"Cleaned up {count} roles by {ctx.author.id}")

    @commands.hybrid_command(name="createrole")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def create_role(self, ctx: commands.Context):
        """Create a new role with a wizard"""
        if not isinstance(ctx.interaction, discord.Interaction):
            await ctx.send(embed=discord.Embed(
                title="ℹ️ Use Slash Command",
                description="Please use `/createrole` for the interactive modal!",
                color=0xffd700
            ), ephemeral=True)
            logger.debug(f"Prefix !createrole invoked by {ctx.author.id}, prompted for slash")
            return
        
        modal = RoleCreationWizard()
        await ctx.interaction.response.send_modal(modal)
        logger.debug(f"Role creation wizard opened by {ctx.author.id}")

    @commands.hybrid_command(name="setupreaction")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def setup_reaction_role(self, ctx: commands.Context):
        """Set up a reaction role message"""
        available_roles = [
            role for role in ctx.guild.roles 
            if role < ctx.guild.me.top_role and not role.managed and role != ctx.guild.default_role
        ]
        
        if not available_roles:
            await ctx.send(embed=discord.Embed(
                title="❌ No Roles Available",
                description="No roles can be used for reaction roles! Create one with `/createrole`.",
                color=0xff0000
            ), ephemeral=True)
            logger.warning(f"No valid roles for reaction role setup by {ctx.author.id}")
            return
        
        view = ReactionRoleSelectView()
        view.children[0].options = [
            SelectOption(label=role.name, value=str(role.id)) for role in available_roles[:25]
        ]
        await ctx.send(
            embed=discord.Embed(
                title="🎭 Select Reaction Role",
                description="Choose a role for the reaction role system:",
                color=0x7289da
            ),
            view=view,
            ephemeral=True
        )
        logger.debug(f"Reaction role setup view sent by {ctx.author.id} with {len(available_roles)} roles")

    @commands.Cog.listener()
    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild or payload.user_id == self.bot.user.id:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        data = load_reaction_roles()
        guild_data = data.get(str(guild.id), [])
        for rr in guild_data:
            if rr["message_id"] == payload.message_id and rr["channel_id"] == payload.channel_id:
                emoji = str(payload.emoji)
                if emoji == rr["emoji"]:
                    role = guild.get_role(rr["role_id"])
                    if role and role not in member.roles:
                        await member.add_roles(role, reason="Reaction role")
                        try:
                            await member.send(embed=discord.Embed(
                                title="✅ Role Added",
                                description=f"You received the {role.name} role!",
                                color=0x00ff00
                            ))
                        except:
                            logger.warning(f"Failed to DM {member.name}")
                        logger.debug(f"Added {role.name} to {member.id}")

    @commands.Cog.listener()
    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        guild = self.bot.get_guild(payload.guild_id)
        if not guild or payload.user_id == self.bot.user.id:
            return
        member = guild.get_member(payload.user_id)
        if not member:
            return
        
        data = load_reaction_roles()
        guild_data = data.get(str(guild.id), [])
        for rr in guild_data:
            if rr["message_id"] == payload.message_id and rr["channel_id"] == payload.channel_id:
                emoji = str(payload.emoji)
                if emoji == rr["emoji"]:
                    role = guild.get_role(rr["role_id"])
                    if role and role in member.roles:
                        await member.remove_roles(role, reason="Reaction role removed")
                        logger.debug(f"Removed {role.name} from {member.id}")

async def setup(bot):
    try:
        await bot.add_cog(AdvancedRoleSystem(bot))
        logger.info("Loaded cog: cogs.advancedrolesystem")
    except Exception as e:
        logger.error(f"Failed to load cog cogs.advancedrolesystem: {e}")
        raise

# working code
# import discord
# from discord.ext import commands
# from discord import ui, SelectOption, ButtonStyle
# from datetime import datetime

# # ---------------------------
# #         Components
# # ---------------------------

# class RoleSelectView(ui.View):
#     def __init__(self, target_user: discord.Member, action: str):
#         super().__init__(timeout=60)
#         self.target_user = target_user
#         self.action = action
#         self.add_item(RoleSelectDropdown(action))

# class RoleSelectDropdown(ui.Select):
#     def __init__(self, action: str):
#         super().__init__(
#             placeholder=f"Select roles to {action}...",
#             min_values=0,
#             max_values=25,
#             options=[],
#             custom_id=f"role_select_{action}"
#         )
#         self.action = action

#     async def callback(self, interaction: discord.Interaction):
#         try:
#             selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.values]
#             current_roles = self.view.target_user.roles
            
#             if self.action == "add":
#                 new_roles = list(set(current_roles) | set(selected_roles))
#                 action_text = "added to"
#             else:
#                 new_roles = list(set(current_roles) - set(selected_roles))
#                 action_text = "removed from"
            
#             await self.view.target_user.edit(roles=new_roles)
            
#             embed = discord.Embed(
#                 title=f"✅ Roles Updated",
#                 description=f"{len(selected_roles)} roles {action_text} {self.view.target_user.mention}",
#                 color=0x00ff00 if self.action == "add" else 0xff0000
#             )
#             await interaction.response.send_message(embed=embed, ephemeral=True)
            
#         except Exception as e:
#             await interaction.response.send_message(
#                 f"❌ Error: {str(e)}", 
#                 ephemeral=True
#             )

# class RoleCreationWizard(ui.Modal):
#     def __init__(self):
#         super().__init__(title="🔧 Role Creation Wizard", timeout=600)
#         self.name = ui.TextInput(label="Role Name", style=discord.TextStyle.short)
#         self.color = ui.TextInput(label="HEX Color", placeholder="#RRGGBB", required=False)
#         self.permissions = ui.TextInput(
#             label="Permissions (comma separated)",
#             placeholder="manage_messages, kick_members, ...",
#             required=False,
#             style=discord.TextStyle.paragraph
#         )
#         self.add_item(self.name)
#         self.add_item(self.color)
#         self.add_item(self.permissions)

#     async def on_submit(self, interaction: discord.Interaction):
#         try:
#             perms = discord.Permissions()
#             for perm in [p.strip() for p in self.permissions.value.split(",")]:
#                 if hasattr(perms, perm):
#                     setattr(perms, perm, True)
            
#             role = await interaction.guild.create_role(
#                 name=str(self.name),
#                 color=discord.Color.from_str(self.color.value) if self.color.value else discord.Color.default(),
#                 permissions=perms,
#                 reason=f"Created by {interaction.user}"
#             )
            
#             await role.edit(position=interaction.guild.me.top_role.position-1)
            
#             embed = discord.Embed(
#                 title="✅ Role Created",
#                 description=f"{role.mention} created successfully!",
#                 color=role.color
#             )
#             await interaction.response.send_message(embed=embed, ephemeral=True)
            
#         except Exception as e:
#             await interaction.response.send_message(
#                 f"❌ Error: {str(e)}",
#                 ephemeral=True
#             )

# # ---------------------------
# #           Main Cog
# # ---------------------------

# class AdvancedRoleSystem(commands.Cog):
#     def __init__(self, bot):
#         self.bot = bot

#     @commands.hybrid_command(name="addrole")
#     @commands.has_permissions(manage_roles=True)
#     async def add_role(self, ctx, member: discord.Member):
#         """Add roles to a member"""
#         available_roles = [
#             role for role in ctx.guild.roles 
#             if role < ctx.guild.me.top_role
#             and role not in member.roles
#             and not role.managed
#         ]
        
#         if not available_roles:
#             return await ctx.send("❌ No roles available to add!", ephemeral=True)
        
#         view = RoleSelectView(member, "add")
#         view.message = await ctx.send(
#             f"Select roles to add to {member.mention}",
#             view=view,
#             ephemeral=True
#         )

#     @commands.hybrid_command(name="removerole")
#     @commands.has_permissions(manage_roles=True)
#     async def remove_role(self, ctx, member: discord.Member):
#         """Remove roles from a member"""
#         removable_roles = [
#             role for role in member.roles 
#             if role < ctx.guild.me.top_role
#             and not role.managed
#             and role != ctx.guild.default_role
#         ]
        
#         if not removable_roles:
#             return await ctx.send("❌ No roles available to remove!", ephemeral=True)
        
#         view = RoleSelectView(member, "remove")
#         view.message = await ctx.send(
#             f"Select roles to remove from {member.mention}",
#             view=view,
#             ephemeral=True
#         )

#     @commands.hybrid_command(name="roleinfo")
#     async def role_info(self, ctx, role: discord.Role):
#         """Get detailed role information"""
#         embed = discord.Embed(title=f"📊 Role Analytics: {role.name}", color=role.color)
#         embed.add_field(name="Members", value=len(role.members), inline=True)
#         embed.add_field(name="Position", value=role.position, inline=True)
#         embed.add_field(name="Color", value=str(role.color).upper(), inline=True)
#         embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
#         embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
#         embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        
#         perms = "\n".join([perm[0] for perm in role.permissions if perm[1]])
#         embed.add_field(name="Key Permissions", value=perms or "No special permissions", inline=False)
        
#         await ctx.send(embed=embed)

#     @commands.hybrid_command(name="rolecleanup")
#     @commands.has_permissions(manage_roles=True)
#     async def role_cleanup(self, ctx):
#         """Remove unused roles"""
#         count = 0
#         for role in ctx.guild.roles:
#             if len(role.members) == 0 and not role.managed and role != ctx.guild.default_role:
#                 try:
#                     await role.delete()
#                     count += 1
#                 except:
#                     continue
                
#         await ctx.send(f"🧹 Cleaned up {count} unused roles")

# async def setup(bot):
#     await bot.add_cog(AdvancedRoleSystem(bot))

'''
import discord
from discord.ext import commands
from discord import ui, SelectOption, ButtonStyle
from datetime import datetime

# ---------------------------
#         Components
# ---------------------------

class RoleView(ui.View):
    def __init__(self, role_options, max_roles=5):
        super().__init__(timeout=120)
        self.add_item(RoleDropdown(role_options, max_roles))

class RoleDropdown(ui.Select):
    def __init__(self, role_options, max_roles):
        options = [SelectOption(label=role.name, value=str(role.id)) for role in role_options]
        super().__init__(
            placeholder="Select roles to add/remove...",
            min_values=0,
            max_values=max_roles,
            options=options,
            custom_id="role_selector"
        )

    async def callback(self, interaction: discord.Interaction):
        selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.values]
        current_roles = set(interaction.user.roles)
        
        added = []
        removed = []
        
        for role in selected_roles:
            if role not in current_roles:
                await interaction.user.add_roles(role)
                added.append(role.name)
        
        for role in current_roles - set(selected_roles):
            if role in self.options and role != interaction.guild.default_role:
                await interaction.user.remove_roles(role)
                removed.append(role.name)
        
        embed = discord.Embed(color=0x2b2d31)
        if added:
            embed.add_field(name="Added Roles", value="\n".join(added), inline=False)
        if removed:
            embed.add_field(name="Removed Roles", value="\n".join(removed), inline=False)
        
        await interaction.response.send_message(embed=embed, ephemeral=True)

class RoleCreationModal(ui.Modal):
    def __init__(self, bot):
        super().__init__(title="🔧 Role Creation Wizard")
        self.bot = bot
        self.add_item(ui.InputText(label="Role Name", placeholder="Enter role name..."))
        self.add_item(ui.InputText(label="Color (HEX)", placeholder="#RRGGBB", required=False))
        self.add_item(ui.InputText(label="Permissions (comma-separated)", 
                                 placeholder="e.g., manage_roles, kick_members", 
                                 required=False))

    async def callback(self, interaction: discord.Interaction):
        try:
            name = self.children[0].value
            color_str = self.children[1].value.strip("#") if self.children[1].value else None
            permissions = self.children[2].value.split(",") if self.children[2].value else []

            color = discord.Color.default()
            if color_str:
                try:
                    color = discord.Color(int(color_str, 16))
                except ValueError:
                    await interaction.response.send_message("⚠️ Invalid color format! Using default color.", ephemeral=True)

            perms = discord.Permissions()
            for perm in permissions:
                clean_perm = perm.strip().lower().replace(" ", "_")
                if hasattr(perms, clean_perm):
                    setattr(perms, clean_perm, True)
                else:
                    await interaction.response.send_message(f"⚠️ Ignored invalid permission: {perm}", ephemeral=True)

            role = await interaction.guild.create_role(
                name=name,
                color=color,
                permissions=perms,
                reason=f"Created by {interaction.user}"
            )

            embed = discord.Embed(title="✅ Role Created Successfully", color=color)
            embed.add_field(name="Role Name", value=role.mention, inline=False)
            embed.add_field(name="Color", value=f"#{color_str}" if color_str else "Default", inline=True)
            embed.add_field(name="Position", value=role.position, inline=True)
            embed.add_field(name="Permissions", value="\n".join([f"• {p}" for p, v in perms if v]), inline=False)
            embed.set_footer(text=f"Created by {interaction.user}", icon_url=interaction.user.avatar.url)

            await interaction.response.send_message(embed=embed)
            self.bot.get_cog("AdvancedRoles").allowed_roles.setdefault(interaction.guild.id, []).append(role.id)

        except Exception as e:
            await interaction.response.send_message(f"❌ Error creating role: {str(e)}", ephemeral=True)

# ---------------------------
#           Main Cog
# ---------------------------

class AdvancedRoles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.role_cooldown = commands.CooldownMapping.from_cooldown(1, 60, commands.BucketType.user)
        self.allowed_roles = {}

    async def send_role_embed(self, ctx, title, description, color=0x2b2d31):
        embed = discord.Embed(
            title=title,
            description=description,
            color=color,
            timestamp=datetime.now()
        )
        embed.set_footer(text=ctx.guild.name, icon_url=ctx.guild.icon.url)
        await ctx.send(embed=embed)

    @commands.Cog.listener()
    async def on_ready(self):
        for guild in self.bot.guilds:
            self.allowed_roles[guild.id] = [role.id for role in guild.roles if not role.managed and role < guild.me.top_role]

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def rolemenu(self, ctx, *, category: str = None):
        """Create an interactive role selection menu"""
        if category:
            roles = [role for role in ctx.guild.roles 
                    if role.name.lower().startswith(category.lower()) 
                    and role.id in self.allowed_roles.get(ctx.guild.id, [])]
        else:
            roles = [ctx.guild.get_role(rid) for rid in self.allowed_roles.get(ctx.guild.id, [])]
        
        if not roles:
            return await self.send_role_embed(ctx, "⚠️ No Roles Available", 
                                            "No self-assignable roles found.", 0xffcc4d)
        
        view = RoleView(roles[:25], max_roles=5)
        embed = discord.Embed(
            title="🔮 Role Selector",
            description="Choose your roles from the dropdown below!\nYou can select multiple roles at once.",
            color=0x7289da
        )
        if category:
            embed.set_author(name=f"Category: {category.title()}")
        embed.set_thumbnail(url=ctx.guild.icon.url)
        await ctx.send(embed=embed, view=view)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name):
        """Assign a role to a user"""
        bucket = self.role_cooldown.get_bucket(ctx.message)
        if bucket.update_rate_limit():
            return await self.send_role_embed(ctx, "⏳ Cooldown Active",
                                            "Please wait before using this command again.", 0xffcc4d)
        
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                return await self.send_role_embed(ctx, "⚠️ Role Not Found",
                                                f"Couldn't find role '{role_name}'", 0xffcc4d)
            
            if role >= ctx.author.top_role and ctx.author != ctx.guild.owner:
                return await self.send_role_embed(ctx, "⛔ Permission Denied",
                                                "You can't assign roles equal to or higher than yours.", 0xdd2e44)
            
            await member.add_roles(role)
            embed = discord.Embed(
                title="✅ Role Added",
                description=f"{member.mention} has received the **{role.name}** role!",
                color=0x77b255
            )
            embed.add_field(name="Assigned By", value=ctx.author.mention)
            await ctx.send(embed=embed)
        
        except discord.Forbidden:
            await self.send_role_embed(ctx, "❌ Missing Permissions",
                                      "I don't have permission to assign roles!", 0xdd2e44)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role_name):
        """Remove a role from a user"""
        try:
            role = discord.utils.get(ctx.guild.roles, name=role_name)
            if not role:
                return await self.send_role_embed(ctx, "⚠️ Role Not Found",
                                                f"Couldn't find role '{role_name}'", 0xffcc4d)
            
            await member.remove_roles(role)
            embed = discord.Embed(
                title="❌ Role Removed",
                description=f"{member.mention} has lost the **{role.name}** role!",
                color=0xdd2e44
            )
            embed.add_field(name="Removed By", value=ctx.author.mention)
            await ctx.send(embed=embed)
        
        except discord.Forbidden:
            await self.send_role_embed(ctx, "❌ Missing Permissions",
                                      "I don't have permission to remove roles!", 0xdd2e44)

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def createrole(self, ctx):
        """Start interactive role creation process"""
        if not ctx.guild.me.guild_permissions.manage_roles:
            return await ctx.send("❌ I need 'Manage Roles' permission to create roles!")
            
        await ctx.send_modal(RoleCreationModal(self.bot))

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def configure(self, ctx, role: discord.Role):
        """Configure existing role properties"""
        view = ui.View(timeout=120)
        
        async def button_callback(interaction):
            prop = interaction.data["custom_id"]
            modal = ui.Modal(title=f"Configure {prop.capitalize()}")
            modal.add_item(ui.InputText(label=f"New {prop.capitalize()}"))
            
            async def modal_callback(interaction):
                try:
                    value = modal.children[0].value
                    if prop == "color":
                        await role.edit(color=discord.Color(int(value.strip("#"), 16)))
                    elif prop == "name":
                        await role.edit(name=value)
                    elif prop == "permissions":
                        perms = discord.Permissions()
                        for p in value.split(","):
                            setattr(perms, p.strip().lower(), True)
                        await role.edit(permissions=perms)
                    await interaction.response.send_message(f"✅ Updated {prop} successfully!")
                except Exception as e:
                    await interaction.response.send_message(f"❌ Error updating {prop}: {str(e)}", ephemeral=True)
            
            modal.callback = modal_callback
            await interaction.response.send_modal(modal)
        
        for prop in ["color", "name", "permissions"]:
            button = ui.Button(
                style=ButtonStyle.secondary,
                label=f"Edit {prop.capitalize()}",
                custom_id=prop
            )
            button.callback = button_callback
            view.add_item(button)
        
        embed = discord.Embed(title="⚙️ Role Configuration", description=f"Editing {role.mention}")
        embed.add_field(name="Current Name", value=role.name)
        embed.add_field(name="Current Color", value=str(role.color).upper())
        embed.add_field(name="Permissions", value="\n".join([f"• {perm[0]}" for perm in role.permissions if perm[1]]))
        await ctx.send(embed=embed, view=view)

    @commands.Cog.listener()
    async def on_member_join(self, member):
        """Auto-role on member join"""
        if autoroles := self.allowed_roles.get(member.guild.id):
            role = member.guild.get_role(autoroles[0])
            if role:
                await member.add_roles(role)

    @commands.command()
    async def roleinfo(self, ctx, *, role: discord.Role):
        """Get detailed information about a role"""
        embed = discord.Embed(title=f"📚 Role Info: {role.name}", color=role.color)
        embed.add_field(name="Members", value=len(role.members))
        embed.add_field(name="Color", value=str(role.color).upper())
        embed.add_field(name="Position", value=role.position)
        embed.add_field(name="Created At", value=role.created_at.strftime("%b %d, %Y"))
        embed.add_field(name="Mentionable", value=role.mentionable)
        embed.add_field(name="Hoisted", value=role.hoist)
        embed.set_thumbnail(url=f"https://singlecolorimage.com/get/{str(role.color).strip('#')}/400x100")
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(AdvancedRoles(bot))'''