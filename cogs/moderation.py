import discord
from discord.ext import commands
import asyncio

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ✅ Helper Function for Embeds
    async def send_embed(self, ctx, title, description, color):
        icon_url = ctx.author.avatar.url if ctx.author.avatar else ctx.author.default_avatar.url
        embed = discord.Embed(title=title, description=description, color=color)
        embed.set_footer(text=f"Requested by {ctx.author}", icon_url=icon_url)
        await ctx.send(embed=embed)

    # ✅ Ban Command
    @commands.command(name="ban")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.ban(reason=reason)
        await self.send_embed(ctx, "🚨 User Banned", f"**{member.mention}** has been **banned**.\n📝 Reason: {reason}", discord.Color.red())

    # ✅ Unban Command (Fixed)
    @commands.command(name="unban")
    @commands.has_permissions(ban_members=True)
    async def unban(self, ctx, user_id: int):
        try:
            user = await self.bot.fetch_user(user_id)
            await ctx.guild.unban(user)
            await self.send_embed(ctx, "✅ User Unbanned", f"**{user.name}** has been unbanned.", discord.Color.green())
        except discord.NotFound:
            await self.send_embed(ctx, "❌ Error", "User not found or not banned.", discord.Color.red())

    # ✅ Kick Command
    @commands.command(name="kick")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        await member.kick(reason=reason)
        await self.send_embed(ctx, "👢 User Kicked", f"**{member.mention}** has been kicked.\n📝 Reason: {reason}", discord.Color.orange())

    # ✅ Purge Command
    @commands.command(name="purge")
    @commands.has_permissions(manage_messages=True)
    async def purge(self, ctx, amount: int):
        if amount < 1 or amount > 100:
            await self.send_embed(ctx, "⚠️ Invalid Input", "Please specify an amount between **1 and 100**.", discord.Color.yellow())
            return

        deleted = await ctx.channel.purge(limit=amount)
        await self.send_embed(ctx, "🧹 Messages Purged", f"Deleted `{len(deleted)}` messages.", discord.Color.purple())

     # ✅ Ensure Muted Role Exists with Proper Permissions
    async def ensure_muted_role(self, guild):
        muted_role = discord.utils.get(guild.roles, name="Muted")
        if not muted_role:
            muted_role = await guild.create_role(name="Muted", reason="Creating Muted role for moderation")
            for channel in guild.channels:
                await channel.set_permissions(muted_role, send_messages=False, speak=False, add_reactions=False)
        return muted_role

    # ✅ Mute Command (Timed)
    @commands.command(name="mute")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, duration: int = 10):
        muted_role = await self.ensure_muted_role(ctx.guild)
        
        if muted_role in member.roles:
            await self.send_embed(ctx, "⚠️ Error", f"**{member.mention}** is already muted.", discord.Color.red())
            return
        
        await member.add_roles(muted_role)
        await self.send_embed(ctx, "🔇 User Muted", f"**{member.mention}** has been muted for `{duration}` minutes.", discord.Color.dark_gray())

        await asyncio.sleep(duration * 60)
        await member.remove_roles(muted_role)
        await self.send_embed(ctx, "🔊 User Unmuted", f"**{member.mention}** has been automatically unmuted.", discord.Color.green())

    # ✅ Unmute Command
    @commands.command(name="unmute")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: discord.Member):
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role or muted_role not in member.roles:
            await self.send_embed(ctx, "⚠️ Error", f"**{member.mention}** is not muted.", discord.Color.red())
            return

        await member.remove_roles(muted_role)
        await self.send_embed(ctx, "🔊 User Unmuted", f"**{member.mention}** has been unmuted.", discord.Color.green())

    # ✅ Error Handler for Missing Permissions
    async def cog_command_error(self, ctx, error):
        if isinstance(error, commands.MissingPermissions):
            await self.send_embed(ctx, "⛔ Permission Denied", "You **don't have permission** to use this command.", discord.Color.red())

async def setup(bot):
    await bot.add_cog(Moderation(bot))