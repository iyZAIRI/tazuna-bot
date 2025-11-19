# 🏇 Uma Musume Pretty Derby Discord Bot

A Discord bot for the Uma Musume Pretty Derby English Global Release! This bot provides character information, gacha simulation, and more features for trainers.

## ✨ Features

- **Character Information**: Look up Uma Musume characters and their details
- **Character List**: Browse all available characters
- **Gacha Simulator**: Simulate gacha rolls (1-10 pulls)
- **Random Character**: Get a random Uma Musume
- **Bot Information**: Check bot stats and latency

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

### Uma Musume Commands
- `!character <name>` or `!uma <name>` - Look up a character
  - Example: `!character Special Week`
- `!list` or `!characters` - List all available characters
- `!random` or `!randomuma` - Get a random character
- `!gacha [1-10]` or `!roll [1-10]` - Simulate gacha rolls
  - Example: `!gacha 10` for a 10-pull

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
└── cogs/              # Command modules
    ├── __init__.py
    ├── general.py     # General bot commands
    └── umamusume.py   # Uma Musume specific commands
```

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
