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
from managers.skill_manager import SkillManager
from models.character import Character, CharacterCard
from constants import (
    EMOJI_SPEED, EMOJI_STAMINA, EMOJI_POWER, EMOJI_GUTS, EMOJI_WIT,
    EMOJI_FRONT_RUNNER, EMOJI_PACE_CHASER, EMOJI_LATE, EMOJI_END_CLOSER
)

class CharacterListView(discord.ui.View):
    """Paginated view for displaying character list."""

    def __init__(self, characters: list, page: int = 0, per_page: int = 15):
        super().__init__(timeout=180)
        self.characters = characters
        self.page = page
        self.per_page = per_page
        self.total_pages = (len(characters) + per_page - 1) // per_page

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
        """Create the character list embed for current page."""
        embed = discord.Embed(
            title="🏇 Uma Musume Characters",
            description=f"Page {self.page + 1}/{self.total_pages} • {len(self.characters)} total characters",
            color=config.EMBED_COLOR
        )

        start_idx = self.page * self.per_page
        end_idx = min(start_idx + self.per_page, len(self.characters))
        page_chars = self.characters[start_idx:end_idx]

        for char in page_chars:
            version_text = "version" if char.card_count == 1 else "versions"
            embed.add_field(
                name=f"{char.highest_rarity}★ {char.display_name}",
                value=f"{char.card_count} {version_text}",
                inline=True
            )

        embed.set_footer(text=f"Use /character <name> for details • Page {self.page + 1}/{self.total_pages}")
        return embed


class CardSelectorView(discord.ui.View):
    """View for selecting character cards/alts."""

    def __init__(self, character: Character, skill_manager: SkillManager):
        super().__init__(timeout=180)  # 3 minute timeout
        self.character = character
        self.skill_manager = skill_manager

        # Add a button for each card (limit to 25 buttons total - Discord limit)
        for idx, card in enumerate(character.cards[:25]):
            # Create button label with card title if available
            if card.card_title:
                # Truncate title if too long (Discord button label limit is 80 chars)
                title = card.card_title[:50] if len(card.card_title) > 50 else card.card_title
                label = f"{card.rarity_stars} {title}"
            else:
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
            # Create a new view with pagination for this card
            detail_view = CardDetailView(self.character, card, self, self.skill_manager)
            embed = detail_view.create_stats_embed()
            await interaction.response.edit_message(embed=embed, view=detail_view)

        return callback


