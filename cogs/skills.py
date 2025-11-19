"""Skill commands using the database."""
import discord
from discord.ext import commands
import config
import sys
from pathlib import Path

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

    @commands.command(name='skill')
    async def skill(self, ctx, *, name: str):
        """Look up information about a skill.

        Usage: !skill <name>
        Example: !skill acceleration
        """
        skill = self.manager.get_by_name(name)

        if not skill:
            await ctx.send(f"❌ Skill '{name}' not found.")
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
            embed.add_field(
                name="Activation Condition",
                value=f"```{skill.condition}```",
                inline=False
            )

        if skill.is_unique:
            embed.add_field(name="Type", value="✨ Unique Skill", inline=True)
        elif skill.is_debuff:
            embed.add_field(name="Type", value="❌ Debuff", inline=True)

        embed.set_footer(text="Uma Musume Pretty Derby • Skill Database")
        await ctx.send(embed=embed)

    @commands.command(name='skills', aliases=['skilllist'])
    async def skills_list(self, ctx, rarity: int = None):
        """List skills, optionally filtered by rarity.

        Usage: !skills [rarity]
        Example: !skills 3
        """
        if rarity is not None:
            if rarity < 1 or rarity > 3:
                await ctx.send("❌ Rarity must be 1, 2, or 3")
                return
            skills = self.manager.get_by_rarity(rarity)
            title = f"{'★' * rarity} Skills"
        else:
            skills = self.manager.get_top(30)
            title = "🏆 Top Skills"

        if not skills:
            await ctx.send("❌ No skills found")
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

        await ctx.send(embed=embed)

    @commands.command(name='searchskill', aliases=['findskill'])
    async def search_skill(self, ctx, *, query: str):
        """Search for skills by name.

        Usage: !searchskill <query>
        Example: !searchskill speed
        """
        results = self.manager.search(query)

        if not results:
            await ctx.send(f"❌ No skills found matching '{query}'")
            return

        embed = discord.Embed(
            title=f"🔍 Skill Search: '{query}'",
            description=f"Found {len(results)} skill(s)",
            color=config.EMBED_COLOR
        )

        for skill in results[:20]:  # Limit to 20
            embed.add_field(
                name=f"{skill.rarity_stars} {skill.display_name}",
                value=f"ID: {skill.skill_id} • Grade: {skill.grade_value}",
                inline=True
            )

        if len(results) > 20:
            embed.set_footer(text=f"Showing 20 of {len(results)} results")

        await ctx.send(embed=embed)

    @commands.command(name='topskills')
    async def top_skills(self, ctx, limit: int = 10):
        """Show top skills by grade value.

        Usage: !topskills [limit]
        Example: !topskills 20
        """
        if limit < 1 or limit > 50:
            await ctx.send("❌ Limit must be between 1 and 50")
            return

        skills = self.manager.get_top(limit)

        if not skills:
            await ctx.send("❌ No skills available")
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

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Skills(bot))
