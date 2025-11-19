"""Character commands using slash commands and the database."""
import discord
from discord import app_commands
from discord.ext import commands
import config
import sys
from pathlib import Path
from typing import Optional

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.character_manager import CharacterManager
from models.character import Character, CharacterCard

class CardSelectorView(discord.ui.View):
    """View for selecting character cards/alts."""

    def __init__(self, character: Character):
        super().__init__(timeout=180)  # 3 minute timeout
        self.character = character

        # Add a button for each card (limit to 25 buttons total - Discord limit)
        for idx, card in enumerate(character.cards[:25]):
            # Create button label with card number (e.g., "1. ★★★ 🎯")
            label = f"{idx + 1}. {card.rarity_stars} {card.running_style_emoji}"
            button = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary,
                custom_id=f"card_{card.card_id}",
                row=idx // 5  # Group into rows of 5
            )
            button.callback = self.create_card_callback(card)
            self.add_item(button)

    def create_card_callback(self, card: CharacterCard):
        """Create a callback for a specific card button."""
        async def callback(interaction: discord.Interaction):
            # Create embed for this specific card
            embed = discord.Embed(
                title=f"{card.running_style_emoji} {self.character.display_name}",
                color=self.character.get_hex_color()
            )

            # Card details
            embed.add_field(name="Rarity", value=card.rarity_stars, inline=True)
            embed.add_field(name="Running Style", value=f"{card.running_style_emoji} {card.running_style_name}", inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

            # Talents
            embed.add_field(name="Speed", value=card.talent_speed, inline=True)
            embed.add_field(name="Stamina", value=card.talent_stamina, inline=True)
            embed.add_field(name="Power", value=card.talent_power, inline=True)
            embed.add_field(name="Guts", value=card.talent_guts, inline=True)
            embed.add_field(name="Wisdom", value=card.talent_wisdom, inline=True)
            embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

            # Character info
            if self.character.birth_date:
                embed.add_field(name="Birthday", value=self.character.birth_date, inline=True)

            # Card image
            embed.set_image(url=card.image_url)
            embed.set_footer(text=f"Uma Musume Pretty Derby • {self.character.display_name}")

            # Update the message
            await interaction.response.edit_message(embed=embed, view=self)

        return callback

class Characters(commands.Cog):
    """Character lookup and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = CharacterManager()
        # Load data on initialization
        if not self.manager.load():
            print("⚠️  Failed to load character data")

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.manager.close()

    @app_commands.command(name="character", description="Look up information about a character")
    @app_commands.describe(name="Character name (partial match supported)")
    async def character(self, interaction: discord.Interaction, name: str):
        """Look up information about a Uma Musume character."""
        await interaction.response.defer()

        # Search for character by name
        char = self.manager.get_by_name(name)

        if not char:
            await interaction.followup.send(f"❌ Character '{name}' not found. Use `/characters` to see all available characters.")
            return

        if not char.cards:
            await interaction.followup.send(f"❌ {char.display_name} has no cards available.")
            return

        # Create initial embed showing character and prompting card selection
        embed = discord.Embed(
            title=f"🏇 {char.display_name}",
            description=f"Select a card to view details ({len(char.cards)} available)",
            color=char.get_hex_color()
        )

        # Show character info
        if char.birth_date:
            embed.add_field(name="Birthday", value=char.birth_date, inline=True)

        embed.add_field(name="Total Cards", value=len(char.cards), inline=True)

        embed.set_footer(text="Uma Musume Pretty Derby • Click a button to view card details")

        # Create view with card selection buttons
        view = CardSelectorView(char)

        # Send with buttons
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="characters", description="List all available characters")
    @app_commands.describe(page="Page number (default: 1)")
    async def characters(self, interaction: discord.Interaction, page: Optional[int] = 1):
        """List all available Uma Musume characters."""
        await interaction.response.defer()

        all_chars = self.manager.get_all()

        if not all_chars:
            await interaction.followup.send("❌ No characters available")
            return

        # Sort by ID
        all_chars.sort(key=lambda c: c.chara_id)

        # Pagination
        per_page = 15
        total_pages = (len(all_chars) + per_page - 1) // per_page

        if page < 1 or page > total_pages:
            await interaction.followup.send(f"❌ Invalid page. Available pages: 1-{total_pages}")
            return

        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page
        page_chars = all_chars[start_idx:end_idx]

        embed = discord.Embed(
            title="🏇 Uma Musume Characters",
            description=f"Page {page}/{total_pages} • {len(all_chars)} total characters",
            color=config.EMBED_COLOR
        )

        for char in page_chars:
            embed.add_field(
                name=f"{char.highest_rarity}★ {char.display_name}",
                value=f"ID: {char.chara_id} • {char.card_count} card(s)",
                inline=True
            )

        embed.set_footer(text=f"Use /character <name> for details • Page {page}/{total_pages}")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="randomchar", description="Get a random character")
    async def random_character(self, interaction: discord.Interaction):
        """Get a random Uma Musume character."""
        char = self.manager.get_random()

        if not char:
            await interaction.response.send_message("❌ No characters available")
            return

        embed = discord.Embed(
            title="🎲 Random Uma Musume!",
            description=f"You got **{char.display_name}**!",
            color=char.get_hex_color()
        )

        if char.birth_date:
            embed.add_field(name="Birthday", value=char.birth_date, inline=True)

        embed.add_field(name="Max Rarity", value=f"{char.highest_rarity}★", inline=True)
        embed.add_field(name="Total Cards", value=char.card_count, inline=True)

        if char.cards:
            highest_card = max(char.cards, key=lambda c: c.rarity)
            embed.add_field(
                name="Best Running Style",
                value=f"{highest_card.running_style_emoji} {highest_card.running_style_name}",
                inline=False
            )

            # Add character image
            embed.set_image(url=highest_card.image_url)

        embed.set_footer(text="Uma Musume Pretty Derby")
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="ssrchars", description="List all characters with SSR cards")
    async def ssr_characters(self, interaction: discord.Interaction):
        """List all characters with SSR cards."""
        await interaction.response.defer()

        ssr_chars = self.manager.get_by_rarity(3)

        if not ssr_chars:
            await interaction.followup.send("❌ No SSR characters found")
            return

        ssr_chars.sort(key=lambda c: c.chara_id)

        embed = discord.Embed(
            title="✨ SSR Uma Musume Characters",
            description=f"{len(ssr_chars)} characters with SSR cards",
            color=0xFFD700  # Gold color
        )

        char_list = []
        for char in ssr_chars[:30]:  # Limit to 30
            char_list.append(f"★★★ {char.display_name}")

        # Split into columns
        mid = len(char_list) // 2
        if char_list:
            embed.add_field(
                name="Characters (1)",
                value="\n".join(char_list[:mid]) or "None",
                inline=True
            )
            embed.add_field(
                name="Characters (2)",
                value="\n".join(char_list[mid:]) or "None",
                inline=True
            )

        if len(ssr_chars) > 30:
            embed.set_footer(text=f"Showing 30 of {len(ssr_chars)} SSR characters")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Characters(bot))