class CardDetailView(discord.ui.View):
    """View for displaying card details with pagination between stats and skills."""

    def __init__(self, character: Character, card: CharacterCard, parent_view: CardSelectorView, skill_manager: SkillManager):
        super().__init__(timeout=180)
        self.character = character
        self.card = card
        self.parent_view = parent_view
        self.skill_manager = skill_manager
        self.current_page = 0  # 0 = stats, 1 = skills

        # Add navigation buttons
        self.prev_button = discord.ui.Button(label="◀ Prev", style=discord.ButtonStyle.secondary, disabled=True)
        self.prev_button.callback = self.prev_page
        self.add_item(self.prev_button)

        self.next_button = discord.ui.Button(label="Skills ▶", style=discord.ButtonStyle.secondary)
        self.next_button.callback = self.next_page
        self.add_item(self.next_button)

        self.back_button = discord.ui.Button(label="⬅ Back to Cards", style=discord.ButtonStyle.primary)
        self.back_button.callback = self.go_back
        self.add_item(self.back_button)

        # Add skill select menu (will be shown only on skills page)
        self.skill_select = None

    async def prev_page(self, interaction: discord.Interaction):
        """Go to previous page."""
        self.current_page = 0
        await self.update_view(interaction)

    async def next_page(self, interaction: discord.Interaction):
        """Go to next page."""
        self.current_page = 1
        await self.update_view(interaction)

    async def go_back(self, interaction: discord.Interaction):
        """Go back to card selection."""
        embed = discord.Embed(
            title=f"🏇 {self.character.display_name}",
            description=f"Select a card to view details ({len(self.character.cards)} available)",
            color=self.character.get_hex_color()
        )
        await interaction.response.edit_message(embed=embed, view=self.parent_view)

    async def update_view(self, interaction: discord.Interaction):
        """Update the embed based on current page."""
        # Update button states
        self.prev_button.disabled = (self.current_page == 0)
        self.next_button.disabled = (self.current_page == 1)
        self.prev_button.label = "◀ Stats" if self.current_page == 1 else "◀ Prev"
        self.next_button.label = "Skills ▶" if self.current_page == 0 else "Next ▶"

        # Add/remove skill select menu based on page
        if self.current_page == 1 and self.skill_select is None:
            # On skills page, add select menu
            self._add_skill_select()
        elif self.current_page == 0 and self.skill_select is not None:
            # Not on skills page, remove select menu
            self.remove_item(self.skill_select)
            self.skill_select = None

        if self.current_page == 0:
            embed = self.create_stats_embed()
        else:
            embed = self.create_skills_embed()

        await interaction.response.edit_message(embed=embed, view=self)

    def _add_skill_select(self):
        """Add skill select menu to the view."""
        # Collect all skills from the card
        all_skills = []

        # Add unique skill first
        if self.card.unique_skill:
            all_skills.append(('💎', self.card.unique_skill))

        # Add innate skills
        for skill in [s for s in self.card.skills if s.need_rank == 0]:
            all_skills.append(('✨', skill))

        # Add awakening skills
        for skill in [s for s in self.card.skills if s.need_rank > 0]:
            all_skills.append(('⭐', skill))

        # Only add select if there are skills
        if not all_skills:
            return

        # Create select menu options (limit to 25 - Discord limit)
        options = []
        for emoji, skill in all_skills[:25]:
            # Truncate skill name if too long (max 100 chars for select option label)
            skill_name = skill.skill_name[:97] + "..." if len(skill.skill_name) > 100 else skill.skill_name
            options.append(
                discord.SelectOption(
                    label=skill_name,
                    value=str(skill.skill_id),
                    emoji=emoji
                )
            )

        # Create select menu
        self.skill_select = discord.ui.Select(
            placeholder="📖 View skill details...",
            options=options,
            row=4  # Put in last row
        )
        self.skill_select.callback = self.skill_selected
        self.add_item(self.skill_select)

    async def skill_selected(self, interaction: discord.Interaction):
        """Handle skill selection from dropdown."""
        skill_id = int(interaction.data['values'][0])

        # Find the skill from card
        selected_skill = None
        if self.card.unique_skill and self.card.unique_skill.skill_id == skill_id:
            selected_skill = self.card.unique_skill
        else:
            for skill in self.card.skills:
                if skill.skill_id == skill_id:
                    selected_skill = skill
                    break

        if not selected_skill:
            await interaction.response.send_message("❌ Skill not found", ephemeral=True)
            return

        # Create skill detail view
        skill_view = SkillDetailView(selected_skill, self, self.skill_manager)
        embed = skill_view.create_embed()
        await interaction.response.edit_message(embed=embed, view=skill_view)

    def create_stats_embed(self) -> discord.Embed:
        """Create the stats page embed."""
        card = self.card
        embed = discord.Embed(
            title=f"{card.running_style_emoji} {self.character.display_name}",
            description=f"📄 Page 1/2: Stats & Aptitudes",
            color=self.character.get_hex_color()
        )

        # Card details
        embed.add_field(name="Rarity", value=card.rarity_stars, inline=True)
        embed.add_field(name="Running Style", value=f"{card.running_style_emoji} {card.running_style_name}", inline=True)
        embed.add_field(name="\u200b", value="\u200b", inline=True)  # Spacer

        # Card title
        if card.card_title:
            embed.add_field(name="Card Title", value=card.card_title, inline=False)

        # Bonuses (compact format)
        bonuses_text = (
            f"{EMOJI_SPEED} {card.talent_speed}% | "
            f"{EMOJI_STAMINA} {card.talent_stamina}% | "
            f"{EMOJI_POWER} {card.talent_power}% | "
            f"{EMOJI_GUTS} {card.talent_guts}% | "
            f"{EMOJI_WIT} {card.talent_wit}%"
        )
        embed.add_field(
            name="💎 Bonuses",
            value=bonuses_text,
            inline=False
        )

        # Base stats at default rarity
        if card.base_speed is not None:
            base_stats_text = (
                f"{EMOJI_SPEED} {card.base_speed}  |  "
                f"{EMOJI_STAMINA} {card.base_stamina}  |  "
                f"{EMOJI_POWER} {card.base_power}  |  "
                f"{EMOJI_GUTS} {card.base_guts}  |  "
                f"{EMOJI_WIT} {card.base_wit}"
            )
            embed.add_field(
                name=f"📊 Base Stats ({card.rarity_stars})",
                value=base_stats_text,
                inline=False
            )

        # Base stats at max rarity (5)
        if card.max_base_speed is not None:
            max_stats_text = (
                f"{EMOJI_SPEED} {card.max_base_speed}  |  "
                f"{EMOJI_STAMINA} {card.max_base_stamina}  |  "
                f"{EMOJI_POWER} {card.max_base_power}  |  "
                f"{EMOJI_GUTS} {card.max_base_guts}  |  "
                f"{EMOJI_WIT} {card.max_base_wit}"
            )
            embed.add_field(
                name="📈 Base Stats (★★★★★)",
                value=max_stats_text,
                inline=False
            )

        # Aptitudes - Distance
        if card.apt_distance_short is not None:
            distance_apt = (
                f"Sprint: {card.aptitude_to_grade(card.apt_distance_short)} | "
                f"Mile: {card.aptitude_to_grade(card.apt_distance_mile)} | "
                f"Medium: {card.aptitude_to_grade(card.apt_distance_middle)} | "
                f"Long: {card.aptitude_to_grade(card.apt_distance_long)}"
            )
            embed.add_field(
                name="🏁 Distance Aptitude",
                value=distance_apt,
                inline=False
            )

        # Aptitudes - Running Style
        if card.apt_style_front_runner is not None:
            style_apt = (
                f"{EMOJI_FRONT_RUNNER} Front Runner: {card.aptitude_to_grade(card.apt_style_front_runner)} | "
                f"{EMOJI_PACE_CHASER} Pace Chaser: {card.aptitude_to_grade(card.apt_style_pace_chaser)}\n"
                f"{EMOJI_LATE} Late: {card.aptitude_to_grade(card.apt_style_late)} | "
                f"{EMOJI_END_CLOSER} End Closer: {card.aptitude_to_grade(card.apt_style_end_closer)}"
            )
            embed.add_field(
                name="🎽 Running Style Aptitude",
                value=style_apt,
                inline=False
            )

        # Aptitudes - Ground
        if card.apt_ground_turf is not None:
            ground_apt = (
                f"Turf: {card.aptitude_to_grade(card.apt_ground_turf)} | "
                f"Dirt: {card.aptitude_to_grade(card.apt_ground_dirt)}"
            )
            embed.add_field(
                name="🌱 Ground Aptitude",
                value=ground_apt,
                inline=False
            )

        # Card image
        embed.set_image(url=card.image_url)
        embed.set_footer(text=f"Uma Musume Pretty Derby • Page 1/2")

        return embed

    def create_skills_embed(self) -> discord.Embed:
        """Create the skills page embed."""
        card = self.card
        embed = discord.Embed(
            title=f"{card.running_style_emoji} {self.character.display_name}",
            description=f"📄 Page 2/2: Skills",
            color=self.character.get_hex_color()
        )

        # Card title
        if card.card_title:
            embed.add_field(name="Card", value=f"{card.rarity_stars} {card.card_title}", inline=False)

        # Unique Skill (unlocked at rarity 3+)
        if card.unique_skill:
            embed.add_field(
                name="💎 Unique Skill",
                value=f"{card.unique_skill.icon_emoji} {card.unique_skill.skill_name}\n*Unlocked at rarity 3+*",
                inline=False
            )

        # Separate skills into innate (rank 0) and awakening (rank 2-5)
        innate_skills = [s for s in card.skills if s.need_rank == 0]
        awakening_skills = [s for s in card.skills if s.need_rank > 0]

        # Innate Skills (unlocked by default)
        if innate_skills:
            innate_text = ""
            for skill in innate_skills:
                innate_text += f"{skill.icon_emoji} {skill.skill_name}\n"

            embed.add_field(
                name=f"✨ Innate Skills ({len(innate_skills)})",
                value=innate_text,
                inline=False
            )

        # Awakening Skills (requires bond levels)
        if awakening_skills:
            awakening_text = ""
            for skill in awakening_skills:
                awakening_text += f"{skill.icon_emoji} {skill.skill_name} {skill.rank_emoji}\n"

            embed.add_field(
                name=f"⭐ Awakening Skills ({len(awakening_skills)})",
                value=awakening_text,
                inline=False
            )

        if not card.unique_skill and not card.skills:
            embed.add_field(
                name="✨ Available Skills",
                value="No skills found for this card.",
                inline=False
            )

        # Card image
        embed.set_image(url=card.image_url)
        embed.set_footer(text=f"Uma Musume Pretty Derby • Page 2/2")

        return embed


