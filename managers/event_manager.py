"""Manager for handling time-limited mission events."""
from typing import List, Dict, Optional
from utils.db_reader import MasterDBReader
import datetime


class EventManager:
    """Manages time-limited mission event data."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db_path = db_path

    def get_all_events(self) -> List[Dict]:
        """Get all story events with basic info."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        events = db.query('''
            SELECT story_event_id, start_date, end_date
            FROM story_event_data
            ORDER BY start_date
        ''')

        result = []
        for event in events:
            # Get event name from text_data category 221
            name_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 221 AND [index] = {event['story_event_id']}
            ''')
            name = name_query[0]['text'] if name_query else f"Event {event['story_event_id']}"

            result.append({
                'event_id': event['story_event_id'],
                'name': name,
                'start_date': event['start_date'],
                'end_date': event['end_date']
            })

        db.close()
        return result

    def get_event_details(self, event_id: int) -> Optional[Dict]:
        """Get detailed information about a specific event."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return None

        # Get basic event info
        event = db.query(f'''
            SELECT * FROM story_event_data
            WHERE story_event_id = {event_id}
        ''')

        if not event:
            db.close()
            return None

        event_data = event[0]

        # Get event name
        name_query = db.query(f'''
            SELECT text FROM text_data
            WHERE category = 221 AND [index] = {event_id}
        ''')
        name = name_query[0]['text'] if name_query else f"Event {event_id}"

        # Get mission groups (step groups)
        missions = db.query(f'''
            SELECT DISTINCT step_group_id
            FROM story_event_mission
            WHERE story_event_id = {event_id}
            ORDER BY step_group_id
        ''')

        mission_groups = [m['step_group_id'] for m in missions]

        # Get bonus support cards
        bonus_cards = db.query(f'''
            SELECT support_card_id, chara_id, rarity, limit_0, limit_4
            FROM story_event_bonus_support_card
            WHERE story_event_id = {event_id}
            ORDER BY rarity DESC, chara_id
        ''')

        bonus_list = []
        for card in bonus_cards:
            chara_name = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 6 AND [index] = {card['chara_id']}
            ''')
            name_text = chara_name[0]['text'] if chara_name else 'Unknown'

            bonus_list.append({
                'card_id': card['support_card_id'],
                'name': name_text,
                'rarity': card['rarity'],
                'bonus_min': card['limit_0'],
                'bonus_max': card['limit_4']
            })

        db.close()

        return {
            'event_id': event_id,
            'name': name,
            'start_date': event_data['start_date'],
            'end_date': event_data['end_date'],
            'mission_groups': mission_groups,
            'bonus_cards': bonus_list
        }

    def get_mission_group_missions(self, event_id: int, step_group_id: int) -> List[Dict]:
        """Get all missions in a specific mission group."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        missions = db.query(f'''
            SELECT id, mission_type, condition_type, condition_num,
                   step_order, disp_order,
                   item_category, item_id, item_num
            FROM story_event_mission
            WHERE story_event_id = {event_id}
              AND step_group_id = {step_group_id}
            ORDER BY step_order, disp_order
        ''')

        result = []
        for mission in missions:
            # Try to get mission description from text_data category 67
            desc_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 67 AND [index] = {mission['condition_type']}
            ''')
            description = desc_query[0]['text'] if desc_query else f"Mission Type {mission['mission_type']}"

            result.append({
                'mission_id': mission['id'],
                'type': mission['mission_type'],
                'condition_type': mission['condition_type'],
                'condition_num': mission['condition_num'],
                'step_order': mission['step_order'],
                'description': description,
                'reward_category': mission['item_category'],
                'reward_item_id': mission['item_id'],
                'reward_amount': mission['item_num']
            })

        db.close()
        return result

    def get_point_rewards(self, event_id: int) -> List[Dict]:
        """Get point milestone rewards for an event."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        rewards = db.query(f'''
            SELECT point, item_category, item_id, item_num
            FROM story_event_point_reward
            WHERE story_event_id = {event_id}
            ORDER BY point
        ''')

        db.close()
        return [dict(r) for r in rewards]
