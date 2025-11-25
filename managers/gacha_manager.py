"""Manager for handling gacha banner data."""
from typing import List, Dict, Optional
from utils.db_reader import MasterDBReader
import time
import datetime


class GachaManager:
    """Manages gacha banner data."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db_path = db_path
        self._character_card_cache = None
        self._support_card_cache = None

    def _load_character_cards(self) -> Dict[int, Dict]:
        """Load character card data and cache it."""
        if self._character_card_cache is not None:
            return self._character_card_cache

        db = MasterDBReader(self.db_path)
        card_map = {}

        if db.connect():
            # Get all character cards with their names
            cards = db.query('''
                SELECT cd.id, cd.chara_id, cd.default_rarity, t.text as name
                FROM card_data cd
                LEFT JOIN text_data t ON t.category = 4 AND t.[index] = cd.id
            ''')

            for card in cards:
                card_map[card['id']] = {
                    'id': card['id'],
                    'chara_id': card['chara_id'],
                    'rarity': card['default_rarity'],
                    'name': card['name'] if card['name'] else f"Character Card {card['id']}"
                }

            db.close()

        self._character_card_cache = card_map
        return card_map

    def _load_support_cards(self) -> Dict[int, Dict]:
        """Load support card data and cache it."""
        if self._support_card_cache is not None:
            return self._support_card_cache

        db = MasterDBReader(self.db_path)
        card_map = {}

        if db.connect():
            # Get all support cards with their data
            cards = db.query('''
                SELECT sc.id, sc.chara_id, sc.rarity, sc.command_id, t.text as name
                FROM support_card_data sc
                LEFT JOIN text_data t ON t.category = 75 AND t.[index] = sc.id
            ''')

            for card in cards:
                card_map[card['id']] = {
                    'id': card['id'],
                    'chara_id': card['chara_id'],
                    'rarity': card['rarity'],
                    'command_id': card['command_id'],
                    'name': card['name'] if card['name'] else f"Support Card {card['id']}"
                }

            db.close()

        self._support_card_cache = card_map
        return card_map

    def get_active_gacha_banners(self) -> List[Dict]:
        """Get all currently active gacha banners (excluding permanent ones)."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        # Get all gacha banners
        gachas = db.query('''
            SELECT id, type, card_type, cost_single, cost_type,
                   start_date, end_date, only_once_flag
            FROM gacha_data
            WHERE start_date <= ? AND end_date >= ?
            ORDER BY id DESC
        ''', (current_time, current_time))

        result = []
        for gacha in gachas:
            # Skip permanent gacha (ending in 2050+)
            end_dt = datetime.datetime.fromtimestamp(gacha['end_date'])
            if end_dt.year >= 2050:
                continue

            # Get pickup cards for this gacha
            pickups = db.query(f'''
                SELECT card_id, card_type, rarity, recommend_order
                FROM gacha_available
                WHERE gacha_id = {gacha['id']} AND is_pickup = 1
                ORDER BY recommend_order
            ''')

            # Format pickup cards
            pickup_cards = []
            char_card_cache = self._load_character_cards()
            support_card_cache = self._load_support_cards()

            for pickup in pickups:
                if pickup['card_type'] == 1:  # Character card
                    char_card = char_card_cache.get(pickup['card_id'])
                    if char_card:
                        pickup_cards.append({
                            'type': 'character',
                            'id': char_card['id'],
                            'name': char_card['name'],
                            'rarity': char_card['rarity']
                        })
                elif pickup['card_type'] == 2:  # Support card
                    support_card = support_card_cache.get(pickup['card_id'])
                    if support_card:
                        pickup_cards.append({
                            'type': 'support',
                            'id': support_card['id'],
                            'name': support_card['name'],
                            'rarity': support_card['rarity'],
                            'command_id': support_card['command_id']
                        })

            result.append({
                'id': gacha['id'],
                'gacha_type': gacha['type'],
                'card_type': gacha['card_type'],  # 1=character, 2=support
                'cost': gacha['cost_single'],
                'cost_type': gacha['cost_type'],
                'start_date': gacha['start_date'],
                'end_date': gacha['end_date'],
                'only_once': gacha['only_once_flag'] == 1,
                'pickups': pickup_cards
            })

        db.close()
        return result
