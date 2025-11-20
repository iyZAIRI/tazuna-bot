"""Support card manager for loading and querying support card data."""
import sys
from pathlib import Path
from typing import List, Optional, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader
from models.support_card import SupportCard

logger = logging.getLogger('UmaMusumeBot.SupportCardManager')

class SupportCardManager:
    """Manages support card data from the database."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        """Initialize the support card manager."""
        self.db_path = db_path
        self.db = MasterDBReader(db_path)
        self.cards: Dict[int, SupportCard] = {}
        self.character_index: Dict[str, List[int]] = {}  # character_name -> list of card_ids
        self._loaded = False

    def load(self) -> bool:
        """Load support card data from database."""
        if self._loaded:
            return True

        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False

        try:
            query = """
            SELECT
                sc.id,
                sc.chara_id,
                sc.rarity,
                sc.command_id,
                sc.support_card_type,
                sc.skill_set_id,
                sc.effect_table_id,
                sc.unique_effect_id,
                t.text as chara_name
            FROM support_card_data sc
            LEFT JOIN text_data t ON t.category = 6 AND t.[index] = sc.chara_id
            ORDER BY sc.rarity DESC, sc.command_id, sc.id
            """

            results = self.db.query(query)

            for row in results:
                card = SupportCard(
                    card_id=row['id'],
                    chara_id=row['chara_id'],
                    character_name=row['chara_name'] or "Unknown",
                    rarity=row['rarity'],
                    command_id=row.get('command_id', 0),
                    support_card_type=row['support_card_type'],
                    skill_set_id=row.get('skill_set_id'),
                    effect_table_id=row.get('effect_table_id'),
                    unique_effect_id=row.get('unique_effect_id')
                )
                self.cards[card.card_id] = card

                # Index by character name
                if row['chara_name']:
                    char_name_lower = row['chara_name'].lower()
                    if char_name_lower not in self.character_index:
                        self.character_index[char_name_lower] = []
                    self.character_index[char_name_lower].append(card.card_id)

            self._loaded = True
            logger.info(f"Loaded {len(self.cards)} support cards")
            return True

        except Exception as e:
            logger.error(f"Failed to load support cards: {e}")
            return False

    def get_by_id(self, card_id: int) -> Optional[SupportCard]:
        """Get support card by ID."""
        if not self._loaded:
            self.load()
        return self.cards.get(card_id)

    def get_by_character_name(self, name: str) -> List[SupportCard]:
        """Get support cards by character name (partial match)."""
        if not self._loaded:
            self.load()

        name_lower = name.lower()
        matching_cards = []

        # Search for partial matches
        for indexed_name, card_ids in self.character_index.items():
            if name_lower in indexed_name:
                for card_id in card_ids:
                    matching_cards.append(self.cards[card_id])

        return matching_cards

    def get_all(self) -> List[SupportCard]:
        """Get all support cards."""
        if not self._loaded:
            self.load()
        return list(self.cards.values())

    def get_by_rarity(self, rarity: int) -> List[SupportCard]:
        """Get support cards by rarity."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.rarity == rarity]

    def get_by_type(self, command_id: int) -> List[SupportCard]:
        """Get support cards by training type (command_id)."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.command_id == command_id]

    def get_by_character_id(self, chara_id: int) -> List[SupportCard]:
        """Get support cards for a specific character."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.chara_id == chara_id]

    def get_ssr_cards(self) -> List[SupportCard]:
        """Get all SSR support cards."""
        return self.get_by_rarity(3)

    def get_pal_cards(self) -> List[SupportCard]:
        """Get all Pal support cards."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.is_pal]

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
