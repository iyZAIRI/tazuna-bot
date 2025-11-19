"""Support card data models."""
from dataclasses import dataclass
from typing import Optional
from enum import IntEnum

class SupportCardType(IntEnum):
    """Support card type enum."""
    SPEED = 1
    STAMINA = 2
    POWER = 3
    GUTS = 4
    WISDOM = 5
    FRIEND = 6

    @classmethod
    def get_name(cls, value: int) -> str:
        """Get human-readable name."""
        names = {
            1: "Speed",
            2: "Stamina",
            3: "Power",
            4: "Guts",
            5: "Wisdom",
            6: "Friend"
        }
        return names.get(value, "Unknown")

    @classmethod
    def get_emoji(cls, value: int) -> str:
        """Get emoji for type."""
        emojis = {
            1: "💨",  # Speed
            2: "🔋",  # Stamina
            3: "💪",  # Power
            4: "❤️",  # Guts
            5: "🧠",  # Wisdom
            6: "👥"   # Friend
        }
        return emojis.get(value, "❓")

    @classmethod
    def get_color(cls, value: int) -> int:
        """Get color for embeds."""
        colors = {
            1: 0x3498DB,  # Blue - Speed
            2: 0x2ECC71,  # Green - Stamina
            3: 0xE74C3C,  # Red - Power
            4: 0xF39C12,  # Orange - Guts
            5: 0x9B59B6,  # Purple - Wisdom
            6: 0xFF69B4   # Pink - Friend
        }
        return colors.get(value, 0x95A5A6)

@dataclass
class SupportCard:
    """Represents a support card."""
    card_id: int
    chara_id: int
    name: str
    rarity: int
    support_type: int
    name_en: Optional[str] = None
    name_jp: Optional[str] = None
    character_name: Optional[str] = None

    @property
    def display_name(self) -> str:
        """Get display name (prefers English)."""
        return self.name_en or self.name_jp or self.name or f"Support {self.card_id}"

    @property
    def rarity_stars(self) -> str:
        """Get star representation of rarity."""
        if self.rarity == 0:
            return "N"
        return "★" * self.rarity

    @property
    def type_name(self) -> str:
        """Get support type name."""
        return SupportCardType.get_name(self.support_type)

    @property
    def type_emoji(self) -> str:
        """Get support type emoji."""
        return SupportCardType.get_emoji(self.support_type)

    @property
    def type_color(self) -> int:
        """Get color for Discord embeds."""
        return SupportCardType.get_color(self.support_type)

    @property
    def is_ssr(self) -> bool:
        """Check if SSR rarity."""
        return self.rarity == 3

    @property
    def is_sr(self) -> bool:
        """Check if SR rarity."""
        return self.rarity == 2

    @property
    def is_r(self) -> bool:
        """Check if R rarity."""
        return self.rarity == 1
