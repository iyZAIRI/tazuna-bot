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
            db_path: Path to the master.mdb file (English version)
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
            # Query for all characters with their cards and base stats
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
                cr_default.speed as base_speed,
                cr_default.stamina as base_stamina,
                cr_default.pow as base_pow,
                cr_default.guts as base_guts,
                cr_default.wiz as base_wiz,
                cr_max.speed as max_base_speed,
                cr_max.stamina as max_base_stamina,
                cr_max.pow as max_base_pow,
                cr_max.guts as max_base_guts,
                cr_max.wiz as max_base_wiz,
                cr_default.proper_distance_short as apt_distance_short,
                cr_default.proper_distance_mile as apt_distance_mile,
                cr_default.proper_distance_middle as apt_distance_middle,
                cr_default.proper_distance_long as apt_distance_long,
                cr_default.proper_running_style_nige as apt_style_front_runner,
                cr_default.proper_running_style_senko as apt_style_pace_chaser,
                cr_default.proper_running_style_sashi as apt_style_late,
                cr_default.proper_running_style_oikomi as apt_style_end_closer,
                cr_default.proper_ground_turf as apt_ground_turf,
                cr_default.proper_ground_dirt as apt_ground_dirt,
                t_card.text as card_title,
                t_name.text as chara_name
            FROM card_data c
            JOIN chara_data cd ON c.chara_id = cd.id
            LEFT JOIN card_rarity_data cr_default ON c.id = cr_default.card_id AND cr_default.rarity = c.default_rarity
            LEFT JOIN card_rarity_data cr_max ON c.id = cr_max.card_id AND cr_max.rarity = 5
            LEFT JOIN text_data t_card ON t_card.category = 5 AND t_card.[index] = c.id
            LEFT JOIN text_data t_name ON t_name.category = 6 AND t_name.[index] = c.chara_id
            WHERE c.default_rarity > 0
            ORDER BY c.chara_id, c.default_rarity DESC
            """

            results = self.db.query(query)

            # Group by character
            for row in results:
                chara_id = row['chara_id']

                # Create character if doesn't exist
                if chara_id not in self.characters:
                    chara_name = row.get('chara_name')
                    if not chara_name:
                        # Skip characters without names
                        logger.warning(f"Character {chara_id} has no name, skipping")
                        continue

                    char = Character(
                        chara_id=chara_id,
                        name=chara_name,
                        name_en=chara_name,
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
                    self.name_index[chara_name.lower()] = chara_id

                # Add card with base stats and aptitudes
                # Strip brackets from card title (category 5 has format [Title])
                card_title_raw = row.get('card_title')
                card_title = card_title_raw.strip('[]') if card_title_raw else None

                card = CharacterCard(
                    card_id=row['card_id'],
                    chara_id=chara_id,
                    rarity=row['default_rarity'],
                    running_style=row['running_style'],
                    talent_speed=row['talent_speed'],
                    talent_stamina=row['talent_stamina'],
                    talent_power=row['talent_pow'],
                    talent_guts=row['talent_guts'],
                    talent_wit=row['talent_wiz'],
                    card_title=card_title,
                    base_speed=row.get('base_speed'),
                    base_stamina=row.get('base_stamina'),
                    base_power=row.get('base_pow'),
                    base_guts=row.get('base_guts'),
                    base_wit=row.get('base_wiz'),
                    max_base_speed=row.get('max_base_speed'),
                    max_base_stamina=row.get('max_base_stamina'),
                    max_base_power=row.get('max_base_pow'),
                    max_base_guts=row.get('max_base_guts'),
                    max_base_wit=row.get('max_base_wiz'),
                    apt_distance_short=row.get('apt_distance_short'),
                    apt_distance_mile=row.get('apt_distance_mile'),
                    apt_distance_middle=row.get('apt_distance_middle'),
                    apt_distance_long=row.get('apt_distance_long'),
                    apt_style_front_runner=row.get('apt_style_front_runner'),
                    apt_style_pace_chaser=row.get('apt_style_pace_chaser'),
                    apt_style_late=row.get('apt_style_late'),
                    apt_style_end_closer=row.get('apt_style_end_closer'),
                    apt_ground_turf=row.get('apt_ground_turf'),
                    apt_ground_dirt=row.get('apt_ground_dirt')
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
