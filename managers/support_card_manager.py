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
        self.name_index: Dict[str, int] = {}
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
                sc.support_card_type,
                t1.text as card_name,
                t2.text as chara_name
            FROM support_card_data sc
            LEFT JOIN text_data t1 ON t1.category = 75 AND t1.[index] = sc.id
            LEFT JOIN text_data t2 ON t2.category = 6 AND t2.[index] = sc.chara_id
            ORDER BY sc.rarity DESC, sc.id
            """

            results = self.db.query(query)

            for row in results:
                card = SupportCard(
                    card_id=row['id'],
                    chara_id=row['chara_id'],
                    name=row['card_name'] or f"Support {row['id']}",
                    rarity=row['rarity'],
                    support_type=row['support_card_type'],
                    name_en=row['card_name'],
                    name_jp=row['card_name'],
                    character_name=row['chara_name']
                )
                self.cards[card.card_id] = card

                # Index by name
                if row['card_name']:
                    self.name_index[row['card_name'].lower()] = card.card_id

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

    def get_by_name(self, name: str) -> Optional[SupportCard]:
        """Get support card by name (partial match)."""
        if not self._loaded:
            self.load()

        name_lower = name.lower()

        # Exact match
        if name_lower in self.name_index:
            return self.cards[self.name_index[name_lower]]

        # Partial match
        for indexed_name, card_id in self.name_index.items():
            if name_lower in indexed_name:
                return self.cards[card_id]

        return None

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

    def get_by_type(self, support_type: int) -> List[SupportCard]:
        """Get support cards by type."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.support_type == support_type]

    def get_by_character(self, chara_id: int) -> List[SupportCard]:
        """Get support cards for a specific character."""
        if not self._loaded:
            self.load()
        return [c for c in self.cards.values() if c.chara_id == chara_id]

    def search(self, query: str) -> List[SupportCard]:
        """Search support cards by name."""
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for name, card_id in self.name_index.items():
            if query_lower in name:
                results.append(self.cards[card_id])

        return results

    def get_ssr_cards(self) -> List[SupportCard]:
        """Get all SSR support cards."""
        return self.get_by_rarity(3)

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
