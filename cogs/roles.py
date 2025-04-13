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
from discord import ui, SelectOption, ButtonStyle
from datetime import datetime

# ---------------------------
#         Components
# ---------------------------

class RoleSelectView(ui.View):
    def __init__(self, target_user: discord.Member, action: str):
        super().__init__(timeout=60)
        self.target_user = target_user
        self.action = action
        self.add_item(RoleSelectDropdown(action))

class RoleSelectDropdown(ui.Select):
    def __init__(self, action: str):
        super().__init__(
            placeholder=f"Select roles to {action}...",
            min_values=0,
            max_values=25,
            options=[],
            custom_id=f"role_select_{action}"
        )
        self.action = action

    async def callback(self, interaction: discord.Interaction):
        try:
            selected_roles = [interaction.guild.get_role(int(role_id)) for role_id in self.values]
            current_roles = self.view.target_user.roles
            
            if self.action == "add":
                new_roles = list(set(current_roles) | set(selected_roles))
                action_text = "added to"
            else:
                new_roles = list(set(current_roles) - set(selected_roles))
                action_text = "removed from"
            
            await self.view.target_user.edit(roles=new_roles)
            
            embed = discord.Embed(
                title=f"✅ Roles Updated",
                description=f"{len(selected_roles)} roles {action_text} {self.view.target_user.mention}",
                color=0x00ff00 if self.action == "add" else 0xff0000
            )
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}", 
                ephemeral=True
            )

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
            perms = discord.Permissions()
            for perm in [p.strip() for p in self.permissions.value.split(",")]:
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
            await interaction.response.send_message(embed=embed, ephemeral=True)
            
        except Exception as e:
            await interaction.response.send_message(
                f"❌ Error: {str(e)}",
                ephemeral=True
            )

# ---------------------------
#           Main Cog
# ---------------------------

class AdvancedRoleSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="addrole")
    @commands.has_permissions(manage_roles=True)
    async def add_role(self, ctx, member: discord.Member):
        """Add roles to a member"""
        available_roles = [
            role for role in ctx.guild.roles 
            if role < ctx.guild.me.top_role
            and role not in member.roles
            and not role.managed
        ]
        
        if not available_roles:
            return await ctx.send("❌ No roles available to add!", ephemeral=True)
        
        view = RoleSelectView(member, "add")
        view.message = await ctx.send(
            f"Select roles to add to {member.mention}",
            view=view,
            ephemeral=True
        )

    @commands.hybrid_command(name="removerole")
    @commands.has_permissions(manage_roles=True)
    async def remove_role(self, ctx, member: discord.Member):
        """Remove roles from a member"""
        removable_roles = [
            role for role in member.roles 
            if role < ctx.guild.me.top_role
            and not role.managed
            and role != ctx.guild.default_role
        ]
        
        if not removable_roles:
            return await ctx.send("❌ No roles available to remove!", ephemeral=True)
        
        view = RoleSelectView(member, "remove")
        view.message = await ctx.send(
            f"Select roles to remove from {member.mention}",
            view=view,
            ephemeral=True
        )

    @commands.hybrid_command(name="roleinfo")
    async def role_info(self, ctx, role: discord.Role):
        """Get detailed role information"""
        embed = discord.Embed(title=f"📊 Role Analytics: {role.name}", color=role.color)
        embed.add_field(name="Members", value=len(role.members), inline=True)
        embed.add_field(name="Position", value=role.position, inline=True)
        embed.add_field(name="Color", value=str(role.color).upper(), inline=True)
        embed.add_field(name="Created At", value=role.created_at.strftime("%Y-%m-%d %H:%M"), inline=True)
        embed.add_field(name="Mentionable", value=role.mentionable, inline=True)
        embed.add_field(name="Hoisted", value=role.hoist, inline=True)
        
        perms = "\n".join([perm[0] for perm in role.permissions if perm[1]])
        embed.add_field(name="Key Permissions", value=perms or "No special permissions", inline=False)
        
        await ctx.send(embed=embed)

    @commands.hybrid_command(name="rolecleanup")
    @commands.has_permissions(manage_roles=True)
    async def role_cleanup(self, ctx):
        """Remove unused roles"""
        count = 0
        for role in ctx.guild.roles:
            if len(role.members) == 0 and not role.managed and role != ctx.guild.default_role:
                try:
                    await role.delete()
                    count += 1
                except:
                    continue
                
        await ctx.send(f"🧹 Cleaned up {count} unused roles")

async def setup(bot):
    await bot.add_cog(AdvancedRoleSystem(bot))

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