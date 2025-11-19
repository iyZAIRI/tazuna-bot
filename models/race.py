"""Race data models."""
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class RaceGrade(IntEnum):
    """Race grade enum."""
    PRE_OPEN = 1
    OPEN = 2
    G3 = 3
    G2 = 4
    G1 = 5

    @classmethod
    def get_name(cls, value: int) -> str:
        """Get grade name."""
        names = {
            1: "Pre-Open",
            2: "Open",
            3: "G3",
            4: "G2",
            5: "G1"
        }
        return names.get(value, "Unknown")

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for grade."""
        emojis = {
            1: "🥉",  # Pre-Open
            2: "🥈",  # Open
            3: "🥉",  # G3
            4: "🥈",  # G2
            5: "🥇"   # G1
        }
        return emojis.get(value, "🏇")

class Ground(IntEnum):
    """Ground type enum."""
    TURF = 1
    DIRT = 2

    @classmethod
    def get_name(cls, value: int) -> str:
        """Get ground name."""
        return "Turf" if value == 1 else "Dirt"

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for ground."""
        return "🌱" if value == 1 else "🏜️"

@dataclass
class Race:
    """Represents a race."""
    race_id: int
    name: str
    grade: int
    distance: int
    ground: int
    track_id: int
    name_en: Optional[str] = None
    name_jp: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get display name (prefers English)."""
        return self.name_en or self.name_jp or self.name or f"Race {self.race_id}"

    @property
    def grade_name(self) -> str:
        """Get grade name."""
        return RaceGrade.get_name(self.grade)

    @property
    def grade_emoji(self) -> str:
        """Get grade emoji."""
        return RaceGrade.get_emoji(self.grade)

    @property
    def ground_name(self) -> str:
        """Get ground name."""
        return Ground.get_name(self.ground)

    @property
    def ground_emoji(self) -> str:
        """Get ground emoji."""
        return Ground.get_emoji(self.ground)

    @property
    def distance_category(self) -> str:
        """Get distance category."""
        if self.distance < 1400:
            return "Sprint"
        elif self.distance < 1800:
            return "Mile"
        elif self.distance < 2400:
            return "Middle"
        else:
            return "Long"

    @property
    def formatted_distance(self) -> str:
        """Get formatted distance."""
        return f"{self.distance}m"
