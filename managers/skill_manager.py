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
        self.name_index: Dict[str, List[int]] = {}  # Changed to List[int] to support duplicates
        self._loaded = False

    def load(self) -> bool:
        """Load skill data from database."""
        if self._loaded:
            return True

        if not self.db.connect():
            logger.error("Failed to connect to database")
            return False

        try:
            # First, get all character unique skill IDs (same way as character loading)
            unique_skill_query = """
            SELECT DISTINCT ss.skill_id1
            FROM card_rarity_data cr
            JOIN skill_set ss ON cr.skill_set = ss.id
            WHERE cr.rarity = 3 AND ss.skill_id1 > 0
            """
            unique_results = self.db.query(unique_skill_query)
            character_unique_ids = {row['skill_id1'] for row in unique_results}

            # Load all skills with ability data
            query = """
            SELECT
                s.id,
                s.rarity,
                s.grade_value,
                s.skill_category,
                s.condition_1,
                s.icon_id,
                s.float_ability_time_1,
                s.ability_type_1_1,
                s.ability_type_1_2,
                s.ability_type_1_3,
                s.float_ability_value_1_1,
                s.float_ability_value_1_2,
                s.float_ability_value_1_3,
                s.float_ability_time_2,
                s.ability_type_2_1,
                s.ability_type_2_2,
                s.ability_type_2_3,
                s.float_ability_value_2_1,
                s.float_ability_value_2_2,
                s.float_ability_value_2_3,
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
                # Parse ability 1
                ability_1 = None
                if row.get('ability_type_1_1', 0) > 0:
                    from models.skill import SkillAbility
                    ability_1 = SkillAbility(
                        ability_types=[
                            row.get('ability_type_1_1', 0),
                            row.get('ability_type_1_2', 0),
                            row.get('ability_type_1_3', 0)
                        ],
                        ability_values=[
                            (row.get('float_ability_value_1_1', 0) or 0) / 10000.0,
                            (row.get('float_ability_value_1_2', 0) or 0) / 10000.0,
                            (row.get('float_ability_value_1_3', 0) or 0) / 10000.0
                        ],
                        duration=(row.get('float_ability_time_1', 0) or 0) / 10000.0
                    )

                # Parse ability 2
                ability_2 = None
                if row.get('ability_type_2_1', 0) > 0:
                    from models.skill import SkillAbility
                    ability_2 = SkillAbility(
                        ability_types=[
                            row.get('ability_type_2_1', 0),
                            row.get('ability_type_2_2', 0),
                            row.get('ability_type_2_3', 0)
                        ],
                        ability_values=[
                            (row.get('float_ability_value_2_1', 0) or 0) / 10000.0,
                            (row.get('float_ability_value_2_2', 0) or 0) / 10000.0,
                            (row.get('float_ability_value_2_3', 0) or 0) / 10000.0
                        ],
                        duration=(row.get('float_ability_time_2', 0) or 0) / 10000.0
                    )

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
                    icon_id=row.get('icon_id', 0),
                    is_character_unique=row['id'] in character_unique_ids,
                    ability_1=ability_1,
                    ability_2=ability_2
                )
                self.skills[skill.skill_id] = skill

                # Index by name (support multiple skills with same name)
                if row['name']:
                    name_lower = row['name'].lower()
                    if name_lower not in self.name_index:
                        self.name_index[name_lower] = []
                    self.name_index[name_lower].append(skill.skill_id)

            self._loaded = True
            logger.info(f"Loaded {len(self.skills)} skills ({len(character_unique_ids)} character uniques)")
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
        """Get skill by name (partial match). Returns first match."""
        if not self._loaded:
            self.load()

        name_lower = name.lower()

        # Exact match - return highest rarity/grade
        if name_lower in self.name_index:
            skill_ids = self.name_index[name_lower]
            # Return the highest quality version (by rarity, then grade)
            skills = [self.skills[sid] for sid in skill_ids]
            best = max(skills, key=lambda s: (s.rarity, s.grade_value))
            return best

        # Partial match - return first highest quality match
        for indexed_name, skill_ids in self.name_index.items():
            if name_lower in indexed_name:
                skills = [self.skills[sid] for sid in skill_ids]
                best = max(skills, key=lambda s: (s.rarity, s.grade_value))
                return best

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
        """Search skills by name. Returns highest rarity version for each unique name."""
        if not self._loaded:
            self.load()

        query_lower = query.lower()
        best_by_name = {}  # Track best skill for each unique display name

        for name, skill_ids in self.name_index.items():
            if query_lower in name:
                # Get all skills with this indexed name
                skills_with_name = [self.skills[sid] for sid in skill_ids]

                # For each skill, keep only the best version per display name
                for skill in skills_with_name:
                    skill_name = skill.display_name.lower()

                    if skill_name not in best_by_name:
                        best_by_name[skill_name] = skill
                    else:
                        # Compare with existing and keep the better one
                        existing = best_by_name[skill_name]
                        if (skill.rarity, skill.grade_value) > (existing.rarity, existing.grade_value):
                            best_by_name[skill_name] = skill

        # Convert to list and sort by quality (highest first)
        results = list(best_by_name.values())
        results.sort(key=lambda s: (s.rarity, s.grade_value), reverse=True)
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
