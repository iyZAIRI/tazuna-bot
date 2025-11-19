# 🎯 Uma Musume Bot - Modules Guide

This guide explains the modular architecture of the Uma Musume Discord bot and how to use it.

---

## 📁 Architecture Overview

The bot is organized into three main layers:

```
┌─────────────────────────────────────────┐
│         Discord Commands (Cogs)         │  ← User-facing commands
├─────────────────────────────────────────┤
│       Managers (Data Access Layer)      │  ← Business logic & queries
├─────────────────────────────────────────┤
│      Models (Data Representation)       │  ← Data structures
├─────────────────────────────────────────┤
│       Database (master.mdb)             │  ← Raw game data
└─────────────────────────────────────────┘
```

---

## 🗂️ Modules

### 1. **Characters Module**

**Models**: `models/character.py`
- `Character` - Represents an Uma Musume character
- `CharacterCard` - Represents a character card (playable version)
- `RunningStyle` - Enum for running styles (Runner, Leader, etc.)

**Manager**: `managers/character_manager.py`
- `CharacterManager` - Handles character data loading and queries

**Cog**: `cogs/characters.py`

**Commands**:
- `!character <name>` - Look up character info
- `!list [page]` - List all characters (paginated)
- `!random` - Get random character
- `!search <query>` - Search for characters
- `!ssr` - List all SSR characters

**Example Usage**:
```python
from managers.character_manager import CharacterManager

manager = CharacterManager()
manager.load()

# Get character by name
special_week = manager.get_by_name("Special Week")
print(special_week.display_name)
print(special_week.birth_date)
print(f"{special_week.card_count} cards")

# Search
results = manager.search("week")

# Get random
random_char = manager.get_random()
```

---

### 2. **Skills Module**

**Models**: `models/skill.py`
- `Skill` - Represents a skill
- `SkillCategory` - Enum for skill categories

**Manager**: `managers/skill_manager.py`
- `SkillManager` - Handles skill data

**Cog**: `cogs/skills.py`

**Commands**:
- `!skill <name>` - Look up skill info
- `!skills [rarity]` - List skills by rarity
- `!searchskill <query>` - Search for skills
- `!topskills [limit]` - Show top skills by grade value

**Example Usage**:
```python
from managers.skill_manager import SkillManager

manager = SkillManager()
manager.load()

# Get skill by name
skill = manager.get_by_name("acceleration")

# Get all SSR skills
ssr_skills = manager.get_by_rarity(3)

# Get top skills
top_10 = manager.get_top(10)
```

---

### 3. **Support Cards Module**

**Models**: `models/support_card.py`
- `SupportCard` - Represents a support card
- `SupportCardType` - Enum for card types (Speed, Stamina, etc.)

**Manager**: `managers/support_card_manager.py`
- `SupportCardManager` - Handles support card data

**Cog**: `cogs/support_cards.py`

**Commands**:
- `!support <name>` - Look up support card
- `!supports [type]` - List support cards by type
- `!ssrsupports` - List all SSR supports
- `!searchsupport <query>` - Search for support cards

**Example Usage**:
```python
from managers.support_card_manager import SupportCardManager

manager = SupportCardManager()
manager.load()

# Get support card
card = manager.get_by_name("Special Week")

# Get all Speed type cards
speed_cards = manager.get_by_type(1)

# Get SSR cards
ssr_cards = manager.get_ssr_cards()
```

---

### 4. **Races Module**

**Models**: `models/race.py`
- `Race` - Represents a race
- `RaceGrade` - Enum for race grades (G1, G2, etc.)
- `Ground` - Enum for ground types (Turf, Dirt)

**Manager**: `managers/race_manager.py`
- `RaceManager` - Handles race data

**Cog**: `cogs/races.py`

**Commands**:
- `!race <name>` - Look up race info
- `!races [grade]` - List races by grade
- `!g1races` - List all G1 races
- `!searchrace <query>` - Search for races

