"""Skill manager for loading and querying skill data."""
import sys
from pathlib import Path
from typing import List, Optional, Dict
import logging

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader
from models.skill import Skill

logger = logging.getLogger('UmaMusumeBot.SkillManager')

class SkillManager:
    """Manages skill data from the database."""

    def __init__(self, db_path: str = "./data/master.mdb"):
        """Initialize the skill manager."""
        self.db_path = db_path
        self.db = MasterDBReader(db_path)
        self.skills: Dict[int, Skill] = {}
        self.name_index: Dict[str, int] = {}
        self._loaded = False

    def load(self) -> bool:
        """Load skill data from database."""
        if self._loaded:
            return True

        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False

        try:
            query = """
            SELECT
                s.id,
                s.rarity,
                s.grade_value,
                s.skill_category,
                s.condition_1,
                s.icon_id,
                t1.text as name,
                t2.text as description
            FROM skill_data s
            LEFT JOIN text_data t1 ON t1.category = 47 AND t1.[index] = s.id
            LEFT JOIN text_data t2 ON t2.category = 48 AND t2.[index] = s.id
            WHERE s.rarity > 0
            ORDER BY s.rarity DESC, s.grade_value DESC
            """

            results = self.db.query(query)

            for row in results:
                skill = Skill(
                    skill_id=row['id'],
                    name=row['name'] or f"Skill {row['id']}",
                    name_en=row['name'],
                    name_jp=row['name'],
                    rarity=row['rarity'],
                    grade_value=row['grade_value'],
                    skill_category=row['skill_category'] or 0,
                    description=row['description'],
                    condition=row['condition_1'],
                    icon_id=row.get('icon_id', 0)
                )
                self.skills[skill.skill_id] = skill

                # Index by name
                if row['name']:
                    self.name_index[row['name'].lower()] = skill.skill_id

            self._loaded = True
            logger.info(f"Loaded {len(self.skills)} skills")
            return True

        except Exception as e:
            logger.error(f"Failed to load skills: {e}")
            return False

    def get_by_id(self, skill_id: int) -> Optional[Skill]:
        """Get skill by ID."""
        if not self._loaded:
            self.load()
        return self.skills.get(skill_id)

    def get_by_name(self, name: str) -> Optional[Skill]:
        """Get skill by name (partial match)."""
        if not self._loaded:
            self.load()

        name_lower = name.lower()

        # Exact match
        if name_lower in self.name_index:
            return self.skills[self.name_index[name_lower]]

        # Partial match
        for indexed_name, skill_id in self.name_index.items():
            if name_lower in indexed_name:
                return self.skills[skill_id]

        return None

    def get_all(self) -> List[Skill]:
        """Get all skills."""
        if not self._loaded:
            self.load()
        return list(self.skills.values())

    def get_by_rarity(self, rarity: int) -> List[Skill]:
        """Get skills by rarity."""
        if not self._loaded:
            self.load()
        return [s for s in self.skills.values() if s.rarity == rarity]

    def get_by_category(self, category: int) -> List[Skill]:
        """Get skills by category."""
        if not self._loaded:
            self.load()
        return [s for s in self.skills.values() if s.skill_category == category]

    def search(self, query: str) -> List[Skill]:
        """Search skills by name."""
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        results = []

        for name, skill_id in self.name_index.items():
            if query_lower in name:
                results.append(self.skills[skill_id])

        return results

    def get_top(self, limit: int = 10) -> List[Skill]:
        """Get top skills by grade value."""
        if not self._loaded:
            self.load()

        sorted_skills = sorted(
            self.skills.values(),
            key=lambda s: (s.rarity, s.grade_value),
            reverse=True
        )
        return sorted_skills[:limit]

    def close(self):
        """Close database connection."""
        if self.db:
            self.db.close()
