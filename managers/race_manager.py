"""Race manager for loading and querying race data."""
import sys
from pathlib import Path
from typing import List, Optional, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader
from models.race import Race

logger = logging.getLogger('UmaMusumeBot.RaceManager')

class RaceManager:
    """Manages race data from the database."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        """Initialize the race manager."""
        self.db_path = db_path
        self.db = MasterDBReader(db_path)
        self.races: Dict[int, Race] = {}
        self.name_index: Dict[str, int] = {}
        self._loaded = False

    def load(self) -> bool:
        """Load race data from database."""
        if self._loaded:
            return True

        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False

        try:
            query = """
            SELECT
                r.id,
                r.grade,
                rcs.distance,
                rcs.ground,
                rcs.race_track_id as track_id,
                t.text as name
            FROM race r
            LEFT JOIN race_course_set rcs ON r.course_set = rcs.id
            LEFT JOIN text_data t ON t.category = 30 AND t.[index] = r.id
            WHERE r.grade > 0 AND rcs.distance IS NOT NULL
            ORDER BY r.grade DESC, rcs.distance
            LIMIT 500
            """

            results = self.db.query(query)

            for row in results:
                race = Race(
                    race_id=row['id'],
                    name=row['name'] or f"Race {row['id']}",
                    grade=row['grade'] or 0,
                    distance=row['distance'],
                    ground=row['ground'],
                    track_id=row['track_id'],
                    name_en=row['name'],
                    name_jp=row['name']
                )
                self.races[race.race_id] = race

                # Index by name
                if row['name']:
                    self.name_index[row['name'].lower()] = race.race_id

            self._loaded = True
            logger.info(f"Loaded {len(self.races)} races")
            return True

        except Exception as e:
            logger.error(f"Failed to load races: {e}")
            return False

    def get_by_id(self, race_id: int) -> Optional[Race]:
        """Get race by ID."""
        if not self._loaded:
            self.load()
        return self.races.get(race_id)

    def get_by_name(self, name: str) -> Optional[Race]:
        """Get race by name (partial match)."""
        if not self._loaded:
            self.load()

        name_lower = name.lower()

        # Exact match
        if name_lower in self.name_index:
            return self.races[self.name_index[name_lower]]

        # Partial match
        for indexed_name, race_id in self.name_index.items():
            if name_lower in indexed_name:
                return self.races[race_id]

        return None

    def get_all(self) -> List[Race]:
        """Get all races."""
        if not self._loaded:
            self.load()
        return list(self.races.values())

    def get_by_grade(self, grade: int) -> List[Race]:
        """Get races by grade."""
        if not self._loaded:
            self.load()
        return [r for r in self.races.values() if r.grade == grade]

    def get_by_distance(self, min_dist: int, max_dist: int) -> List[Race]:
        """Get races within distance range."""
        if not self._loaded:
            self.load()
        return [r for r in self.races.values() if min_dist <= r.distance <= max_dist]

    def get_by_ground(self, ground: int) -> List[Race]:
        """Get races by ground type."""
        if not self._loaded:
            self.load()
        return [r for r in self.races.values() if r.ground == ground]

    def get_g1_races(self) -> List[Race]:
        """Get all G1 races."""
        return self.get_by_grade(5)

    def search(self, query: str) -> List[Race]:
        """Search races by name."""
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for name, race_id in self.name_index.items():
            if query_lower in name:
                results.append(self.races[race_id])

        return results

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
