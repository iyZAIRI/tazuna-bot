"""Skill commands using slash commands and the database."""
import discord
from discord import app_commands
from discord.ext import commands
import config
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.skill_manager import SkillManager

class SkillSelectorView(discord.ui.View):
    """View for selecting a skill when multiple matches are found."""

    def __init__(self, skills: list, search_query: str = ""):
        super().__init__(timeout=180)
        self.skills = skills
        self.search_query = search_query

        # Add a button for each skill (limit to 25 - Discord limit)
        for idx, skill in enumerate(skills[:25]):
            # Create button label with skill name and rarity
            label = f"{skill.rarity_stars} {skill.display_name[:60]}"  # Truncate if needed

            button = discord.ui.Button(
                label=label,
                style=discord.ButtonStyle.primary,
                custom_id=f"skill_{skill.skill_id}",
                row=idx // 5  # Group into rows of 5
            )
            button.callback = self.create_skill_callback(skill)
            self.add_item(button)

    def create_skill_callback(self, skill):
        """Create a callback for a specific skill button."""
        async def callback(interaction: discord.Interaction):
            # Create detail view with back button
            detail_view = SkillDetailView(skill, self)
            embed = detail_view.create_embed()
            await interaction.response.edit_message(embed=embed, view=detail_view)

        return callback

    def create_selector_embed(self) -> discord.Embed:
        """Create the selector embed showing all matching skills."""
        embed = discord.Embed(
            title="🎯 Multiple Skills Found",
            description=f"Found {len(self.skills)} skills matching '{self.search_query}'. Select one:",
            color=config.EMBED_COLOR
        )

        # Show preview of matches (up to 10)
        preview_list = []
        for i, skill in enumerate(self.skills[:10], 1):
            preview_list.append(f"{i}. {skill.icon_emoji} {skill.rarity_stars} **{skill.display_name}**")

        embed.add_field(
            name="Matches",
            value="\n".join(preview_list),
            inline=False
        )

        if len(self.skills) > 10:
            embed.set_footer(text=f"Showing 10 of {len(self.skills)} matches • Select a skill below")
        else:
            embed.set_footer(text="Select a skill below")

        return embed


class SkillDetailView(discord.ui.View):
    """View for displaying skill details with back button."""

    def __init__(self, skill, parent_selector: SkillSelectorView):
        super().__init__(timeout=180)
        self.skill = skill
        self.parent_selector = parent_selector

        # Back button
        back_button = discord.ui.Button(label="⬅ Back to Skills", style=discord.ButtonStyle.primary)
        back_button.callback = self.go_back
        self.add_item(back_button)

    async def go_back(self, interaction: discord.Interaction):
        """Go back to skill selector."""
        embed = self.parent_selector.create_selector_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_selector)

    def create_embed(self) -> discord.Embed:
        """Create skill detail embed."""
        skill = self.skill
        embed = discord.Embed(
            title=f"{skill.icon_emoji} {skill.display_name}",
            description=skill.description or "No description available",
            color=config.EMBED_COLOR
        )

        embed.add_field(name="Rarity", value=skill.rarity_stars, inline=True)
        embed.add_field(name="Grade Value", value=skill.grade_value, inline=True)

        if skill.is_character_unique:
            embed.add_field(name="Character Unique", value="💎", inline=True)

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

        embed.set_footer(text="Uma Musume Pretty Derby • Skill Database")
        return embed


class Skills(commands.Cog):
    """Skill lookup and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = SkillManager()
        if not self.manager.load():
            print("⚠️  Failed to load skill data")

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.manager.close()

    @app_commands.command(name="skill", description="Look up information about a skill")
    @app_commands.describe(name="Skill name (partial match supported)")
    async def skill(self, interaction: discord.Interaction, name: str):
        """Look up information about a skill."""
        await interaction.response.defer()

        # Search for skills matching the query
        skills = self.manager.search(name)

        if not skills:
            await interaction.followup.send(f"❌ No skills found matching '{name}'.")
            return

        # If multiple matches, show selector
        if len(skills) > 1:
            view = SkillSelectorView(skills, name)
            embed = view.create_selector_embed()
            await interaction.followup.send(embed=embed, view=view)
            return

        # Single match - show directly (no back button needed)
        skill = skills[0]
        embed = discord.Embed(
            title=f"{skill.icon_emoji} {skill.display_name}",
            description=skill.description or "No description available",
            color=config.EMBED_COLOR
        )

        embed.add_field(name="Rarity", value=skill.rarity_stars, inline=True)
        embed.add_field(name="Grade Value", value=skill.grade_value, inline=True)

        if skill.is_character_unique:
            embed.add_field(name="Character Unique", value="💎", inline=True)

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

        embed.set_footer(text="Uma Musume Pretty Derby • Skill Database")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="skills", description="List skills by rarity")
    @app_commands.describe(rarity="Skill rarity (1=R, 2=SR, 3=SSR)")
    @app_commands.choices(rarity=[
        app_commands.Choice(name="⭐ R", value=1),
        app_commands.Choice(name="⭐⭐ SR", value=2),
        app_commands.Choice(name="⭐⭐⭐ SSR", value=3),
    ])
    async def skills_list(self, interaction: discord.Interaction, rarity: Optional[int] = None):
        """List skills, optionally filtered by rarity."""
        await interaction.response.defer()

        if rarity is not None:
            skills = self.manager.get_by_rarity(rarity)
            title = f"{'★' * rarity} Skills"
        else:
            skills = self.manager.get_top(30)
            title = "🏆 Top Skills"

        if not skills:
            await interaction.followup.send("❌ No skills found")
            return

        embed = discord.Embed(
            title=title,
            description=f"{len(skills)} skill(s) found",
            color=config.EMBED_COLOR
        )

        for skill in skills[:25]:  # Limit to 25
            embed.add_field(
                name=f"{skill.icon_emoji} {skill.rarity_stars} {skill.display_name}",
                value=f"Grade: {skill.grade_value}",
                inline=True
            )

        if len(skills) > 25:
            embed.set_footer(text=f"Showing 25 of {len(skills)} skills")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="topskills", description="Show top skills by grade value")
    @app_commands.describe(limit="Number of skills to show (max 50)")
    async def top_skills(self, interaction: discord.Interaction, limit: Optional[int] = 10):
        """Show top skills by grade value."""
        await interaction.response.defer()

        if limit < 1 or limit > 50:
            await interaction.followup.send("❌ Limit must be between 1 and 50")
            return

        skills = self.manager.get_top(limit)

        if not skills:
            await interaction.followup.send("❌ No skills available")
            return

        embed = discord.Embed(
            title=f"🏆 Top {len(skills)} Skills",
            description="Sorted by rarity and grade value",
            color=0xFFD700
        )

        skill_list = []
        for i, skill in enumerate(skills, 1):
            skill_list.append(
                f"{i}. {skill.icon_emoji} {skill.rarity_stars} **{skill.display_name}** ({skill.grade_value})"
            )

        embed.add_field(
            name="Skills",
            value="\n".join(skill_list),
            inline=False
        )

        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Skills(bot))
