import discord
from discord.ext import commands
import time

class ChatCommands(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def ping(self, ctx):
        """Check if the bot is responsive and measure latency."""
        await ctx.message.delete()

        start_time = time.time()
        message = await ctx.send("⌛ **Calculating ping...**")
        end_time = time.time()

        latency = round(self.bot.latency * 1000)
        response_time = round((end_time - start_time) * 1000)

        color, indicator = (
            (discord.Color.green(), "🟢 **Blazing Fast!**") if latency < 100 else
            (discord.Color.orange(), "🟡 **Good Speed.**") if latency < 250 else
            (discord.Color.red(), "🔴 **High Latency!**")
        )

        embed = discord.Embed(title="🏓 Pong!", color=color)
        embed.add_field(name="⏳ API Latency", value=f"`{latency} ms`", inline=True)
        embed.add_field(name="⚡ Response Time", value=f"`{response_time} ms`", inline=True)
        embed.add_field(name="📶 Status", value=indicator, inline=False)
        embed.set_footer(text="Ping results updated!", icon_url=self.bot.user.display_avatar.url)

        await message.edit(content="", embed=embed)

    @commands.command()
    async def userinfo(self, ctx, member: discord.Member = None):
        """Show detailed user profile information in a well-structured embed."""
        member = member or ctx.author

        status_dict = {
            discord.Status.online: "🟢 Online",
            discord.Status.offline: "⚫ Offline",
            discord.Status.idle: "🌙 Idle",
            discord.Status.dnd: "⛔ Do Not Disturb"
        }
        status = status_dict.get(member.status, "Unknown")

        role_color = member.top_role.color if member.top_role.color.value != 0 else discord.Color.blue()

        role_badges = []
        if ctx.guild.owner_id == member.id:
            role_badges.append("👑 **Server Owner**")
        if member.guild_permissions.administrator:
            role_badges.append("🔴 **Administrator**")
        if any(role.name.lower() in ["moderator", "mod"] for role in member.roles):
            role_badges.append("🛡 **Moderator**")
        role_badges_text = "\n".join(role_badges) if role_badges else "No special roles."

        role_mentions = [role.mention for role in member.roles if role != ctx.guild.default_role]
        roles_display = ", ".join(role_mentions) if role_mentions else "No Roles"

        permissions = [perm.replace('_', ' ').title() for perm, value in member.guild_permissions if value]
        permissions_display = f"```{', '.join(permissions)}```" if permissions else "No Special Permissions"

        embed = discord.Embed(title=f"👤 {member.display_name}'s Profile", color=role_color)
        embed.set_thumbnail(url=member.display_avatar.url)
        embed.add_field(name="📛 Username", value=f"`{member.name}#{member.discriminator}`", inline=True)
        embed.add_field(name="🆔 User ID", value=f"`{member.id}`", inline=True)
        embed.add_field(name="🌍 Status", value=status, inline=True)
        embed.add_field(name="📅 Joined Server", value=f"`{member.joined_at.strftime('%B %d, %Y')}`", inline=True)
        embed.add_field(name="🌟 Account Created", value=f"`{member.created_at.strftime('%B %d, %Y')}`", inline=True)
        embed.add_field(name="🎭 Top Role", value=f"🎖 {member.top_role.mention}", inline=True)
        embed.add_field(name="💎 Boosting?", value="✨ **Yes**" if member.premium_since else "No", inline=True)
        embed.add_field(name="🔰 Special Roles", value=role_badges_text, inline=False)
        embed.add_field(name="📜 Roles", value=roles_display, inline=False)
        embed.add_field(name="⚙️ Permissions", value=permissions_display, inline=False)
        embed.set_footer(text=f"Requested by {ctx.author.display_name}", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

    @commands.command()
    async def assist(self, ctx):
        """Show an advanced help panel with organized sections."""
        await ctx.message.delete()

        embed = discord.Embed(title=f"🛠️ {self.bot.user.name} Assistance Panel", color=discord.Color.blurple())
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        embed.add_field(
            name="📜 General Commands",
            value="**!ping** - Check bot latency\n**!userinfo [@user]** - Get user information",
            inline=False
        )
        embed.add_field(
            name="🛡️ Moderation",
            value="**!ban @user** - Ban a user\n**!kick @user** - Kick a user\n**!mute @user** - Temporarily mute a user",
            inline=False
        )
        embed.add_field(
            name="🎮 Fun & Utility",
            value="**!8ball <question>** - Ask the magic 8-ball\n**!meme** - Get a random meme",
            inline=False
        )
        embed.set_footer(text="More commands coming soon! Stay tuned.", icon_url=ctx.author.display_avatar.url)
        await ctx.send(embed=embed)

async def setup(bot):
    await bot.add_cog(ChatCommands(bot))
