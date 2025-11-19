# Tazuna Bot - Development Notes

A Discord bot for Uma Musume Pretty Derby using the master.mdb game database.

## 🎯 Current Implementation

### Architecture
- **3-layer modular architecture**: Models → Managers → Cogs
- **Discord.py 2.3.2+** with slash commands (`/` commands)
- **SQLite database** (master.mdb from SimpleSandman/UmaMusumeMetaMasterMDB)
- **Virtual environment** for dependency isolation

### Currently Implemented Features

#### Characters (`/character`, `/characters`, `/randomchar`, `/ssrchars`)
- Character lookup by name
- Character listing with pagination
- Random character selector
- SSR character filter
- **Display data**: Name (EN/JP), birthday, ID, card count, running style, base talents
- **Images**: Character card images from GameTora CDN
  - Pattern: `https://gametora.com/images/umamusume/characters/chara_stand_{chara_id}_{card_id}.png`

#### Skills (`/skill`, `/skills`, `/randomskill`)
- Skill lookup by ID
- Skill listing by rarity
- Random skill selector
- **Display data**: Skill ID, description, rarity, cooldown, grade value

#### Support Cards (`/supportcard`, `/supportcards`, `/randomsupport`)
- Support card lookup by ID
- Support card listing by type/rarity
- Random support card selector
- **Display data**: Card ID, character, type, rarity
- **Missing**: Card names, images, effects, bonuses

#### Races (`/race`, `/races`, `/randomrace`)
- Race lookup
- Race listing by grade
- Random race selector
- **Display data**: Race name, grade, distance, ground type, track

### Models Structure
- `models/character.py` - Character and CharacterCard dataclasses
- `models/skill.py` - Skill dataclass
- `models/card.py` - SupportCard dataclass
- `models/race.py` - Race dataclass

### Managers Structure
- `managers/character_manager.py` - Character data access with caching
- `managers/skill_manager.py` - Skill data access
- `managers/support_card_manager.py` - Support card data access
- `managers/race_manager.py` - Race data access (with JOIN to race_course_set)

### Database Configuration
- `DATABASE_PATH` - Path to master.mdb (default: `./data/master.mdb`)
- `DATABASE_LANGUAGE` - Language preference: 'en', 'jp', or 'auto'
- Database downloaded via `utils/download_masterdb.py`

## 📊 Database Overview

The master.mdb contains **574 tables** with extensive game data:

### What We're Currently Using
- `card_data` - Character cards (119 characters, multiple cards each)
- `chara_data` - Character information (birth dates, colors)
- `skill_data` - Skills (1,847 skills)
- `support_card_data` - Support cards (495 cards)
- `race` - Race information (2,386 races)
- `race_course_set` - Race track details (joined with race table)
- `text_data` - Localized text (82,950 entries across categories)

### What We're NOT Using (But Available)

#### 📖 Stories & Events (47 tables, 15,569+ stories)
- `single_mode_story_data` - Story scenarios
- `story_event_point_reward` - Event rewards
- `story_event_mission` - Event missions
- `home_story_trigger` - Home screen story triggers
- `event_motion_data` - Event animations

**Potential commands**: `/stories`, `/events`, `/story <id>`

#### 🏋️ Training System (29 tables)
- `training_challenge_score` - Training challenge data
- `single_mode_training_effect` - Training effects
- `single_mode_training` - Training scenarios
- `training_report_normal_reward` / `training_report_special_reward` - Training rewards

**Potential commands**: `/training`, `/scenarios`

#### 🎵 Live Performances (10 tables, 173 songs)
- `live_data` - Live performance information (173 songs)
- `jukebox_music_data` - Jukebox songs (165 tracks)
- `single_mode_live_square` - Live performance bonuses
- `live_dress_restrict_data` - Costume restrictions

**Potential commands**: `/live`, `/songs`, `/music`

#### 👗 Costumes/Dresses (4 tables, 452 dresses)
- `dress_data` - Dress/costume information
- `mob_dress_color_set` - Color variations
- `audience_dress_color_set` - Audience outfits

**Potential commands**: `/dresses`, `/costumes`, `/dress <id>`

#### 🎁 Items & Shop (17 tables, 647 items)
- `item_data` - Item information
- `item_exchange` - Item exchange data (5,226 exchanges)
- `piece_data` - Piece/fragment data (229 pieces)
- `single_mode_free_shop_effect` - Shop bonuses

**Potential commands**: `/items`, `/shop`, `/exchange`

#### 🎰 Gacha/Banners (13 tables, 547 banners)
- `gacha_data` - Gacha banner information
- `gacha_available` - Gacha availability (83,194 records!)
- `select_pickup` - Pickup selections
- `banner_data` - Banner art/info
- `gacha_stepup` - Step-up gacha mechanics