class SkillDetailView(discord.ui.View):
    """View for displaying skill details with navigation back to card skills."""

    def __init__(self, skill, card_detail_view: 'CardDetailView', skill_manager: SkillManager):
        super().__init__(timeout=180)
        self.skill_obj = skill_manager.get_by_id(skill.skill_id)
        self.card_detail_view = card_detail_view
        self.skill_manager = skill_manager

        # Back button to return to card skills
        back_button = discord.ui.Button(label="⬅ Back to Skills", style=discord.ButtonStyle.primary)
        back_button.callback = self.go_back
        self.add_item(back_button)

    async def go_back(self, interaction: discord.Interaction):
        """Go back to card skills page."""
        # Set card detail view to skills page
        self.card_detail_view.current_page = 1
        embed = self.card_detail_view.create_skills_embed()
        await interaction.response.edit_message(embed=embed, view=self.card_detail_view)

    def create_embed(self) -> discord.Embed:
        """Create skill detail embed."""
        skill = self.skill_obj
        if not skill:
            return discord.Embed(
                title="❌ Skill Not Found",
                description="Unable to load skill details",
                color=config.ERROR_COLOR
            )

        embed = discord.Embed(
            title=f"{skill.icon_emoji} {skill.display_name}",
            description=skill.description or "No description available",
            color=config.EMBED_COLOR
        )

        # Display activation type
        activation_type = "Wisdom Check" if skill.requires_wisdom else "Guaranteed"
        embed.add_field(name="Activation", value=activation_type, inline=True)

        # Display SP cost (only for non-unique skills)
        if skill.sp_cost is not None:
            embed.add_field(name="SP Cost", value=str(skill.sp_cost), inline=True)

        if skill.is_character_unique:
            char_display = skill.unique_character_name if skill.unique_character_name else "💎"
            embed.add_field(name="Character Unique", value=char_display, inline=True)

        # Display effects
        effect_lines = []
        has_multiple_abilities = skill.ability_1 and skill.ability_2

        if skill.ability_1:
            ability_1_lines = skill.ability_1.get_effect_lines()
            if ability_1_lines:
                if has_multiple_abilities:
                    effect_lines.append("**Trigger 1:**")
                effect_lines.extend(ability_1_lines)

        if skill.ability_2:
            ability_2_lines = skill.ability_2.get_effect_lines()
            if ability_2_lines:
                if effect_lines:
                    effect_lines.append("")  # Blank line between triggers
                effect_lines.append("**Trigger 2:**")
                effect_lines.extend(ability_2_lines)

        if effect_lines:
            embed.add_field(
                name="Effect",
                value="\n".join(effect_lines),
                inline=False
            )

        embed.set_footer(text="Uma Musume Pretty Derby • Skill Details")
        return embed


