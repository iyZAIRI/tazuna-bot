# 🗄️ Uma Musume master.mdb Database Report

**Generated:** 2025-11-19
**Source:** [UmaMusumeMetaMasterMDB](https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB)
**Database Size:** 574 tables, ~500k+ total rows

---

## 📊 Executive Summary

The master.mdb file contains **ALL** game data for Uma Musume Pretty Derby including:
- ✅ **119 playable characters** (with 230 character cards)
- ✅ **1,847 skills** (passives, actives, unique skills)
- ✅ **329 support cards** (SSR, SR, R rarities)
- ✅ **2,386 races** (story races, daily races, legend races, etc.)
- ✅ **15,569 story events** (character stories, main story, etc.)
- ✅ Training scenarios, items, gacha data, and more!

---

## 🎯 Key Tables Reference

### **Character Data**

| Table | Rows | Description |
|-------|------|-------------|
| `card_data` | 230 | Character cards (playable units) |
| `chara_data` | 157 | Base character information (appearance, colors, birth date) |
| `text_data` (cat=6) | 157 | Character names (Japanese) |

**Character Card Structure:**
```json
{
  "card_id": 100101,
  "chara_id": 1001,
  "default_rarity": 3,
  "running_style": 3,
  "talent_speed": 0,
  "talent_stamina": 20,
  "talent_pow": 0,
  "talent_guts": 0,
  "talent_wiz": 10
}
```

**Example Characters:**
- Special Week (1001) - 4 cards
- Silence Suzuka (1002) - 2 cards
- Tokai Teio (1003) - 3 cards
- Gold Ship (1007) - 3 cards
- Vodka (1008) - 2 cards

### **Skill Data**

| Table | Rows | Description |
|-------|------|-------------|
| `skill_data` | 1,847 | All skills in the game |
| `skill_set` | 4,132 | Skill groupings/combinations |
| `text_data` (cat=47) | 1,847 | Skill names (Japanese) |
| `available_skill_set` | 1,596 | Skills available to specific characters |

**Skill Categories:**
- Unique skills (character-specific)
- Normal skills (learnable)
- Inheritable skills
- Evolution skills

**Skill Structure:**
```json
{
  "id": 10071,
  "rarity": 3,
  "grade_value": 240,
  "skill_category": 5,
  "condition_1": "distance_rate>=50&distance_rate<=60&order_rate>50"
}
```

### **Support Card Data**

| Table | Rows | Description |
|-------|------|-------------|
| `support_card_data` | 329 | Support cards |
| `text_data` (cat=75) | 329 | Support card names (Japanese) |

**Support Card Types:**
1. Speed (スピード)
2. Stamina (スタミナ)
3. Power (パワー)
4. Guts (根性)
5. Wisdom (賢さ)
6. Friend (友人)

### **Race Data**

| Table | Rows | Description |
|-------|------|-------------|
| `race` | 2,386 | All races in the game |
| `race_instance` | 2,834 | Race instances/schedules |
| `race_track` | 16 | Race tracks/courses |
| `legend_race` | 106 | Special legend races |
| `daily_race` | 10 | Daily race types |

### **Story Data**

| Table | Rows | Description |
|-------|------|-------------|
| `single_mode_story_data` | 15,569 | Story mode events |
| `chara_story_data` | 833 | Character-specific stories |
| `main_story_data` | 169 | Main story chapters |
| `story_event_data` | 48 | Special story events |

### **Text/Translation Data**

| Table | Rows | Description |
|-------|------|-------------|
| `text_data` | 82,950 | All in-game text (names, descriptions, dialogue) |
| `character_system_text` | 29,309 | System/UI text |

**Text Data Categories:**
- Category 6: Character names
- Category 47: Skill names
- Category 75: Support card names
- Category 170: Skill descriptions
- And many more...

---

## 🔄 Extracted Data Files

We've pre-extracted key data for easier use:

### `data/characters.json`
- **119 characters** with English translations (77 complete, 42 pending)
- Includes: chara_id, name (JP/EN), birth date, color, card list

