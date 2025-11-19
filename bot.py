"""
Uma Musume Pretty Derby Discord Bot
Main bot file with slash commands support
"""
import discord
from discord import app_commands
from discord.ext import commands
import asyncio
import logging
from pathlib import Path
import config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('UmaMusumeBot')

# Bot intents
intents = discord.Intents.default()
intents.message_content = True
intents.members = True

class UmaMusumeBot(commands.Bot):
    """Custom bot class for Uma Musume bot with slash commands."""

    def __init__(self):
        super().__init__(
            command_prefix="!",  # Kept for legacy, but slash commands are primary
            description=config.BOT_DESCRIPTION,
            intents=intents,
            help_command=None  # Disabled default help
        )
        self.initial_extensions = []

    async def setup_hook(self):
        """Load cogs and sync slash commands when bot starts."""
        logger.info("Loading cogs...")

        # Load all cogs from the cogs directory
        cogs_path = Path('./cogs')
        if cogs_path.exists():
            for cog_file in cogs_path.glob('*.py'):
                if cog_file.name != '__init__.py' and not cog_file.name.endswith('.backup'):
                    cog_name = f'cogs.{cog_file.stem}'
                    try:
                        await self.load_extension(cog_name)
                        logger.info(f'Loaded cog: {cog_name}')
                    except Exception as e:
                        logger.error(f'Failed to load cog {cog_name}: {e}')

        # Sync slash commands with Discord
        logger.info("Syncing slash commands...")
        try:
            synced = await self.tree.sync()
            logger.info(f"Synced {len(synced)} slash command(s)")
        except Exception as e:
            logger.error(f"Failed to sync commands: {e}")

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Bot is ready! Running discord.py version {discord.__version__}')
        logger.info(f'Connected to {len(self.guilds)} guilds')

        # Set bot presence
        await self.change_presence(
            activity=discord.Game(name="Uma Musume | Use /help")
        )

    async def on_command_error(self, ctx, error):
        """Global error handler for prefix commands (legacy)."""
        if isinstance(error, commands.CommandNotFound):
            return
        logger.error(f'Error in command {ctx.command}: {error}')

async def main():
    """Main function to run the bot."""
    if not config.DISCORD_TOKEN:
        logger.error("DISCORD_TOKEN not found in environment variables!")
        logger.error("Please create a .env file with your bot token.")
        logger.error("See .env.example for reference.")
        return

    bot = UmaMusumeBot()

    try:
        await bot.start(config.DISCORD_TOKEN)
    except KeyboardInterrupt:
        logger.info("Shutting down bot...")
        await bot.close()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        await bot.close()

if __name__ == '__main__':
    asyncio.run(main())
