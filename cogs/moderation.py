import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Ban a user from the server."""
        await member.ban(reason=reason)
        await ctx.send(f"🚨 {member.name} has been **banned**. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason="No reason provided"):
        """Kick a user from the server."""
        await member.kick(reason=reason)
        await ctx.send(f"👢 {member.name} has been **kicked**. Reason: {reason}")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member):
        """Mute a user (Requires 'Muted' role)."""
        muted_role = discord.utils.get(ctx.guild.roles, name="Muted")
        if not muted_role:
            await ctx.send("⚠️ No 'Muted' role found. Please create one.")
            return
        await member.add_roles(muted_role)
        await ctx.send(f"🔇 {member.name} has been **muted**.")

async def setup(bot):
    await bot.add_cog(Moderation(bot))
