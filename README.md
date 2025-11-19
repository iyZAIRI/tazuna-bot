# 🏇 Uma Musume Pretty Derby Discord Bot

A Discord bot for the Uma Musume Pretty Derby English Global Release! This bot provides character information, gacha simulation, and more features for trainers.

## ✨ Features

### Character System
- **Character Database**: 119+ characters from the game database
- **Character Cards**: View all card variants and rarities
- **Character Search**: Search by name (English/Japanese support)
- **Running Styles**: See character running styles and talents

### Skills System
- **Skill Database**: 1,847+ skills with detailed information
- **Skill Search**: Find skills by name or category
- **Top Skills**: View highest-rated skills
- **Skill Categories**: Speed, Stamina, Position, and more

### Support Cards
- **Support Card Database**: 329+ support cards
- **Card Types**: Speed, Stamina, Power, Guts, Wisdom, Friend
- **SSR Listing**: Filter by rarity
- **Character Support**: Find all supports for a character

### Races
- **Race Database**: 500+ races from the game
- **Grade Filtering**: G1, G2, G3, Open, Pre-Open
- **Distance Categories**: Sprint, Mile, Middle, Long
- **Ground Types**: Turf and Dirt races

### Database Features
- **Real Game Data**: Uses actual game database (master.mdb)
- **EN/JP Support**: Works with both English and Japanese databases
- **Database Explorer**: Explore 574 tables via Discord commands

## 📋 Prerequisites

