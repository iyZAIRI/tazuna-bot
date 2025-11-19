"""Skill data models."""
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class SkillCategory(IntEnum):
    """Skill category enum."""
    SPEED = 1
    ACCELERATION = 2
    STAMINA = 3
    POSITION = 4
    START = 5
    OVERTAKE = 6
    LANE_CHANGE = 7
    BLOCKED = 8
    SPURT = 9
    UNIQUE = 10
    DEBUFF = 11

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for category."""
        emojis = {
            1: "💨",  # Speed
            2: "⚡",  # Acceleration
            3: "🔋",  # Stamina
            4: "📍",  # Position
            5: "🏁",  # Start
            6: "🎯",  # Overtake
            7: "↔️",  # Lane Change
            8: "🚧",  # Blocked
            9: "🔥",  # Spurt
            10: "✨", # Unique
            11: "❌"  # Debuff
        }
        return emojis.get(value, "❓")

@dataclass
class Skill:
    """Represents a skill."""
    skill_id: int
    name: str
    name_en: Optional[str] = None
    name_jp: Optional[str] = None
    rarity: int = 0
    grade_value: int = 0
    skill_category: int = 0
    description: Optional[str] = None
    condition: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get display name (prefers English)."""
        return self.name_en or self.name_jp or self.name or f"Skill {self.skill_id}"

    @property
    def rarity_stars(self) -> str:
        """Get star representation of rarity."""
        if self.rarity == 0:
            return "N"
        return "★" * self.rarity

    @property
    def category_emoji(self) -> str:
        """Get category emoji."""
        return SkillCategory.get_emoji(self.skill_category)

    @property
    def is_unique(self) -> bool:
        """Check if skill is unique."""
        return self.skill_category == SkillCategory.UNIQUE

    @property
    def is_debuff(self) -> bool:
        """Check if skill is a debuff."""
        return self.skill_category == SkillCategory.DEBUFF
