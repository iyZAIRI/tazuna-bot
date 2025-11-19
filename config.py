"""Configuration management for the Uma Musume Discord bot."""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Discord Configuration
DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
COMMAND_PREFIX = os.getenv('COMMAND_PREFIX', '!')

# Bot Settings
BOT_DESCRIPTION = 'Uma Musume Pretty Derby Discord Bot'
BOT_VERSION = '2.0.0'

# Database Configuration
DATABASE_PATH = os.getenv('DATABASE_PATH', './data/master.mdb')
DATABASE_LANGUAGE = os.getenv('DATABASE_LANGUAGE', 'auto')  # 'en', 'jp', or 'auto'

# Colors for embeds (Uma Musume theme)
EMBED_COLOR = 0xFF69B4  # Hot pink, matching Uma Musume's vibrant theme
ERROR_COLOR = 0xFF0000
SUCCESS_COLOR = 0x00FF00
INFO_COLOR = 0x3498DB
