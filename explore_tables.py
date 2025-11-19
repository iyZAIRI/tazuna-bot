#!/usr/bin/env python3
"""Quick script to explore key database tables."""
from utils.db_reader import MasterDBReader
import json

db = MasterDBReader()
db.connect()

# Explore key tables
tables = ['card_data', 'chara_data', 'skill_data', 'support_card_data']

for table in tables:
    print('\n' + '='*60)
    print(f'Table: {table}')
    print('='*60)

    # Get schema
    schema = db.get_table_schema(table)
    col_names = [c['name'] for c in schema]
    print(f'Columns ({len(schema)}):')
    print(', '.join(col_names[:20]))
    if len(col_names) > 20:
        print(f'... and {len(col_names) - 20} more')

    # Get sample data
    sample = db.get_table_data(table, limit=2)
    if sample:
        print(f'\nSample data (first 2 rows):')
        output = json.dumps(sample, indent=2, ensure_ascii=False)
        if len(output) > 2000:
            output = output[:2000] + '\n... (truncated)'
        print(output)

db.close()
