"""
Read and explore the master.mdb SQLite database.
"""
import sqlite3
import json
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger('UmaMusumeBot.DBReader')

class MasterDBReader:
    """Reader for Uma Musume master.mdb database."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        """
        Initialize the database reader.

        Args:
            db_path: Path to the master.mdb file
        """
        self.db_path = Path(db_path)
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> bool:
        """
        Connect to the database.

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            if not self.db_path.exists():
                logger.error(f"Database file not found: {self.db_path}")
                return False

            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row  # Enable column access by name
            logger.info(f"Connected to database: {self.db_path}")
            return True

        except sqlite3.Error as e:
            logger.error(f"Failed to connect to database: {e}")
            return False

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def get_tables(self) -> List[str]:
        """
        Get list of all tables in the database.

        Returns:
            List of table names
        """
        if not self.conn:
            logger.error("Not connected to database")
            return []

        try:
            cursor = self.conn.cursor()
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = [row[0] for row in cursor.fetchall()]
            return tables

        except sqlite3.Error as e:
            logger.error(f"Failed to get tables: {e}")
            return []

    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Get schema information for a table.

        Args:
            table_name: Name of the table

        Returns:
            List of column information dictionaries
        """
        if not self.conn:
            logger.error("Not connected to database")
            return []

        try:
            cursor = self.conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = []
            for row in cursor.fetchall():
                columns.append({
                    'cid': row[0],
                    'name': row[1],
                    'type': row[2],
                    'notnull': row[3],
                    'default': row[4],
                    'pk': row[5]
                })
            return columns

        except sqlite3.Error as e:
            logger.error(f"Failed to get schema for {table_name}: {e}")
            return []

    def query(self, sql: str, params: tuple = ()) -> List[Dict[str, Any]]:
        """
        Execute a SQL query and return results as dictionaries.

        Args:
            sql: SQL query string
            params: Query parameters (optional)

        Returns:
            List of row dictionaries
        """
        if not self.conn:
            logger.error("Not connected to database")
            return []

        try:
            cursor = self.conn.cursor()
            cursor.execute(sql, params)

            # Convert rows to dictionaries
            columns = [description[0] for description in cursor.description]
            results = []
            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))

            return results

        except sqlite3.Error as e:
            logger.error(f"Query failed: {e}")
            return []

    def get_table_data(self, table_name: str, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get all data from a table.

        Args:
            table_name: Name of the table
            limit: Maximum number of rows (optional)

        Returns:
            List of row dictionaries
        """
        sql = f"SELECT * FROM {table_name}"
        if limit:
            sql += f" LIMIT {limit}"
        return self.query(sql)

    def export_table_to_json(self, table_name: str, output_path: str):
        """
        Export a table to a JSON file.

        Args:
            table_name: Name of the table
            output_path: Path to save JSON file
        """
        data = self.get_table_data(table_name)

        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.info(f"Exported {len(data)} rows from {table_name} to {output_path}")

        except IOError as e:
            logger.error(f"Failed to write JSON file: {e}")

def main():
    """Main function for CLI exploration."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    db = MasterDBReader()

    if not db.connect():
        print("❌ Failed to connect to database")
        print("💡 Try running: python utils/download_masterdb.py")
        return

    print("\n" + "="*60)
    print("🗄️  Uma Musume Master Database Explorer")
    print("="*60)

    tables = db.get_tables()
    print(f"\n📋 Found {len(tables)} tables:\n")

    for i, table in enumerate(tables, 1):
        # Get row count
        result = db.query(f"SELECT COUNT(*) as count FROM {table}")
        count = result[0]['count'] if result else 0
        print(f"{i:3}. {table:40} ({count:6} rows)")

    print("\n" + "="*60)
    print("\n💡 To explore a table, use:")
    print("   python -c \"from utils.db_reader import MasterDBReader; db = MasterDBReader(); db.connect(); print(db.get_table_data('TABLE_NAME', limit=5))\"")
    print("\n💡 To export a table to JSON:")
    print("   python -c \"from utils.db_reader import MasterDBReader; db = MasterDBReader(); db.connect(); db.export_table_to_json('TABLE_NAME', 'output.json')\"")

    db.close()

if __name__ == "__main__":
    main()
