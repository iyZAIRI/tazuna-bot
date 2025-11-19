#!/usr/bin/env python3
"""Simple database explorer for viewing tables and schemas."""
import sys
from utils.db_reader import MasterDBReader

def show_table_schema(db, table_name):
    """Show detailed schema for a table."""
    cursor = db.conn.cursor()
    cursor.execute(f'PRAGMA table_info({table_name})')

    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print(f"{'='*60}\n")

    columns = cursor.fetchall()
    print(f"{'Column':<30} {'Type':<15} {'Not Null':<10}")
    print("-" * 60)
    for col in columns:
        nullable = "NO" if col[3] else "YES"
        print(f"{col[1]:<30} {col[2]:<15} {nullable:<10}")

    # Show row count
    cursor.execute(f'SELECT COUNT(*) FROM {table_name}')
    count = cursor.fetchone()[0]
    print(f"\nTotal rows: {count}")

def show_sample_data(db, table_name, limit=5):
    """Show sample data from a table."""
    cursor = db.conn.cursor()
    cursor.execute(f'SELECT * FROM {table_name} LIMIT {limit}')

    rows = cursor.fetchall()
    cols = [desc[0] for desc in cursor.description]

    print(f"\n{'='*60}")
    print(f"SAMPLE DATA: {table_name} (showing {len(rows)} rows)")
    print(f"{'='*60}\n")

    for i, row in enumerate(rows, 1):
        print(f"Row {i}:")
        for col_name, value in zip(cols, row):
            print(f"  {col_name:<30} = {value}")
        print()

def search_tables(db, search_term):
    """Search for tables matching a term."""
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    matching = [t for t in tables if search_term.lower() in t.lower()]

    print(f"\n{'='*60}")
    print(f"TABLES MATCHING '{search_term}': {len(matching)} found")
    print(f"{'='*60}\n")

    for table in matching:
        cursor.execute(f'SELECT COUNT(*) FROM {table}')
        count = cursor.fetchone()[0]
        print(f"  • {table:<40} ({count:>6} rows)")

def main():
    """Main entry point."""
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python explore_db.py schema <table_name>     - Show table schema")
        print("  python explore_db.py sample <table_name> [n] - Show n sample rows")
        print("  python explore_db.py search <term>           - Search for tables")
        print("\nExamples:")
        print("  python explore_db.py schema card_data")
        print("  python explore_db.py sample card_data 10")
        print("  python explore_db.py search character")
        sys.exit(1)

    db = MasterDBReader()
    if not db.connect():
        print("❌ Failed to connect to database")
        sys.exit(1)

    command = sys.argv[1].lower()

    try:
        if command == "schema" and len(sys.argv) >= 3:
            table_name = sys.argv[2]
            show_table_schema(db, table_name)

        elif command == "sample" and len(sys.argv) >= 3:
            table_name = sys.argv[2]
            limit = int(sys.argv[3]) if len(sys.argv) >= 4 else 5
            show_sample_data(db, table_name, limit)

        elif command == "search" and len(sys.argv) >= 3:
            search_term = sys.argv[2]
            search_tables(db, search_term)

        else:
            print("❌ Invalid command or missing arguments")
            sys.exit(1)

    finally:
        db.close()

if __name__ == "__main__":
    main()
