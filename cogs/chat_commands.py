import discord
from discord.ext import commands

class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check if the bot is responsive."""
        await ctx.send("Pong! 🏓")

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show user information. If no user is mentioned, show info of the sender."""
        member = member or ctx.author
        embed = discord.Embed(title="User Info", color=discord.Color.blue())
        embed.set_thumbnail(url=member.avatar.url)
        embed.add_field(name="Username", value=member.name, inline=True)
        embed.add_field(name="ID", value=member.id, inline=True)
        embed.add_field(name="Joined", value=member.joined_at.strftime("%Y-%m-%d"), inline=False)
        await ctx.send(embed=embed)

    @commands.command()
    async def assist(self, ctx):
        """Show available commands."""
        help_text = "**Available Commands:**\n"
        help_text += "`!ping` - Check if bot is online.\n"
        help_text += "`!userinfo [@user]` - Get user info.\n"
        help_text += "`!assist` - Show this help message."
        await ctx.send(help_text)

async def setup(bot):
    await bot.add_cog(ChatCommands(bot))