- Python 3.8 or higher
- A Discord account
- A Discord bot token ([How to get one](#getting-a-discord-bot-token))

## 🚀 Quick Start

### 1. Clone the Repository

```bash
git clone <your-repo-url>
cd tazuna-bot
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

Or using a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configure the Bot

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Discord bot token:
   ```
   DISCORD_TOKEN=your_bot_token_here
   COMMAND_PREFIX=!
   ```

### 4. Run the Bot

```bash
python bot.py
```

You should see output indicating the bot has logged in successfully!

## 🎮 Commands

### General Commands
- `!ping` - Check bot latency
- `!info` - Display bot information
- `!invite` - Get bot invite link
- `!help` - Show all available commands

### Character Commands
- `!character <name>` - Look up character information
- `!list [page]` - List all characters (paginated)
- `!random` - Get a random character
- `!search <query>` - Search for characters
- `!ssr` - List all SSR characters

### Skill Commands
- `!skill <name>` - Look up skill information
- `!skills [rarity]` - List skills by rarity (1-3)
- `!searchskill <query>` - Search for skills
- `!topskills [limit]` - Show top skills by grade value

### Support Card Commands
- `!support <name>` - Look up support card
- `!supports [type]` - List support cards by type
  - Types: speed, stamina, power, guts, wisdom, friend
- `!ssrsupports` - List all SSR support cards
- `!searchsupport <query>` - Search for support cards

### Race Commands
- `!race <name>` - Look up race information
- `!races [grade]` - List races by grade (1-5)
  - 1=Pre-Open, 2=Open, 3=G3, 4=G2, 5=G1
- `!g1races` - List all G1 races
- `!searchrace <query>` - Search for races

### Database Commands
- `!dbstatus` - Check database connection status
- `!dbtables [search]` - List all database tables
- `!dbschema <table>` - Show table structure
- `!dbquery <sql>` - Run SELECT query (owner only)

## 🔧 Getting a Discord Bot Token

1. Go to the [Discord Developer Portal](https://discord.com/developers/applications)
2. Click "New Application" and give it a name
3. Go to the "Bot" section in the left sidebar
4. Click "Add Bot"
5. Under the bot's username, click "Reset Token" to reveal your bot token
6. Copy the token and paste it in your `.env` file
7. Enable "Message Content Intent" under Privileged Gateway Intents
8. Go to OAuth2 → URL Generator
9. Select scopes: `bot`
10. Select permissions:
    - Read Messages/View Channels
    - Send Messages
    - Embed Links
    - Attach Files
    - Read Message History
    - Add Reactions
11. Copy the generated URL and use it to invite the bot to your server

## 📁 Project Structure

```
tazuna-bot/
├── bot.py              # Main bot file
├── config.py           # Configuration management
├── requirements.txt    # Python dependencies
├── .env               # Environment variables (not in git)
├── .env.example       # Example environment file
├── .gitignore         # Git ignore rules
├── cogs/              # Command modules (Discord commands)
│   ├── __init__.py
│   ├── general.py     # General bot commands
│   ├── characters.py  # Character commands
│   ├── skills.py      # Skill commands
│   ├── support_cards.py # Support card commands
│   ├── races.py       # Race commands
│   ├── database.py    # Database exploration commands
│   └── umamusume.py   # Legacy commands (deprecated)
├── models/            # Data models (game entities)
│   ├── __init__.py
│   ├── character.py   # Character & CharacterCard models
│   ├── skill.py       # Skill model
│   ├── support_card.py # SupportCard model
│   └── race.py        # Race model
├── managers/          # Data managers (business logic)
│   ├── __init__.py
│   ├── character_manager.py    # Character data management
│   ├── skill_manager.py        # Skill data management
│   ├── support_card_manager.py # Support card management
│   └── race_manager.py         # Race data management
├── utils/             # Utility scripts
│   ├── __init__.py
│   ├── download_masterdb.py  # Download master.mdb from GitHub
│   ├── db_reader.py          # SQLite database reader
│   └── extract_data.py       # Data extraction tool
└── data/              # Game database and extracted data
    ├── README.md      # Data directory documentation
    └── master.mdb     # Game database (download separately)
```

## 🗄️ Working with Game Data (master.mdb)

The bot can use real game data from Uma Musume's master.mdb database file!

### Download the Database

```bash
# Download master.mdb from GitHub
python utils/download_masterdb.py
```

This downloads the database to `./data/master.mdb`.

### Explore the Database

```bash
# See all available tables
python utils/db_reader.py

# Extract and explore game data
python utils/extract_data.py
```

### Use Database in Discord

Once downloaded, use these commands in Discord:
- `!dbstatus` - Check if database is connected
- `!dbtables` - List all tables
- `!dbtables skill` - Search for tables containing "skill"
- `!dbschema table_name` - See table structure

### Extract Custom Data

```python
from utils.db_reader import MasterDBReader

db = MasterDBReader()
db.connect()

# Get character data (example - table names may vary)
characters = db.query("SELECT * FROM card_data LIMIT 10")
print(characters)

# Export to JSON
db.export_table_to_json('skill_data', './data/skills.json')

db.close()
```

See `data/README.md` for more details!

## 🛠️ Development

### Adding New Commands

Commands are organized in cogs located in the `cogs/` directory. To add a new command:

1. Open the appropriate cog file (or create a new one)
2. Add your command using the `@commands.command()` decorator
3. The bot will automatically load it on startup

Example:
```python
@commands.command(name='mycommand')
async def my_command(self, ctx):
    """Command description."""
    await ctx.send("Hello!")
```

### Adding New Cogs

1. Create a new Python file in the `cogs/` directory
2. Follow the structure of existing cogs
3. Make sure to include the `setup()` function at the bottom

## 🎨 Customization

- **Command Prefix**: Change `COMMAND_PREFIX` in `.env`
- **Embed Colors**: Modify colors in `config.py`
- **Bot Presence**: Edit the `on_ready()` function in `bot.py`

## 📝 To-Do / Future Features

- [ ] Integration with Uma Musume game data API
- [ ] Event notifications and timers
- [ ] Skill and ability information
- [ ] Support card database
- [ ] Team building recommendations
- [ ] Race simulation
- [ ] User profiles and favorites
- [ ] Database integration for persistence

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Report bugs
- Suggest new features
- Submit pull requests

## 📜 License

This project is for educational and fan purposes. Uma Musume Pretty Derby is owned by Cygames.

## 🙏 Credits

- Uma Musume Pretty Derby © Cygames
- Built with [discord.py](https://github.com/Rapptz/discord.py)

## 📞 Support

If you encounter any issues or have questions, please open an issue on GitHub.

---

**Happy Training, Trainer! 🏇✨**