**Example Usage**:
```python
from managers.race_manager import RaceManager

manager = RaceManager()
manager.load()

# Get race by name
race = manager.get_by_name("Japan Cup")

# Get all G1 races
g1_races = manager.get_g1_races()

# Get races by distance
middle_races = manager.get_by_distance(1800, 2400)
```

---

## 🌐 Language Support (EN/JP Database)

The bot supports both English and Japanese databases!

### **Setting Up**

1. **Japanese Database** (default):
   ```bash
   python utils/download_masterdb.py
   ```
   This downloads the JP master.mdb

2. **English Database**:
   - Extract master.mdb from your English game installation
   - Place it in `./data/master_en.mdb`
   - Update `.env`:
     ```
     DATABASE_PATH=./data/master_en.mdb
     DATABASE_LANGUAGE=en
     ```

3. **Auto-detect**:
   ```
   DATABASE_LANGUAGE=auto
   ```
   The bot will detect which language the database is in

### **Switching Databases**

Just change the `DATABASE_PATH` in your `.env` file:

```env
# Use Japanese database
DATABASE_PATH=./data/master.mdb

# Use English database
DATABASE_PATH=./data/master_en.mdb
```

All text (character names, skills, races) will automatically be in the correct language!

---

## 🔧 Adding New Modules

To add a new game module:

### 1. **Create a Model** (`models/your_module.py`)
```python
from dataclasses import dataclass

@dataclass
class YourData:
    id: int
    name: str
    # Add more fields...
```

### 2. **Create a Manager** (`managers/your_manager.py`)
```python
from utils.db_reader import MasterDBReader
from models.your_module import YourData

class YourManager:
    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db = MasterDBReader(db_path)
        self.data = {}

    def load(self) -> bool:
        self.db.connect()
        query = "SELECT * FROM your_table"
        results = self.db.query(query)
        # Process results...
        return True
```

### 3. **Create a Cog** (`cogs/your_module.py`)
```python
from discord.ext import commands
from managers.your_manager import YourManager

class YourModule(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.manager = YourManager()
        self.manager.load()

    @commands.command(name='your_command')
    async def your_command(self, ctx):
        # Implement command...
        pass

async def setup(bot):
    await bot.add_cog(YourModule(bot))
```

---

## 📊 Database Tables Reference

Key tables used by each module:

| Module | Main Tables | Text Category |
|--------|-------------|---------------|
| Characters | `card_data`, `chara_data` | 6 (names) |
| Skills | `skill_data`, `skill_set` | 47 (names), 48 (descriptions) |
| Support Cards | `support_card_data` | 75 (names) |
| Races | `race`, `race_instance` | 30 (names) |

---

## 🎯 Best Practices

1. **Always use Managers** - Never query the database directly from cogs
2. **Load once** - Managers cache data in memory after loading
3. **Close connections** - Use `manager.close()` in `cog_unload()`
4. **Handle errors** - Check if `manager.load()` returns `True`
5. **Limit results** - Use pagination for large result sets

---

## 🧪 Testing Modules

```python
# Test character manager
from managers.character_manager import CharacterManager

manager = CharacterManager()
if manager.load():
    print(f"Loaded {len(manager.get_all())} characters")
    special_week = manager.get_by_name("Special Week")
    print(f"Found: {special_week.display_name}")
else:
    print("Failed to load")
```

---

## 📝 Module Status

| Module | Status | Commands | Database Tables |
|--------|--------|----------|-----------------|
| ✅ Characters | Complete | 5 | 3 |
| ✅ Skills | Complete | 4 | 4 |
| ✅ Support Cards | Complete | 4 | 2 |
| ✅ Races | Complete | 4 | 2 |
| 🚧 Training | Planned | - | 10+ |
| 🚧 Gacha | Planned | - | 5+ |
| 🚧 Events | Planned | - | 8+ |

---

**Happy coding, Trainer! 🏇✨**
