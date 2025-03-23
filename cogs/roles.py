import discord
from discord.ext import commands

class Roles(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx, member: discord.Member, *, role_name):
        """Assign a role to a user."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send("⚠️ Role not found.")
            return
        await member.add_roles(role)
        await ctx.send(f"✅ {member.name} has been given the role **{role_name}**.")

    @commands.command()
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx, member: discord.Member, *, role_name):
        """Remove a role from a user."""
        role = discord.utils.get(ctx.guild.roles, name=role_name)
        if not role:
            await ctx.send("⚠️ Role not found.")
            return
        await member.remove_roles(role)
        await ctx.send(f"❌ {member.name} has been removed from the role **{role_name}**.")

async def setup(bot):
    await bot.add_cog(Roles(bot))
