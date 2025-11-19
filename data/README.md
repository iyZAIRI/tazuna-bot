# Data Directory

This directory contains the Uma Musume game database and extracted data.

## Quick Start

### 1. Download the master.mdb Database

```bash
python utils/download_masterdb.py
```

This will download the `master.mdb` file from the [UmaMusumeMetaMasterMDB](https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB) repository.

### 2. Explore the Database

```bash
python utils/db_reader.py
```

This will show you all available tables and their row counts.

### 3. Extract Game Data

```bash
python utils/extract_data.py
```

This script helps you:
- Find character-related tables
- Find skill-related tables
- Find support card tables
- Export sample data
- Interactive exploration mode

## Database Structure

The `master.mdb` file is an SQLite database containing all game data including:
- Character data (Uma Musume cards)
- Support cards
- Skills and abilities
- Race information
- Training scenarios
- Item data
- And much more!

## Usage Examples

### Export a Specific Table

```python
from utils.db_reader import MasterDBReader

db = MasterDBReader()
db.connect()

# Export a table to JSON
db.export_table_to_json('table_name', './data/table_name.json')

db.close()
```

### Query Custom Data

```python
from utils.db_reader import MasterDBReader

db = MasterDBReader()
db.connect()

# Run a custom query
results = db.query("SELECT * FROM table_name WHERE condition = ?", (value,))

for row in results:
    print(row)

db.close()
```

## Files

- `master.mdb` - Main game database (SQLite format)
- `meta` - Metadata file from the repository
- `samples/` - Sample data exports for exploration
- `*.json` - Extracted game data in JSON format

## Notes

- The master.mdb file is regularly updated by the community when the game updates
- Table names and structures may change between game versions
- The database contains Japanese text - you may need to handle encoding properly
- Some tables have foreign key relationships - explore carefully!

## Tips

1. **Find the right tables**: Use `extract_data.py` to search for relevant tables
2. **Check the schema**: Use `db_reader.py` to see column names and types
3. **Export samples**: Look at a few rows before exporting entire tables
4. **Cross-reference**: Some data requires joining multiple tables

## Data Sources

- Database: [UmaMusumeMetaMasterMDB](https://github.com/SimpleSandman/UmaMusumeMetaMasterMDB)
- Community tools: [SimpleSandman's repos](https://github.com/SimpleSandman)

## Legal

This is for educational and fan purposes only. Uma Musume Pretty Derby is owned by Cygames.