class Characters(commands.Cog):
    """Character lookup and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = CharacterManager()
        self.skill_manager = SkillManager()
        # Load data on initialization
        if not self.manager.load():
            print("⚠️  Failed to load character data")
        if not self.skill_manager.load():
            print("⚠️  Failed to load skill data")

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.manager.close()
        self.skill_manager.close()

    async def character_name_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> list[app_commands.Choice[str]]:
        """Autocomplete for character names."""
        # If no input, show first 25 characters
        if not current:
            all_chars = self.manager.get_all()
            all_chars.sort(key=lambda c: c.display_name)
            return [
                app_commands.Choice(name=char.display_name, value=char.display_name)
                for char in all_chars[:25]
            ]

        # Search for matching characters
        matches = self.manager.search(current)
        matches.sort(key=lambda c: c.display_name)

        # Return up to 25 matches (Discord limit)
        return [
            app_commands.Choice(name=char.display_name, value=char.display_name)
            for char in matches[:25]
        ]

    @app_commands.command(name="character", description="Look up information about a character")
    @app_commands.describe(name="Character name")
    @app_commands.autocomplete(name=character_name_autocomplete)
    async def character(self, interaction: discord.Interaction, name: str):
        """Look up information about a Uma Musume character."""
        await interaction.response.defer()

        # Search for character by name
        # Try exact match first, then partial match
        char = self.manager.get_by_name(name)

        # If partial match returns multiple results, try to find exact match
        if not char:
            matches = self.manager.search(name)
            if len(matches) == 1:
                char = matches[0]
            elif len(matches) > 1:
                # Multiple matches found - list them
                match_names = ", ".join([c.display_name for c in matches[:10]])
                await interaction.followup.send(
                    f"❌ Multiple characters match '{name}': {match_names}\n"
                    f"Please be more specific or use autocomplete."
                )
                return

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
        view = CardSelectorView(char, self.skill_manager)

        # Send with buttons
        await interaction.followup.send(embed=embed, view=view)

    @app_commands.command(name="characters", description="List all available characters")
    async def characters(self, interaction: discord.Interaction):
        """List all available Uma Musume characters."""
        await interaction.response.defer()

        all_chars = self.manager.get_all()

        if not all_chars:
            await interaction.followup.send("❌ No characters available")
            return

        # Sort by ID
        all_chars.sort(key=lambda c: c.chara_id)

        # Create paginated view
        view = CharacterListView(all_chars)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Characters(bot))