Example:
```json
{
  "chara_id": 1001,
  "name_jp": "スペシャルウィーク",
  "name_en": "Special Week",
  "birth_date": "1995-05-02",
  "color": "FCA7FF",
  "cards": [...]
}
```

### `data/skills.json`
- **100 top skills** (sorted by rarity and grade)
- Includes: id, rarity, grade_value, name_jp

---

## 🎨 How to Use This Data

### 1. **Query the Database Directly**
```python
from utils.db_reader import MasterDBReader

db = MasterDBReader()
db.connect()

# Get all SSR characters
ssr_cards = db.query("SELECT * FROM card_data WHERE default_rarity = 3")

# Get character by name
special_week = db.query("""
  SELECT c.*, t.text as name
  FROM chara_data c
  JOIN text_data t ON t.category = 6 AND t.[index] = c.id
  WHERE c.id = 1001
""")

db.close()
```

### 2. **Use Pre-extracted JSON Files**
```python
import json

with open('./data/characters.json') as f:
    characters = json.load(f)

# Find character
special_week = next(c for c in characters if c['chara_id'] == 1001)
print(special_week['name_en'])  # "Special Week"
```

### 3. **Explore via Discord Bot**
```
!dbstatus              # Check database connection
!dbtables skill        # Find skill-related tables
!dbschema card_data    # See card_data structure
!dbquery SELECT * FROM card_data LIMIT 5
```

---

## 📝 Important Tables by Feature

### Training/育成 (Scenario Mode)
- `single_mode_scenario` - Training scenarios (URA, Aoharu, etc.)
- `single_mode_training` - Training commands
- `single_mode_npc` - NPCs in training mode
- `single_mode_route` - Character routes

### Gacha/ガチャ
- `gacha_data` - Gacha banners
- `gacha_available` - Available cards per gacha
- `gacha_exchange` - Gacha exchange items

### Events/イベント
- `story_event_data` - Special events
- `campaign_data` - Campaign information
- `login_bonus_data` - Login bonuses

### Items/アイテム
- `item_data` - All items (647 items)
- `item_exchange` - Item exchange rates
- `piece_data` - Character pieces

---

## 🌐 Translation Status

### Character Names
- ✅ **77/119 (64.7%)** have English translations
- ❓ **42/119 (35.3%)** need translation

**Most translations are:**
- Official character names from the English release
- Romanized names where official translations don't exist

### Skills & Support Cards
- ⚠️ Currently in Japanese
- Translation mapping needed
- Can be crowd-sourced or pulled from wikis

---

## 🚀 Next Steps for Bot Development

### Immediate (Ready to Use)
1. ✅ Character lookup by name (English/Japanese)
2. ✅ Character cards and rarity info
3. ✅ Basic character stats

### Short Term (Needs Work)
1. 🔧 Skill database with descriptions
2. 🔧 Support card recommendations
3. 🔧 Race calendar/schedule
4. 🔧 Complete English translations

### Long Term (Advanced Features)
1. 🎯 Training optimizer
2. 🎯 Team builder
3. 🎯 Gacha simulator with real rates
4. 🎯 Event tracking
5. 🎯 Character progression calculator

---

## ⚠️ Known Limitations

1. **Japanese Text**: Most text is in Japanese, requires translation layer
2. **Complex Relationships**: Many tables have foreign keys requiring joins
3. **Game Updates**: Database needs to be re-downloaded when game updates
4. **Archived Source**: UmaMusumeMetaMasterMDB is archived (read-only)

---

## 🔗 Useful Resources

- **Database Source**: https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB
- **Game Wikis**:
  - https://game8.co/games/Umamusume-Pretty-Derby
  - https://gametora.com/umamusume
- **Community**: Discord servers, Reddit communities

---

## 📊 Database Statistics

```
Total Tables:     574
Total Rows:       ~500,000+
Database Size:    ~100MB
Languages:        Japanese (primary)
Last Updated:     2025 (check GitHub for latest)
```

---

**Happy training, Trainer! 🏇✨**