**Potential commands**: `/gacha`, `/banners`, `/current`, `/history`

#### 🏆 Missions (4 tables, 7,809 missions)
- `mission_data` - Mission objectives
- `live_permission_data` - Live unlock conditions
- `collect_raid_mission` - Raid missions

**Potential commands**: `/missions`, `/achievements`

#### 🧬 Breeding/Succession System
- `succession_factor_effect` - Inheritance effects (5,808 records)
- `succession_relation` - Inheritance relationships (2,680)
- `succession_factor` - Inheritance factors (2,274)

**Potential commands**: `/breeding`, `/inheritance`, `/factors`

#### 🏃 Champions/Rivals
- `single_mode_rival` - Rival data (5,806 rivals)
- `single_mode_npc` - NPC data (3,198 NPCs)
- `champions_news_chara_comment` - Character comments
- `champions_reward_rate` - Reward rates

**Potential commands**: `/rivals`, `/npcs`, `/champions`

#### 📋 Text Localization (82,950 entries)
Text data categories discovered:
- Category 6: Support card names (157 entries)
- Category 10: Skill descriptions (645 entries)
- Category 13: Gacha banners (547)
- Category 14: Dresses (452)
- Category 23: Items (647)
- Category 30: Race names
- And many more...

**Usage**: Need to identify correct category for each data type

## 🚀 Enhancement Opportunities

### Immediate Improvements

#### 1. Support Card Enhancement
**Current state**: Basic info only (ID, character, type, rarity)

**Missing data available**:
- ❌ Card names (join with text_data category 6)
- ❌ Card images (need CDN URL pattern from GameTora)
- ❌ Training bonuses (support_card_effect_table - 4,460 rows)
- ❌ Unique effects (support_card_unique_effect - 360 effects)
- ❌ Skills granted (via skill_set_id)
- ❌ Limit break info
- ❌ Exchange costs
- ❌ Release dates

**Tables to use**:
- `support_card_effect_table` - Training bonuses by level
- `support_card_unique_effect` - Passive abilities
- `skill_set` - Skills the card teaches
- `text_data` (category 6) - Card names

#### 2. Character Enhancement
**Current state**: Good basic info with images

**Missing data available**:
- ❌ Character stories
- ❌ Voice actor information
- ❌ Character-specific events
- ❌ Home screen dialogue
- ❌ Character height (available in chara_data)

#### 3. Race Enhancement
**Current state**: Basic race info

**Missing data available**:
- ❌ Race commentary/jikkyo (6,128 base messages)
- ❌ Race conditions
- ❌ Legend race NPCs (1,793)
- ❌ Race rewards
- ❌ Track-specific details

#### 4. Skill Enhancement
**Current state**: Basic skill info

**Missing data available**:
- ❌ Skill upgrade paths (skill_upgrade_condition - 1,562)
- ❌ Skill evolution requirements
- ❌ Skill descriptions (text_data category 10)
- ❌ Skill compatibility
- ❌ Skill point costs (single_mode_skill_need_point - 1,006)

### New Feature Ideas

#### 🎮 Interactive Features
- **Gacha simulator** - Simulate pulls using gacha_data
- **Team builder** - Build support card decks
- **Character comparison** - Compare stats side-by-side
- **Breeding calculator** - Calculate inheritance outcomes
- **Training planner** - Plan training scenarios

#### 📊 Information Commands
- **Daily/Weekly rotation** - Check current events/gachas
- **Database search** - Search across all content
- **Tier lists** - Community-driven rankings
- **News feed** - Parse champions_news data

#### 🎨 Visual Enhancements
- **Embed improvements** - Better formatting, more data
- **Image galleries** - Character/dress galleries
- **Animation previews** - Link to animation data
- **Color theming** - Use character colors throughout

## 🔧 Technical Notes

### Database Patterns Discovered

#### Joining Tables
Race data requires joining multiple tables:
```sql
SELECT r.id, r.grade, rcs.distance, rcs.ground, t.text as name
FROM race r
LEFT JOIN race_course_set rcs ON r.course_set = rcs.id
LEFT JOIN text_data t ON t.category = 30 AND t.[index] = r.id
```

#### Text Localization
Text data uses category + index pattern:
```sql
LEFT JOIN text_data t ON t.category = [category_id] AND t.[index] = [item_id]
```

#### Character Images
GameTora CDN pattern:
```
https://gametora.com/images/umamusume/characters/chara_stand_{chara_id}_{card_id}.png
```

