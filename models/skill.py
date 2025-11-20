"""Skill data models."""
from dataclasses import dataclass
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from constants import get_skill_icon_emoji, get_skill_types

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
    icon_id: int = 0
    tag_id: str = ""
    is_character_unique: bool = False  # True if this skill is a character's unique skill

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
    def icon_emoji(self) -> str:
        """Get skill icon Discord emoji."""
        return get_skill_icon_emoji(self.icon_id)

    @property
    def skill_types(self) -> list:
        """Get list of skill type names from tag_id."""
        return get_skill_types(self.tag_id)
