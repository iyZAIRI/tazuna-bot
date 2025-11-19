#!/usr/bin/env python3
"""
Create a character database by joining card_data, chara_data, and text_data.
"""
from utils.db_reader import MasterDBReader
import json

db = MasterDBReader()
db.connect()

print("🏇 Creating Uma Musume Character Database...\n")

# Get all characters with their card data
query = """
SELECT
    c.id as card_id,
    c.chara_id,
    c.default_rarity,
    c.running_style,
    cd.image_color_main,
    cd.birth_year,
    cd.birth_month,
    cd.birth_day,
    t.text as name_jp
FROM card_data c
JOIN chara_data cd ON c.chara_id = cd.id
LEFT JOIN text_data t ON t.category = 6 AND t.[index] = c.chara_id
ORDER BY c.chara_id, c.default_rarity DESC
"""

characters = db.query(query)

print(f"Found {len(characters)} character cards\n")

# Group by character
char_dict = {}
for char in characters:
    chara_id = char['chara_id']
    if chara_id not in char_dict:
        char_dict[chara_id] = {
            'chara_id': chara_id,
            'name_jp': char['name_jp'],
            'name_en': None,  # Will need translation
            'birth_date': f"{char['birth_year']}-{char['birth_month']:02d}-{char['birth_day']:02d}",
            'color': char['image_color_main'],
            'cards': []
        }

    char_dict[chara_id]['cards'].append({
        'card_id': char['card_id'],
        'rarity': char['default_rarity'],
        'running_style': char['running_style']
    })

# Convert to list
characters_list = list(char_dict.values())

print("Sample characters:")
for char in characters_list[:10]:
    print(f"  {char['chara_id']:4d} | {char['name_jp']:20s} | {len(char['cards'])} cards | {char['color']}")

# Save to JSON
output_file = './data/characters.json'
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(characters_list, f, indent=2, ensure_ascii=False)

print(f"\n✅ Saved {len(characters_list)} characters to {output_file}")

# Also create a skills database
print("\n🎯 Creating Skills Database...")

query_skills = """
SELECT
    s.id,
    s.rarity,
    s.grade_value,
    t.text as name_jp
FROM skill_data s
LEFT JOIN text_data t ON t.category = 47 AND t.[index] = s.id
WHERE s.rarity > 0
ORDER BY s.rarity DESC, s.grade_value DESC
LIMIT 100
"""

skills = db.query(query_skills)
skills_file = './data/skills.json'
with open(skills_file, 'w', encoding='utf-8') as f:
    json.dump(skills, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(skills)} top skills to {skills_file}")

db.close()
print("\n✨ Done!")
