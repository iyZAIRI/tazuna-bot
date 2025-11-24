"""Manager for handling time-limited mission events."""
from typing import List, Dict, Optional
from utils.db_reader import MasterDBReader
import time
import datetime


class EventManager:
    """Manages time-limited mission event data."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        self.db_path = db_path

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

            # Skip inactive events
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
                # Clean up common prefixes
                if 'Pt ' in event_name:
                    event_name = event_name.split('Pt ')[0].strip()
                elif 'Day ' in event_name:
                    event_name = event_name.split('Day ')[0].strip()

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
