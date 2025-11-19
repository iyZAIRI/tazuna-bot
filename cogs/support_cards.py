"""Support card commands using slash commands and the database."""
import discord
from discord import app_commands
from discord.ext import commands
import config
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.support_card_manager import SupportCardManager

class SupportCards(commands.Cog):
    """Support card lookup and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = SupportCardManager()
        if not self.manager.load():
            print("⚠️  Failed to load support card data")

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.manager.close()

    @app_commands.command(name="support", description="Look up information about a support card")
    @app_commands.describe(name="Support card name (partial match supported)")
    async def support(self, interaction: discord.Interaction, name: str):
        """Look up information about a support card."""
        await interaction.response.defer()

        card = self.manager.get_by_name(name)

        if not card:
            await interaction.followup.send(f"❌ Support card '{name}' not found.")
            return

        embed = discord.Embed(
            title=f"{card.type_emoji} {card.display_name}",
            color=card.type_color
        )

        embed.add_field(name="Rarity", value=card.rarity_stars, inline=True)
        embed.add_field(name="Type", value=f"{card.type_emoji} {card.type_name}", inline=True)
        embed.add_field(name="Card ID", value=card.card_id, inline=True)

        if card.character_name:
            embed.add_field(name="Character", value=card.character_name, inline=True)

        embed.add_field(name="Character ID", value=card.chara_id, inline=True)

        embed.set_image(url=card.image_url)
        embed.set_footer(text="Uma Musume Pretty Derby • Support Cards")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="supports", description="List support cards by type")
    @app_commands.describe(card_type="Support card type")
    @app_commands.choices(card_type=[
        app_commands.Choice(name="💨 Speed", value=1),
        app_commands.Choice(name="🔋 Stamina", value=2),
        app_commands.Choice(name="💪 Power", value=3),
        app_commands.Choice(name="❤️ Guts", value=4),
        app_commands.Choice(name="🧠 Wisdom", value=5),
        app_commands.Choice(name="👥 Friend", value=6),
    ])
    async def supports_list(self, interaction: discord.Interaction, card_type: Optional[int] = None):
        """List support cards, optionally filtered by type."""
        await interaction.response.defer()

        if card_type:
            cards = self.manager.get_by_type(card_type)
            title = f"{cards[0].type_emoji} {cards[0].type_name} Support Cards" if cards else "Support Cards"
            color = cards[0].type_color if cards else config.EMBED_COLOR
        else:
            cards = self.manager.get_ssr_cards()
            title = "✨ SSR Support Cards"
            color = 0xFFD700

        if not cards:
            await interaction.followup.send("❌ No support cards found")
            return

        # Sort by rarity descending
        cards.sort(key=lambda c: c.rarity, reverse=True)

        embed = discord.Embed(
            title=title,
            description=f"{len(cards)} card(s) found",
            color=color
        )

        for card in cards[:25]:  # Limit to 25
            embed.add_field(
                name=f"{card.rarity_stars} {card.character_name or 'Unknown'}",
                value=f"{card.type_emoji} {card.type_name}",
                inline=True
            )

        if len(cards) > 25:
            embed.set_footer(text=f"Showing 25 of {len(cards)} cards")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="ssrsupports", description="List all SSR support cards")
    async def ssr_supports(self, interaction: discord.Interaction):
        """List all SSR support cards."""
        await interaction.response.defer()

        cards = self.manager.get_ssr_cards()

        if not cards:
            await interaction.followup.send("❌ No SSR support cards found")
            return

        embed = discord.Embed(
            title="✨ SSR Support Cards",
            description=f"{len(cards)} SSR support cards",
            color=0xFFD700
        )

        # Group by type
        type_groups = {}
        for card in cards:
            type_name = card.type_name
            if type_name not in type_groups:
                type_groups[type_name] = []
            type_groups[type_name].append(card)

        for type_name, type_cards in sorted(type_groups.items()):
            if type_cards:
                emoji = type_cards[0].type_emoji
                card_names = [c.character_name or "Unknown" for c in type_cards[:10]]
                embed.add_field(
                    name=f"{emoji} {type_name} ({len(type_cards)})",
                    value="\n".join(card_names) or "None",
                    inline=True
                )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(SupportCards(bot))
