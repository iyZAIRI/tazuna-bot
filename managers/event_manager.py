"""Manager for handling time-limited mission events."""
from typing import List, Dict, Optional
from utils.db_reader import MasterDBReader
import time
import datetime
from pathlib import Path


class EventManager:
    """Manages time-limited mission event data."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db_path = db_path
        self._emoji_cache = None
        self._support_card_cache = None
        self._mission_cache = {}  # Cache missions per event_id
        self._mission_cache_time = 0  # Timestamp of last cache load

    def _load_emoji_mappings(self) -> Dict[int, str]:
        """Load emoji mappings from emoji_codes.txt."""
        if self._emoji_cache is not None:
            return self._emoji_cache

        emoji_file = Path(__file__).parent.parent / "emoji_codes.txt"
        emoji_map = {}

        try:
            with open(emoji_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    if line and line.startswith('<:item_icon_'):
                        # Extract item ID from emoji name
                        # Format: <:item_icon_00110:1442616043070558270>
                        try:
                            emoji_name = line.split(':')[1]  # Get "item_icon_00110"
                            item_id_str = emoji_name.replace('item_icon_', '')  # Get "00110"
                            item_id = int(item_id_str)  # Convert to 110
                            emoji_map[item_id] = line
                        except (IndexError, ValueError):
                            continue
        except FileNotFoundError:
            pass

        self._emoji_cache = emoji_map
        return emoji_map

    def get_item_emoji(self, item_id: int) -> str:
        """Get emoji for an item ID, or ❓ if not found."""
        emoji_map = self._load_emoji_mappings()
        return emoji_map.get(item_id, f"❓ Item {item_id}")

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

    def format_reward(self, reward_category: int, reward_item_id: int, reward_amount: int) -> str:
        """Format a mission reward based on its category."""
        # Category 51 = Support Cards
        if reward_category == 51:
            # Get card from cache
            card_cache = self._load_support_cards()
            card = card_cache.get(reward_item_id)

            if card:
                # Get rarity and type emojis
                from constants import get_rarity_emoji, get_support_card_type_emoji
                rarity_emoji = get_rarity_emoji(card['rarity'])
                type_emoji = get_support_card_type_emoji(card['command_id'])

                if reward_amount > 1:
                    return f"{rarity_emoji} {type_emoji} {card['name']} x{reward_amount}"
                return f"{rarity_emoji} {type_emoji} {card['name']}"

            # Fallback if card not found
            return f"🎴 Support Card {reward_item_id} x{reward_amount}"

        # Otherwise, it's an item - use emoji
        item_emoji = self.get_item_emoji(reward_item_id)
        return f"{item_emoji} x{reward_amount}"

    def _is_cache_valid(self) -> bool:
        """Check if mission cache is still valid (same hour)."""
        if self._mission_cache_time == 0:
            return False

        current_time = int(time.time())

        # Round down both timestamps to the nearest hour
        # If they're in the same hour, cache is valid
        cache_hour_timestamp = (self._mission_cache_time // 3600) * 3600
        current_hour_timestamp = (current_time // 3600) * 3600

        return cache_hour_timestamp == current_hour_timestamp

    def _invalidate_mission_cache(self):
        """Clear mission cache and reset timestamp."""
        self._mission_cache = {}
        self._mission_cache_time = 0

    def _parse_datetime(self, date_str: str) -> int:
        """Parse datetime string from database to Unix timestamp."""
        try:
            # Format: "2025/07/13 22:00:00"
            dt = datetime.datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S")
            return int(dt.timestamp())
        except (ValueError, AttributeError):
            return 0

    def get_active_events(self) -> List[Dict]:
        """Get all currently active mission events."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        # Get all unique event_ids from mission_data
        events = db.query('''
            SELECT DISTINCT event_id
            FROM mission_data
            WHERE event_id > 0
            ORDER BY event_id
        ''')

        result = []
        for event in events:
            event_id = event['event_id']

            # Get first mission to check dates and get event name
            first_mission = db.query(f'''
                SELECT id, start_date, end_date
                FROM mission_data
                WHERE event_id = {event_id}
                ORDER BY id
                LIMIT 1
            ''')

            if not first_mission:
                continue

            # Parse dates and check if currently active
            start_timestamp = self._parse_datetime(first_mission[0]['start_date'])
            end_timestamp = self._parse_datetime(first_mission[0]['end_date'])

            # Skip inactive events or events ending in 2050+ (permanent missions)
            end_year = datetime.datetime.fromtimestamp(end_timestamp).year if end_timestamp > 0 else 0
            if end_year >= 2050:
                continue

            if not (start_timestamp <= current_time <= end_timestamp):
                continue

            # Extract event name from mission ID description
            mission_id = first_mission[0]['id']
            desc_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 67 AND [index] = {mission_id}
            ''')

            # Parse event name from description
            if desc_query and desc_query[0]['text']:
                desc = desc_query[0]['text']
                # Extract the main event name before ":"
                event_name = desc.split(':')[0].strip()

                # Ensure event name is not empty after all the processing
                if not event_name or len(event_name) == 0:
                    event_name = f"Event {event_id}"
            else:
                event_name = f"Event {event_id}"

            result.append({
                'event_id': event_id,
                'name': event_name,
                'start_date': start_timestamp,
                'end_date': end_timestamp
            })

        db.close()
        return result

    def get_event_mission_groups(self, event_id: int) -> List[Dict]:
        """Get mission groups for a specific event."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        # Get all missions for this event
        all_missions = db.query(f'''
            SELECT step_group_id, id, start_date, end_date
            FROM mission_data
            WHERE event_id = {event_id}
            ORDER BY step_group_id, id
        ''')

        # Group by step_group_id and filter by date
        groups_dict = {}
        for mission in all_missions:
            # Parse dates and check if active
            start_ts = self._parse_datetime(mission['start_date'])
            end_ts = self._parse_datetime(mission['end_date'])

            if not (start_ts <= current_time <= end_ts):
                continue

            step_group_id = mission['step_group_id']
            if step_group_id not in groups_dict:
                groups_dict[step_group_id] = {
                    'step_group_id': step_group_id,
                    'first_mission_id': mission['id'],
                    'count': 0
                }
            groups_dict[step_group_id]['count'] += 1

        # Get group names and format result
        result = []
        for group_id, group_info in sorted(groups_dict.items()):
            # Get group name from first mission
            desc_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 67 AND [index] = {group_info['first_mission_id']}
            ''')

            if desc_query and desc_query[0]['text']:
                desc = desc_query[0]['text']
                # Extract group name
                group_name = desc.split(':')[0].strip()

                # Ensure group name is not empty
                if not group_name or len(group_name) == 0:
                    group_name = f"Group {group_id}"
            else:
                group_name = f"Group {group_id}"

            result.append({
                'step_group_id': group_id,
                'name': group_name,
                'mission_count': group_info['count']
            })

        db.close()
        return result

    def get_missions_by_group(self, event_id: int, step_group_id: int) -> List[Dict]:
        """Get all missions in a specific group."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        missions = db.query(f'''
            SELECT id, mission_type, condition_type, condition_num,
                   step_order, disp_order,
                   item_category, item_id, item_num,
                   start_date, end_date
            FROM mission_data
            WHERE event_id = {event_id}
              AND step_group_id = {step_group_id}
            ORDER BY disp_order, step_order
        ''')

        result = []
        for mission in missions:
            # Parse dates and check if active
            start_ts = self._parse_datetime(mission['start_date'])
            end_ts = self._parse_datetime(mission['end_date'])

            if not (start_ts <= current_time <= end_ts):
                continue

            # Get mission description from text_data category 67
            desc_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 67 AND [index] = {mission['id']}
            ''')

            if desc_query and desc_query[0]['text']:
                description = desc_query[0]['text']
            else:
                description = f"Mission {mission['id']}"

            result.append({
                'mission_id': mission['id'],
                'type': mission['mission_type'],
                'condition_type': mission['condition_type'],
                'condition_num': mission['condition_num'],
                'description': description,
                'reward_category': mission['item_category'],
                'reward_item_id': mission['item_id'],
                'reward_amount': mission['item_num']
            })

        db.close()
        return result

    def get_event_missions(self, event_id: int) -> List[Dict]:
        """Get all missions for an event directly (simplified - no groups)."""
        # Check cache validity
        if not self._is_cache_valid():
            self._invalidate_mission_cache()

        # Return cached missions if available
        if event_id in self._mission_cache:
            return self._filter_active_missions(self._mission_cache[event_id])

        # Load missions from database
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        missions = db.query(f'''
            SELECT id, mission_type, condition_type, condition_num,
                   step_order, disp_order,
                   item_category, item_id, item_num,
                   start_date, end_date
            FROM mission_data
            WHERE event_id = {event_id}
            ORDER BY disp_order, step_order
        ''')

        # Get descriptions for all missions at once (more efficient)
        mission_ids = [str(m['id']) for m in missions]
        if mission_ids:
            desc_query = db.query(f'''
                SELECT [index], text FROM text_data
                WHERE category = 67 AND [index] IN ({','.join(mission_ids)})
            ''')
            desc_map = {row['index']: row['text'] for row in desc_query}
        else:
            desc_map = {}

        db.close()

        # Build mission list with all data (not filtered by time yet)
        all_missions = []
        for mission in missions:
            description = desc_map.get(mission['id'], f"Mission {mission['id']}")

            all_missions.append({
                'mission_id': mission['id'],
                'type': mission['mission_type'],
                'condition_type': mission['condition_type'],
                'condition_num': mission['condition_num'],
                'description': description,
                'reward_category': mission['item_category'],
                'reward_item_id': mission['item_id'],
                'reward_amount': mission['item_num'],
                'start_date': mission['start_date'],
                'end_date': mission['end_date']
            })

        # Cache all missions for this event
        self._mission_cache[event_id] = all_missions
        self._mission_cache_time = int(time.time())

        # Return filtered active missions
        return self._filter_active_missions(all_missions)

    def _filter_active_missions(self, missions: List[Dict]) -> List[Dict]:
        """Filter missions to only include currently active ones."""
        current_time = int(time.time())
        result = []

        for mission in missions:
            # Parse dates and check if active
            start_ts = self._parse_datetime(mission['start_date'])
            end_ts = self._parse_datetime(mission['end_date'])

            # Skip missions ending in 2050+ (permanent missions)
            end_year = datetime.datetime.fromtimestamp(end_ts).year if end_ts > 0 else 0
            if end_year >= 2050:
                continue

            if not (start_ts <= current_time <= end_ts):
                continue

            result.append(mission)

        return result
