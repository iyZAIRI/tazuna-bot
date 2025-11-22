"""Support card data models."""
from dataclasses import dataclass
from typing import Optional
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from constants import get_support_card_type_emoji, get_rarity_emoji, SUPPORT_CARD_TYPES

@dataclass
class SupportCard:
    """Represents a support card."""
    card_id: int
    chara_id: int
    character_name: str
    rarity: int  # 1=R, 2=SR, 3=SSR
    command_id: int  # Training type: 101=Speed, 102=Power, 103=Guts, 105=Stamina, 106=Wit, 0=Pal
    support_card_type: int  # 1=Regular, 2=Pal
    skill_set_id: Optional[int] = None
    effect_table_id: Optional[int] = None
    unique_effect_id: Optional[int] = None

    @property
    def type_name(self) -> str:
        """Get the training type name."""
        return SUPPORT_CARD_TYPES.get(self.command_id, "Unknown")

    @property
    def type_emoji(self) -> str:
        """Get the training type emoji."""
        return get_support_card_type_emoji(self.command_id)

    @property
    def rarity_emoji(self) -> str:
        """Get the rarity emoji."""
        return get_rarity_emoji(self.rarity)

    @property
    def display_name(self) -> str:
        """Get display name with rarity and type emojis."""
        return f"{self.rarity_emoji} {self.type_emoji} {self.character_name}"

    @property
    def is_pal(self) -> bool:
        """Check if this is a Pal card."""
        return self.support_card_type == 2

    @property
    def image_url(self) -> str:
        """Get support card image URL from GameTora CDN."""
        return f"https://gametora.com/images/umamusume/supports/tex_support_card_{self.card_id}.png"
