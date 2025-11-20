"""Support card commands and views."""
import discord
from discord import app_commands
from discord.ext import commands
import sys
from pathlib import Path
from typing import List
import math

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.support_card_manager import SupportCardManager
from models.support_card import SupportCard
import config

class SupportCardListView(discord.ui.View):
    """Paginated view for displaying support card list."""

    def __init__(self, cards: List[SupportCard], page: int = 0, per_page: int = 10):
        super().__init__(timeout=180)
        self.cards = cards
        self.page = page
        self.per_page = per_page
        self.total_pages = math.ceil(len(cards) / per_page)

        # Update button states
        self.update_buttons()

    def update_buttons(self):
        """Update button states based on current page."""
        # Clear existing items
        self.clear_items()

        # Previous page button
        prev_button = discord.ui.Button(
            label="◀ Previous",
            style=discord.ButtonStyle.primary,
            disabled=(self.page == 0)
        )
        prev_button.callback = self.previous_page
        self.add_item(prev_button)

        # Page indicator
        page_button = discord.ui.Button(
            label=f"Page {self.page + 1}/{self.total_pages}",
            style=discord.ButtonStyle.secondary,
            disabled=True
        )
        self.add_item(page_button)

        # Next page button
        next_button = discord.ui.Button(
            label="Next ▶",
            style=discord.ButtonStyle.primary,
            disabled=(self.page >= self.total_pages - 1)
        )
        next_button.callback = self.next_page
        self.add_item(next_button)

    async def previous_page(self, interaction: discord.Interaction):
        """Go to previous page."""
        if self.page > 0:
            self.page -= 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    async def next_page(self, interaction: discord.Interaction):
        """Go to next page."""
        if self.page < self.total_pages - 1:
            self.page += 1
            self.update_buttons()
            embed = self.create_embed()
            await interaction.response.edit_message(embed=embed, view=self)

    def create_embed(self) -> discord.Embed:
        """Create the support card list embed for current page."""
        embed = discord.Embed(
            title=f"🎴 Support Cards",
            description=f"Showing {len(self.cards)} support cards",
            color=config.EMBED_COLOR
        )

        start_idx = self.page * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.cards))
        page_cards = self.cards[start_idx:end_idx]

        # Group cards by character
        cards_text = []
        for card in page_cards:
            cards_text.append(card.display_name)

        if cards_text:
            embed.add_field(
                name=f"Page {self.page + 1}/{self.total_pages}",
                value="\n".join(cards_text),
                inline=False
            )

        embed.set_footer(text=f"Uma Musume Pretty Derby • {len(self.cards)} cards total")
        return embed


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

    @app_commands.command(name="supports", description="List all support cards with pagination")
    @app_commands.describe(
        rarity="Filter by rarity (1=R, 2=SR, 3=SSR)",
        stat="Filter by stat type (speed, stamina, power, guts, wit, pal)"
    )
    @app_commands.choices(rarity=[
        app_commands.Choice(name="SSR", value=3),
        app_commands.Choice(name="SR", value=2),
        app_commands.Choice(name="R", value=1)
    ])
    @app_commands.choices(stat=[
        app_commands.Choice(name="Speed", value=101),
        app_commands.Choice(name="Power", value=102),
        app_commands.Choice(name="Guts", value=103),
        app_commands.Choice(name="Stamina", value=105),
        app_commands.Choice(name="Wit", value=106),
        app_commands.Choice(name="Pal", value=0)
    ])
    async def supports(
        self,
        interaction: discord.Interaction,
        rarity: int = None,
        stat: int = None
    ):
        """List support cards with optional filtering."""
        await interaction.response.defer()

        # Get cards based on filters
        cards = self.manager.get_all()

        if rarity is not None:
            cards = [c for c in cards if c.rarity == rarity]

        if stat is not None:
            cards = [c for c in cards if c.command_id == stat]

        if not cards:
            await interaction.followup.send("❌ No support cards found matching your filters.")
            return

        # Create paginated view
        view = SupportCardListView(cards)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot):
    """Load the support cards cog."""
    await bot.add_cog(SupportCards(bot))
