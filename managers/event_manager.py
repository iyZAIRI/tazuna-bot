"""Manager for handling time-limited mission events."""
from typing import List, Dict, Optional
from utils.db_reader import MasterDBReader
import time


class EventManager:
    """Manages time-limited mission event data."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db_path = db_path

    def get_active_events(self) -> List[Dict]:
        """Get all currently active mission events."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        # Get unique event_ids from mission_data that are currently active
        events = db.query(f'''
            SELECT DISTINCT event_id
            FROM mission_data
            WHERE event_id > 0
              AND start_date <= {current_time}
              AND end_date >= {current_time}
            ORDER BY event_id
        ''')

        result = []
        for event in events:
            event_id = event['event_id']

            # Get event name from the first mission in this event
            # Event names are usually in mission descriptions
            first_mission = db.query(f'''
                SELECT id, start_date, end_date
                FROM mission_data
                WHERE event_id = {event_id}
                ORDER BY id
                LIMIT 1
            ''')

            if not first_mission:
                continue

            # Extract event name from mission ID description
            mission_id = first_mission[0]['id']
            desc_query = db.query(f'''
                SELECT text FROM text_data
                WHERE category = 67 AND [index] = {mission_id}
            ''')

            # Parse event name from description (e.g., "Half Anni Pt 1: ..." -> "Half Anniversary")
            if desc_query and desc_query[0]['text']:
                desc = desc_query[0]['text']
                # Extract the main event name before ":"
                event_name = desc.split(':')[0].strip()
                # Clean up common prefixes
                if 'Pt ' in event_name:
                    event_name = event_name.split('Pt ')[0].strip()
                elif 'Day ' in event_name:
                    event_name = event_name.split('Day ')[0].strip()
            else:
                event_name = f"Event {event_id}"

            result.append({
                'event_id': event_id,
                'name': event_name,
                'start_date': first_mission[0]['start_date'],
                'end_date': first_mission[0]['end_date']
            })

        db.close()
        return result

    def get_event_mission_groups(self, event_id: int) -> List[Dict]:
        """Get mission groups for a specific event."""
        db = MasterDBReader(self.db_path)
        if not db.connect():
            return []

        current_time = int(time.time())

        # Get unique step_group_ids for this event
        groups = db.query(f'''
            SELECT DISTINCT step_group_id
            FROM mission_data
            WHERE event_id = {event_id}
              AND start_date <= {current_time}
              AND end_date >= {current_time}
            ORDER BY step_group_id
        ''')

        result = []
        for group in groups:
            step_group_id = group['step_group_id']

            # Get a representative mission to extract group name
            sample = db.query(f'''
                SELECT id
                FROM mission_data
                WHERE event_id = {event_id}
                  AND step_group_id = {step_group_id}
                ORDER BY id
                LIMIT 1
            ''')

            if sample:
                mission_id = sample[0]['id']
                desc_query = db.query(f'''
                    SELECT text FROM text_data
                    WHERE category = 67 AND [index] = {mission_id}
                ''')

                if desc_query and desc_query[0]['text']:
                    desc = desc_query[0]['text']
                    # Extract group name (e.g., "Half Anni Pt 1" or "Pt 1 Day 1")
                    group_name = desc.split(':')[0].strip()
                else:
                    group_name = f"Group {step_group_id}"
            else:
                group_name = f"Group {step_group_id}"

            # Count missions in this group
            count_query = db.query(f'''
                SELECT COUNT(*) as count
                FROM mission_data
                WHERE event_id = {event_id}
                  AND step_group_id = {step_group_id}
                  AND start_date <= {current_time}
                  AND end_date >= {current_time}
            ''')
            mission_count = count_query[0]['count'] if count_query else 0

            result.append({
                'step_group_id': step_group_id,
                'name': group_name,
                'mission_count': mission_count
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
                   item_category, item_id, item_num
            FROM mission_data
            WHERE event_id = {event_id}
              AND step_group_id = {step_group_id}
              AND start_date <= {current_time}
              AND end_date >= {current_time}
            ORDER BY disp_order, step_order
        ''')

        result = []
        for mission in missions:
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
