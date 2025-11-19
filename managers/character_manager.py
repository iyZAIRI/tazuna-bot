"""Character manager for loading and querying character data."""
import sys
from pathlib import Path
from typing import List, Optional, Dict
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader
from models.character import Character, CharacterCard

logger = logging.getLogger('UmaMusumeBot.CharacterManager')

class CharacterManager:
    """Manages character data from the database."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        """
        Initialize the character manager.

        Args:
            db_path: Path to the master.mdb file
        """
        self.db_path = db_path
        self.db = MasterDBReader(db_path)
        self.characters: Dict[int, Character] = {}
        self.name_index: Dict[str, int] = {}  # name -> chara_id
        self._loaded = False

    def load(self) -> bool:
        """
        Load character data from database.

        Returns:
            bool: True if successful
        """
        if self._loaded:
            return True

        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False

        try:
            # Query for all characters with their cards
            query = """
            SELECT
                c.id as card_id,
                c.chara_id,
                c.default_rarity,
                c.running_style,
                c.talent_speed,
                c.talent_stamina,
                c.talent_pow,
                c.talent_guts,
                c.talent_wiz,
                cd.birth_year,
                cd.birth_month,
                cd.birth_day,
                cd.image_color_main,
                cd.image_color_sub,
                cd.height,
                t.text as name
            FROM card_data c
            JOIN chara_data cd ON c.chara_id = cd.id
            LEFT JOIN text_data t ON t.category = 6 AND t.[index] = c.chara_id
            ORDER BY c.chara_id, c.default_rarity DESC
            """

            results = self.db.query(query)

            # Group by character
            for row in results:
                chara_id = row['chara_id']

                # Create character if doesn't exist
                if chara_id not in self.characters:
                    char = Character(
                        chara_id=chara_id,
                        name=row['name'] or f"Character {chara_id}",
                        name_en=row['name'],  # Will be EN if using EN database
                        name_jp=row['name'],  # Will be JP if using JP database
                        birth_year=row['birth_year'],
                        birth_month=row['birth_month'],
                        birth_day=row['birth_day'],
                        color_main=row['image_color_main'],
                        color_sub=row['image_color_sub'],
                        height=row['height'],
                        cards=[]
                    )
                    self.characters[chara_id] = char

                    # Index by name (lowercase for search)
                    if row['name']:
                        self.name_index[row['name'].lower()] = chara_id

                # Add card
                card = CharacterCard(
                    card_id=row['card_id'],
                    chara_id=chara_id,
                    rarity=row['default_rarity'],
                    running_style=row['running_style'],
                    talent_speed=row['talent_speed'],
                    talent_stamina=row['talent_stamina'],
                    talent_power=row['talent_pow'],
                    talent_guts=row['talent_guts'],
                    talent_wisdom=row['talent_wiz']
                )
                self.characters[chara_id].cards.append(card)

            self._loaded = True
            logger.info(f"Loaded {len(self.characters)} characters")
            return True

        except Exception as e:
            logger.error(f"Failed to load characters: {e}")
            return False

    def get_by_id(self, chara_id: int) -> Optional[Character]:
        """Get character by ID."""
        if not self._loaded:
            self.load()
        return self.characters.get(chara_id)

    def get_by_name(self, name: str) -> Optional[Character]:
        """
        Get character by name (case-insensitive).

        Args:
            name: Character name (partial match supported)
        """
        if not self._loaded:
            self.load()

        name_lower = name.lower()

        # Exact match
        if name_lower in self.name_index:
            return self.characters[self.name_index[name_lower]]

        # Partial match
        for indexed_name, chara_id in self.name_index.items():
            if name_lower in indexed_name:
                return self.characters[chara_id]

        return None

    def get_all(self) -> List[Character]:
        """Get all characters."""
        if not self._loaded:
            self.load()
        return list(self.characters.values())

    def search(self, query: str) -> List[Character]:
        """
        Search for characters by name.

        Args:
            query: Search query

        Returns:
            List of matching characters
        """
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for name, chara_id in self.name_index.items():
            if query_lower in name:
                results.append(self.characters[chara_id])

        return results

    def get_random(self) -> Optional[Character]:
        """Get a random character."""
        if not self._loaded:
            self.load()

        if not self.characters:
            return None

        import random
        return random.choice(list(self.characters.values()))

    def get_by_rarity(self, rarity: int) -> List[Character]:
        """Get characters that have cards of specified rarity."""
        if not self._loaded:
            self.load()

        results = []
        for char in self.characters.values():
            if any(card.rarity == rarity for card in char.cards):
                results.append(char)

        return results

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
