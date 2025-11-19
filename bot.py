"""
Uma Musume Pretty Derby Discord Bot
Main bot file
"""
import discord
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
    """Custom bot class for Uma Musume bot."""

    def __init__(self):
        super().__init__(
            command_prefix=config.COMMAND_PREFIX,
            description=config.BOT_DESCRIPTION,
            intents=intents,
            help_command=commands.DefaultHelpCommand()
        )

    async def setup_hook(self):
        """Load cogs when bot starts."""
        logger.info("Loading cogs...")

        # Load all cogs from the cogs directory
        cogs_path = Path('./cogs')
        if cogs_path.exists():
            for cog_file in cogs_path.glob('*.py'):
                if cog_file.name != '__init__.py':
                    cog_name = f'cogs.{cog_file.stem}'
                    try:
                        await self.load_extension(cog_name)
                        logger.info(f'Loaded cog: {cog_name}')
                    except Exception as e:
                        logger.error(f'Failed to load cog {cog_name}: {e}')

    async def on_ready(self):
        """Called when bot is ready."""
        logger.info(f'Logged in as {self.user} (ID: {self.user.id})')
        logger.info(f'Bot is ready! Running discord.py version {discord.__version__}')
        logger.info(f'Connected to {len(self.guilds)} guilds')

        # Set bot presence
        await self.change_presence(
            activity=discord.Game(name=f"Uma Musume | {config.COMMAND_PREFIX}help")
        )

    async def on_command_error(self, ctx, error):
        """Global error handler."""
        if isinstance(error, commands.CommandNotFound):
            return
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send(f'❌ Missing required argument: {error.param.name}')
        elif isinstance(error, commands.BadArgument):
            await ctx.send(f'❌ Bad argument provided.')
        else:
            logger.error(f'Error in command {ctx.command}: {error}')
            await ctx.send(f'❌ An error occurred: {str(error)}')

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
