"""Character data models."""
from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from constants import (
    EMOJI_FRONT_RUNNER, EMOJI_PACE_CHASER, EMOJI_LATE, EMOJI_END_CLOSER,
    RANK_EMOJIS
)

@dataclass
class CardSkill:
    """Represents a skill available on a character card."""
    skill_id: int
    skill_name: str
    need_rank: int  # Bond level required to unlock (0-5)

    @property
    def rank_emoji(self) -> str:
        """Get emoji for unlock rank."""
        if self.need_rank == 0:
            return "🔓"
        return f"🔒{self.need_rank}"

class RunningStyle(IntEnum):
    """Running style enum."""
    RUNNER = 1
    LEADER = 2
    BETWEENER = 3
    CHASER = 4

    @classmethod
    def get_name(cls, value: int) -> str:
        """Get human-readable name."""
        names = {
            1: "Front Runner",
            2: "Pace Chaser",
            3: "Late",
            4: "End Closer"
        }
        return names.get(value, "Unknown")

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for style."""
        emojis = {
            1: EMOJI_FRONT_RUNNER,
            2: EMOJI_PACE_CHASER,
            3: EMOJI_LATE,
            4: EMOJI_END_CLOSER
        }
        return emojis.get(value, "❓")

@dataclass
class CharacterCard:
    """Represents a character card (playable version)."""
    card_id: int
    chara_id: int
    rarity: int
    running_style: int
    talent_speed: int
    talent_stamina: int
    talent_power: int
    talent_guts: int
    talent_wit: int
    card_title: Optional[str] = None
    # Base stats at default rarity
    base_speed: Optional[int] = None
    base_stamina: Optional[int] = None
    base_power: Optional[int] = None
    base_guts: Optional[int] = None
    base_wit: Optional[int] = None
    # Base stats at max rarity (5)
    max_base_speed: Optional[int] = None
    max_base_stamina: Optional[int] = None
    max_base_power: Optional[int] = None
    max_base_guts: Optional[int] = None
    max_base_wit: Optional[int] = None
    # Aptitudes (1-7 scale, at default rarity)
    apt_distance_short: Optional[int] = None
    apt_distance_mile: Optional[int] = None
    apt_distance_middle: Optional[int] = None
    apt_distance_long: Optional[int] = None
    apt_style_front_runner: Optional[int] = None
    apt_style_pace_chaser: Optional[int] = None
    apt_style_late: Optional[int] = None
    apt_style_end_closer: Optional[int] = None
    apt_ground_turf: Optional[int] = None
    apt_ground_dirt: Optional[int] = None
    # Skills available on this card
    skills: List['CardSkill'] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.skills is None:
            self.skills = []

    @staticmethod
    def aptitude_to_grade(value: Optional[int]) -> str:
        """Convert aptitude value (1-7) to rank emoji (G-A)."""
        if value is None:
            return RANK_EMOJIS["?"]
        grades = {1: "G", 2: "F", 3: "E", 4: "D", 5: "C", 6: "B", 7: "A"}
        grade_letter = grades.get(value, "?")
        return RANK_EMOJIS.get(grade_letter, RANK_EMOJIS["?"])

    @property
    def rarity_stars(self) -> str:
        """Get star representation of rarity."""
        return "★" * self.rarity if self.rarity > 0 else "N"

    @property
    def running_style_name(self) -> str:
        """Get running style name."""
        return RunningStyle.get_name(self.running_style)

    @property
    def running_style_emoji(self) -> str:
        """Get running style emoji."""
        return RunningStyle.get_emoji(self.running_style)

    @property
    def image_url(self) -> str:
        """Get character card image URL from GameTora CDN."""
        return f"https://gametora.com/images/umamusume/characters/chara_stand_{self.chara_id}_{self.card_id}.png"

@dataclass
class Character:
    """Represents a Uma Musume character."""
    chara_id: int
    name: str
    name_en: Optional[str] = None
    birth_year: Optional[int] = None
    birth_month: Optional[int] = None
    birth_day: Optional[int] = None
    color_main: Optional[str] = None
    color_sub: Optional[str] = None
    height: Optional[int] = None
    cards: List[CharacterCard] = None

    def __post_init__(self):
        """Initialize defaults."""
        if self.cards is None:
            self.cards = []

    @property
    def display_name(self) -> str:
        """Get display name (English only)."""
        return self.name_en or self.name or f"Character {self.chara_id}"

    @property
    def birth_date(self) -> Optional[str]:
        """Get formatted birth date."""
        if self.birth_year and self.birth_month and self.birth_day:
            return f"{self.birth_year}-{self.birth_month:02d}-{self.birth_day:02d}"
        return None

    @property
    def highest_rarity(self) -> int:
        """Get highest rarity card."""
        if not self.cards:
            return 0
        return max(card.rarity for card in self.cards)

    @property
    def card_count(self) -> int:
        """Get number of cards."""
        return len(self.cards)

    def get_hex_color(self) -> int:
        """Get color as integer for Discord embeds."""
        if self.color_main:
            try:
                return int(self.color_main, 16)
            except ValueError:
                pass
        return 0xFF69B4  # Default pink