#### Support Card Images
Pattern not yet discovered. Potential patterns to test:
- `https://gametora.com/images/umamusume/support_cards/support_card_{card_id}.png`
- `https://gametora.com/images/umamusume/supports/support_{card_id}.png`
- `https://gametora.com/images/umamusume/supports/{card_id}.png`

### Known Issues & Fixes

#### Issue: Race table missing columns
**Problem**: `race` table doesn't have `race_number`, `distance`, or `ground` columns directly
**Solution**: JOIN with `race_course_set` table

#### Issue: Command conflicts
**Problem**: Multiple cogs defining same command names
**Solution**: Backed up old `cogs/umamusume.py` to prevent conflicts

#### Issue: Privileged intents
**Problem**: Bot requires MESSAGE_CONTENT_INTENT enabled
**Solution**: Enable in Discord Developer Portal → Bot → Privileged Gateway Intents

### OAuth2 & Permissions

**Required OAuth2 Scopes**:
- `bot` - Add bot to server
- `applications.commands` - Enable slash commands

**Required Bot Permissions**:
- Send Messages
- Embed Links
- Use Slash Commands
- Read Message History (optional)

### Data Sources

- **Database**: [SimpleSandman/UmaMusumeMetaMasterMDB](https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB)
- **Images**: [GameTora](https://gametora.com)
- **Community API**: [SimpleSandman/UmaMusumeAPI](https://github.com/SimpleSandman/UmaMusumeAPI)
- **Asset Tools**:
  - [UmaViewer](https://github.com/katboi01/UmaViewer)
  - [UmaMusumeToolbox](https://github.com/SimpleSandman/UmaMusumeToolbox)

## 📝 Development Workflow

### Adding a New Feature

1. **Explore database tables** - Use `utils/extract_data.py` interactive mode
2. **Create model** - Define dataclass in `models/`
3. **Create manager** - Build data access layer in `managers/`
4. **Create cog** - Add slash commands in `cogs/`
5. **Test** - Run bot and test commands
6. **Commit** - Use descriptive commit messages

### Git Branch Naming
Pattern: `claude/{feature-description}-{session_id}`
Example: `claude/add-character-images-01QogtdCAkPAiRjenjTS12EK`

### Commit Message Format
```
Add [feature] to [area]

- Bullet point of changes
- Another change
- Technical details if needed
```

## 🎯 Priority Roadmap

### Phase 1: Core Content (Current)
- [x] Characters with images
- [x] Skills
- [x] Basic support cards
- [x] Races
- [ ] Support card images
- [ ] Support card effects

### Phase 2: Enhanced Data
- [ ] Support card training bonuses
- [ ] Support card unique effects
- [ ] Skill upgrade paths
- [ ] Character stories
- [ ] Race commentary

### Phase 3: New Systems
- [ ] Live/Music system
- [ ] Costumes/Dresses
- [ ] Items & Shop
- [ ] Gacha/Banners
- [ ] Missions

### Phase 4: Interactive Features
- [ ] Gacha simulator
- [ ] Team builder
- [ ] Breeding calculator
- [ ] Training planner
- [ ] Search system

### Phase 5: Advanced Features
- [ ] User profiles
- [ ] Favorites system
- [ ] Notifications
- [ ] Analytics
- [ ] Admin tools

## 💡 Best Practices

1. **Always query database directly** - Don't rely on JSON exports
2. **Use caching in managers** - Load data once, cache results
3. **Join text_data for names** - Use appropriate category codes
4. **Handle missing data gracefully** - Some records may not have all fields
5. **Use defensive SQL** - LEFT JOIN instead of JOIN to avoid missing data
6. **Test with different languages** - Support EN/JP database variants
7. **Commit frequently** - Keep commits focused and atomic
8. **Document patterns** - Add notes when discovering new DB patterns

## 🔍 Useful Queries

### Find text category for an item type
```sql
SELECT DISTINCT category, COUNT(*) as count
FROM text_data
GROUP BY category
ORDER BY category;
```

### Explore table relationships
```sql
PRAGMA foreign_key_list(table_name);
```

### Sample data exploration
```sql
SELECT * FROM table_name LIMIT 5;
```

### Count records by type/category
```sql
SELECT type_column, COUNT(*) as count
FROM table_name
GROUP BY type_column;
```

## 📚 Resources

- [Discord.py Documentation](https://discordpy.readthedocs.io/)
- [Uma Musume Wiki](https://umamusu.wiki/)
- [GameTora Database](https://gametora.com/umamusume)
- [SimpleSandman's GitHub](https://github.com/SimpleSandman)

---

**Last Updated**: 2025-11-19
**Bot Version**: 2.0.0
**Database Version**: Check meta file in data/
