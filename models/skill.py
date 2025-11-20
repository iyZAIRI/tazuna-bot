"""Skill data models."""
from dataclasses import dataclass
from typing import Optional, List
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from constants import get_skill_icon_emoji, get_ability_type_name

@dataclass
class SkillAbility:
    """Represents a skill ability effect (trigger)."""
    ability_types: List[int]  # ability_type_X_1, ability_type_X_2, ability_type_X_3
    ability_values: List[float]  # float_ability_value_X_1, X_2, X_3
    duration: float  # float_ability_time_X (in seconds)
    cooldown: float  # float_cooldown_time_X (in seconds)
    condition: Optional[str] = None  # condition_X - activation condition for this trigger

    def get_effect_lines(self) -> List[str]:
        """Get formatted effect lines with duration/cooldown first, then effects."""
        lines = []

        # Show duration and cooldown first
        if self.duration > 0:
            lines.append(f"Base Duration: {self.duration:.1f}s")
        if self.cooldown > 0:
            lines.append(f"Base Cooldown: {self.cooldown:.1f}s")

        # Then show the effects
        for ab_type, ab_value in zip(self.ability_types, self.ability_values):
            if ab_type > 0:
                type_name = get_ability_type_name(ab_type)
                # Add "Up" or "Down" suffix based on value sign
                if ab_value > 0:
                    type_name += " Up"
                elif ab_value < 0:
                    type_name += " Down"
                lines.append(f"{type_name}: {ab_value:+.3f}")

        # Show activation condition if exists
        if self.condition:
            lines.append(f"**Condition:**\n```\n{self.condition}\n```")

        return lines

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
    is_character_unique: bool = False
    unique_character_name: Optional[str] = None  # Name of character who owns this unique skill
    requires_wisdom: bool = False  # True if skill requires wisdom check (activate_lot=1), False if guaranteed (activate_lot=0)
    sp_cost: Optional[int] = None  # Skill point cost (None for character unique skills)
    ability_1: Optional[SkillAbility] = None
    ability_2: Optional[SkillAbility] = None

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
