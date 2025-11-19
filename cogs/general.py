"""General commands for the bot using slash commands."""
import discord
from discord import app_commands
from discord.ext import commands
import config
import time

class General(commands.Cog):
    """General bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        """Check bot latency."""
        start_time = time.time()

        # Defer the response
        await interaction.response.defer()

        end_time = time.time()

        embed = discord.Embed(
            title="🏁 Pong!",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="Bot Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        embed.add_field(
            name="Response Time",
            value=f"{round((end_time - start_time) * 1000)}ms",
            inline=True
        )
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="info", description="Display bot information")
    async def info(self, interaction: discord.Interaction):
        """Display bot information."""
        embed = discord.Embed(
            title="🏇 Uma Musume Bot Information",
            description=config.BOT_DESCRIPTION,
            color=config.EMBED_COLOR
        )
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(
            name="Library",
            value=f"discord.py {discord.__version__}",
            inline=True
        )
        embed.set_footer(text="Uma Musume Pretty Derby Discord Bot")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="help", description="Show all available commands")
    async def help_command(self, interaction: discord.Interaction):
        """Show all available commands."""
        embed = discord.Embed(
            title="🏇 Uma Musume Bot - Commands",
            description="Use `/` to see all available commands with autocomplete!",
            color=config.EMBED_COLOR
        )

        embed.add_field(
            name="📊 General",
            value="`/ping` - Check bot latency\n`/info` - Bot information\n`/help` - This message",
            inline=False
        )

        embed.add_field(
            name="🏇 Characters",
            value="`/character` - Look up character info\n`/characters` - List all characters\n`/randomchar` - Random character",
            inline=False
        )

        embed.add_field(
            name="⚡ Skills",
            value="`/skill` - Look up skill info\n`/skills` - List skills\n`/topskills` - Top skills",
            inline=False
        )

        embed.add_field(
            name="💪 Support Cards",
            value="`/support` - Look up support card\n`/supports` - List support cards\n`/ssrsupports` - List SSR supports",
            inline=False
        )

        embed.add_field(
            name="🏁 Races",
            value="`/race` - Look up race info\n`/races` - List races\n`/g1races` - List G1 races",
            inline=False
        )

        embed.set_footer(text="💡 Tip: Start typing / and Discord will show you all commands!")
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(General(bot))
