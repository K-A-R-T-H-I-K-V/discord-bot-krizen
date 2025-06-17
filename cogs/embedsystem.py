import discord
from discord.ext import commands
from discord import ui, TextStyle, app_commands
import logging
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('embed.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class EmbedCreationModal(ui.Modal, title="✨ Create Custom Embed"):
    def __init__(self):
        super().__init__(timeout=600)
        self.title_input = ui.TextInput(
            label="Title",
            placeholder="Enter embed title (max 256 chars)",
            max_length=256,
            required=True
        )
        self.description = ui.TextInput(
            label="Description",
            placeholder="Enter embed description (max 2048 chars)",
            style=TextStyle.paragraph,
            max_length=2048,
            required=False
        )
        self.fields = ui.TextInput(
            label="Fields (name:value, one per line)",
            placeholder="Rule 1: Be kind\nRule 2: No spam",
            style=TextStyle.paragraph,
            required=False
        )
        self.color = ui.TextInput(
            label="Color (HEX)",
            placeholder="#RRGGBB or leave blank for default",
            max_length=7,
            required=False
        )
        self.footer = ui.TextInput(
            label="Footer",
            placeholder="Enter footer text (max 2048 chars)",
            max_length=2048,
            required=False
        )
        self.add_item(self.title_input)
        self.add_item(self.description)
        self.add_item(self.fields)
        self.add_item(self.color)
        self.add_item(self.footer)

    async def on_submit(self, interaction: discord.Interaction):
        try:
            embed = discord.Embed(
                title=str(self.title_input),
                description=str(self.description) or None,
                color=self.parse_color(str(self.color)) if self.color.value else 0x7289da
            )
            if self.fields.value:
                for line in self.fields.value.split('\n')[:10]:  # Limit to 10 fields
                    if ':' in line:
                        name, value = line.split(':', 1)
                        embed.add_field(name=name.strip()[:256], value=value.strip()[:1024], inline=False)
            if self.footer.value:
                embed.set_footer(text=str(self.footer))
            await interaction.channel.send(embed=embed)
            await interaction.response.send_message(embed=discord.Embed(
                title="✅ Embed Created",
                description="Your embed has been posted!",
                color=0x00ff00
            ), ephemeral=True)
            logger.info(f"Embed created by {interaction.user.id} in {interaction.channel.id}")
        except Exception as e:
            await interaction.response.send_message(embed=discord.Embed(
                title="❌ Error",
                description=f"Failed to create embed: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Embed creation failed: {e}")

    def parse_color(self, color_str: str) -> int:
        if re.match(r'^#[0-9A-Fa-f]{6}$', color_str):
            return int(color_str[1:], 16)
        return 0x7289da  # Default color

class EmbedSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        logger.info("EmbedSystem initialized")

    @commands.hybrid_command(name="createembed")
    @app_commands.checks.has_permissions(administrator=True)
    async def create_embed(self, ctx: commands.Context):
        """Create a custom embed (admin only)."""
        if not isinstance(ctx.interaction, discord.Interaction):
            # Prefix command invoked
            await ctx.send(embed=discord.Embed(
                title="ℹ️ Use Slash Command",
                description="Please use `/createembed` for the interactive modal!",
                color=0xffd700
            ), ephemeral=True)
            logger.debug(f"Prefix !createembed invoked by {ctx.author.id}, prompted for slash")
            return
        
        try:
            modal = EmbedCreationModal()
            await ctx.interaction.response.send_modal(modal)
        except Exception as e:
            await ctx.send(embed=discord.Embed(
                title="❌ Error",
                description=f"Failed to open modal: {str(e)}",
                color=0xff0000
            ), ephemeral=True)
            logger.error(f"Modal send failed: {e}")

async def setup(bot):
    try:
        await bot.add_cog(EmbedSystem(bot))
        logger.info("Loaded cog: cogs.embedsystem")
    except Exception as e:
        logger.error(f"Failed to load cog cogs.embedsystem: {e}")
        raise