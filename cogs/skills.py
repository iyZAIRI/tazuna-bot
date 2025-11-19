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

        skill = self.manager.get_by_name(name)

        if not skill:
            await interaction.followup.send(f"❌ Skill '{name}' not found.")
            return

        embed = discord.Embed(
            title=f"{skill.category_emoji} {skill.display_name}",
            description=skill.description or "No description available",
            color=config.EMBED_COLOR
        )

        embed.add_field(name="Rarity", value=skill.rarity_stars, inline=True)
        embed.add_field(name="Grade Value", value=skill.grade_value, inline=True)
        embed.add_field(name="Skill ID", value=skill.skill_id, inline=True)

        if skill.condition:
            condition_text = skill.condition[:200] + "..." if len(skill.condition) > 200 else skill.condition
            embed.add_field(
                name="Activation Condition",
                value=f"```{condition_text}```",
                inline=False
            )

        if skill.is_unique:
            embed.add_field(name="Type", value="✨ Unique Skill", inline=True)
        elif skill.is_debuff:
            embed.add_field(name="Type", value="❌ Debuff", inline=True)

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
                name=f"{skill.rarity_stars} {skill.display_name}",
                value=f"Grade: {skill.grade_value} {skill.category_emoji}",
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
                f"{i}. {skill.rarity_stars} **{skill.display_name}** ({skill.grade_value})"
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
