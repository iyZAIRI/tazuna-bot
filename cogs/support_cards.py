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


class SupportCardSelectorView(discord.ui.View):
    """View for selecting a support card when multiple matches are found."""

    def __init__(self, cards: List[SupportCard], search_query: str):
        super().__init__(timeout=180)
        self.cards = cards
        self.search_query = search_query

        # Create buttons for each card (limit to 25 - Discord limit)
        for idx, card in enumerate(cards[:25]):
            button = discord.ui.Button(
                label=f"{card.character_name} - {card.type_name}",
                style=discord.ButtonStyle.secondary,
                emoji=card.rarity_emoji,
                custom_id=f"support_{card.card_id}",
                row=idx // 5  # Group into rows of 5
            )
            button.callback = self.create_card_callback(card)
            self.add_item(button)

    def create_card_callback(self, card):
        """Create a callback for a specific card button."""
        async def callback(interaction: discord.Interaction):
            # Create detail view with back button
            detail_view = SupportCardDetailView(card, self)
            embed = detail_view.create_embed()
            await interaction.response.edit_message(embed=embed, view=detail_view)

        return callback

    def create_selector_embed(self) -> discord.Embed:
        """Create the selector embed showing all matching cards."""
        embed = discord.Embed(
            title="🎴 Multiple Support Cards Found",
            description=f"Found {len(self.cards)} support cards matching '{self.search_query}'. Select one:",
            color=config.EMBED_COLOR
        )

        # Show preview of matches (up to 10)
        preview_list = []
        for i, card in enumerate(self.cards[:10], 1):
            preview_list.append(f"{i}. {card.display_name}")

        embed.add_field(
            name="Matches",
            value="\n".join(preview_list),
            inline=False
        )

        if len(self.cards) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.cards)} matches • Select a card below")
        else:
            embed.set_footer(text="Select a card below")

        return embed


class SupportCardDetailView(discord.ui.View):
    """View for displaying support card details with back button."""

    def __init__(self, card: SupportCard, parent_selector: SupportCardSelectorView):
        super().__init__(timeout=180)
        self.card = card
        self.parent_selector = parent_selector

        # Back button
        back_button = discord.ui.Button(label="⬅ Back to Cards", style=discord.ButtonStyle.primary)
        back_button.callback = self.go_back
        self.add_item(back_button)

    async def go_back(self, interaction: discord.Interaction):
        """Go back to card selector."""
        embed = self.parent_selector.create_selector_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_selector)

    def create_embed(self) -> discord.Embed:
        """Create detailed embed for a support card."""
        card = self.card
        embed = discord.Embed(
            title=card.display_name,
            description=f"Card ID: {card.card_id}",
            color=config.EMBED_COLOR
        )

        embed.add_field(name="Type", value=f"{card.type_emoji} {card.type_name}", inline=True)
        embed.add_field(name="Character", value=card.character_name, inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        if card.skill_set_id:
            embed.add_field(name="Skill Set ID", value=card.skill_set_id, inline=True)
        if card.effect_table_id:
            embed.add_field(name="Effect Table ID", value=card.effect_table_id, inline=True)
        if card.unique_effect_id:
            embed.add_field(name="Unique Effect ID", value=card.unique_effect_id, inline=True)

        embed.set_image(url=card.image_url)
        embed.set_footer(text="Uma Musume Pretty Derby • Support Cards")
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

    @app_commands.command(name="support", description="Look up a specific support card")
    @app_commands.describe(name="Character name to search for")
    async def support(self, interaction: discord.Interaction, name: str):
        """Look up information about a support card."""
        await interaction.response.defer()

        # Search for cards by character name
        cards = self.manager.get_by_character_name(name)

        if not cards:
            await interaction.followup.send(f"❌ No support cards found for '{name}'.")
            return

        # If single match, show directly (no back button needed)
        if len(cards) == 1:
            card = cards[0]
            embed = discord.Embed(
                title=card.display_name,
                description=f"Card ID: {card.card_id}",
                color=config.EMBED_COLOR
            )

            embed.add_field(name="Type", value=f"{card.type_emoji} {card.type_name}", inline=True)
            embed.add_field(name="Character", value=card.character_name, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

            if card.skill_set_id:
                embed.add_field(name="Skill Set ID", value=card.skill_set_id, inline=True)
            if card.effect_table_id:
                embed.add_field(name="Effect Table ID", value=card.effect_table_id, inline=True)
            if card.unique_effect_id:
                embed.add_field(name="Unique Effect ID", value=card.unique_effect_id, inline=True)

            embed.set_image(url=card.image_url)
            embed.set_footer(text="Uma Musume Pretty Derby • Support Cards")
            await interaction.followup.send(embed=embed)
            return

        # Multiple matches - show selector with buttons
        view = SupportCardSelectorView(cards, name)
        embed = view.create_selector_embed()
        await interaction.followup.send(embed=embed, view=view)

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
