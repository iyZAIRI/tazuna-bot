"""Character data models."""
from dataclasses import dataclass
from typing import List, Optional
from enum import IntEnum

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
            1: "Runner",
            2: "Leader",
            3: "Betweener",
            4: "Chaser"
        }
        return names.get(value, "Unknown")

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for style."""
        emojis = {
            1: "🏃",  # Runner
            2: "👑",  # Leader
            3: "🎯",  # Betweener
            4: "⚡"   # Chaser
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
    talent_wisdom: int

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
