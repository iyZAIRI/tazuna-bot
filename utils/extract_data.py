"""
Extract character, skill, and support card data from master.mdb.
This script helps identify the relevant tables and extract game data.
"""
import sys
from pathlib import Path
from db_reader import MasterDBReader
import json
import logging

logger = logging.getLogger('UmaMusumeBot.Extractor')

def explore_character_tables(db: MasterDBReader):
    """
    Find and explore tables that might contain character data.

    Args:
        db: MasterDBReader instance
    """
    print("\n" + "="*60)
    print("🔍 Searching for Character Tables...")
    print("="*60)

    tables = db.get_tables()

    # Common keywords for character tables
    character_keywords = [
        'card', 'chara', 'character', 'uma', 'horse', 'girl',
        'name', 'data', 'text'
    ]

    potential_tables = []
    for table in tables:
        table_lower = table.lower()
        if any(keyword in table_lower for keyword in character_keywords):
            potential_tables.append(table)

    print(f"\n📋 Found {len(potential_tables)} potential character-related tables:\n")

    for table in potential_tables:
        result = db.query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count'] if result else 0

        # Get sample data
        sample = db.get_table_data(table, limit=1)

        print(f"  • {table} ({count} rows)")

        if sample:
            print(f"    Columns: {', '.join(sample[0].keys())}")

    return potential_tables

def explore_skill_tables(db: MasterDBReader):
    """
    Find and explore tables that might contain skill data.

    Args:
        db: MasterDBReader instance
    """
    print("\n" + "="*60)
    print("🔍 Searching for Skill Tables...")
    print("="*60)

    tables = db.get_tables()

    # Common keywords for skill tables
    skill_keywords = [
        'skill', 'ability', 'effect', 'passive', 'active'
    ]

    potential_tables = []
    for table in tables:
        table_lower = table.lower()
        if any(keyword in table_lower for keyword in skill_keywords):
            potential_tables.append(table)

    print(f"\n📋 Found {len(potential_tables)} potential skill-related tables:\n")

    for table in potential_tables:
        result = db.query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count'] if result else 0

        # Get sample data
        sample = db.get_table_data(table, limit=1)

        print(f"  • {table} ({count} rows)")

        if sample:
            print(f"    Columns: {', '.join(sample[0].keys())}")

    return potential_tables

def explore_support_tables(db: MasterDBReader):
    """
    Find and explore tables that might contain support card data.

    Args:
        db: MasterDBReader instance
    """
    print("\n" + "="*60)
    print("🔍 Searching for Support Card Tables...")
    print("="*60)

    tables = db.get_tables()

    # Common keywords for support tables
    support_keywords = [
        'support', 'card', 'deck', 'assist'
    ]

    potential_tables = []
    for table in tables:
        table_lower = table.lower()
        if any(keyword in table_lower for keyword in support_keywords):
            potential_tables.append(table)

    print(f"\n📋 Found {len(potential_tables)} potential support-related tables:\n")

    for table in potential_tables:
        result = db.query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count'] if result else 0

        # Get sample data
        sample = db.get_table_data(table, limit=1)

        print(f"  • {table} ({count} rows)")

        if sample:
            print(f"    Columns: {', '.join(sample[0].keys())}")

    return potential_tables

def export_sample_data(db: MasterDBReader, table_name: str, output_dir: str = "./data/samples"):
    """
    Export sample data from a table for examination.

    Args:
        db: MasterDBReader instance
        table_name: Name of the table to export
        output_dir: Directory to save sample data
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Export first 10 rows as sample
    sample_data = db.get_table_data(table_name, limit=10)

    if sample_data:
        output_file = output_path / f"{table_name}_sample.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        print(f"✅ Exported sample from {table_name} to {output_file}")
    else:
        print(f"❌ No data found in {table_name}")

def interactive_explore(db: MasterDBReader):
    """
    Interactive exploration mode.

    Args:
        db: MasterDBReader instance
    """
    print("\n" + "="*60)
    print("🎮 Interactive Exploration Mode")
    print("="*60)
    print("\nCommands:")
    print("  tables              - List all tables")
    print("  explore <table>     - Show table details")
    print("  sample <table> [n]  - Show n rows from table (default: 5)")
    print("  export <table>      - Export table to JSON")
    print("  quit                - Exit")
    print("="*60)

    while True:
        try:
            command = input("\n> ").strip().split()

            if not command:
                continue

            cmd = command[0].lower()

            if cmd == 'quit' or cmd == 'exit':
                break

            elif cmd == 'tables':
                tables = db.get_tables()
                for i, table in enumerate(tables, 1):
                    result = db.query(f"SELECT COUNT(*) as count FROM {table}")
                    count = result[0]['count'] if result else 0
                    print(f"{i:3}. {table:40} ({count:6} rows)")

            elif cmd == 'explore' and len(command) > 1:
                table = command[1]
                schema = db.get_table_schema(table)
                print(f"\n📋 Schema for {table}:")
                for col in schema:
                    pk = " [PK]" if col['pk'] else ""
                    print(f"  {col['name']:30} {col['type']:15}{pk}")

            elif cmd == 'sample' and len(command) > 1:
                table = command[1]
                limit = int(command[2]) if len(command) > 2 else 5
                data = db.get_table_data(table, limit=limit)
                print(f"\n📄 Sample data from {table}:")
                print(json.dumps(data, indent=2, ensure_ascii=False))

            elif cmd == 'export' and len(command) > 1:
                table = command[1]
                output_file = f"./data/{table}.json"
                db.export_table_to_json(table, output_file)
                print(f"✅ Exported to {output_file}")

            else:
                print("❌ Unknown command or missing arguments")

        except KeyboardInterrupt:
            print("\n👋 Exiting...")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

def main():
    """Main function."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db = MasterDBReader()

    if not db.connect():
        print("\n❌ Failed to connect to database!")
        print("💡 Make sure you've downloaded the master.mdb file:")
        print("   python utils/download_masterdb.py")
        return

    print("\n🏇 Uma Musume Data Extractor")
    print("="*60)

    # Explore different data types
    char_tables = explore_character_tables(db)
    skill_tables = explore_skill_tables(db)
    support_tables = explore_support_tables(db)

    # Export sample data from interesting tables
    print("\n" + "="*60)
    print("📦 Exporting Sample Data...")
    print("="*60 + "\n")

    all_interesting = set(char_tables + skill_tables + support_tables)
    for table in list(all_interesting)[:10]:  # Limit to first 10 to avoid spam
        export_sample_data(db, table)

    # Launch interactive mode
    print("\n" + "="*60)
    response = input("\n💡 Launch interactive exploration mode? (y/n): ")

    if response.lower() == 'y':
        interactive_explore(db)

    db.close()
    print("\n👋 Done!")

if __name__ == "__main__":
    main()
