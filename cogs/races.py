"""Race commands using slash commands and the database."""
import discord
from discord import app_commands
from discord.ext import commands
import config
import sys
from pathlib import Path
from typing import Optional

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.race_manager import RaceManager

class Races(commands.Cog):
    """Race lookup and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.manager = RaceManager()
        if not self.manager.load():
            print("⚠️  Failed to load race data")

    def cog_unload(self):
        """Clean up when cog is unloaded."""
        self.manager.close()

    @app_commands.command(name="race", description="Look up information about a race")
    @app_commands.describe(name="Race name (partial match supported)")
    async def race(self, interaction: discord.Interaction, name: str):
        """Look up information about a race."""
        await interaction.response.defer()

        race = self.manager.get_by_name(name)

        if not race:
            await interaction.followup.send(f"❌ Race '{name}' not found.")
            return

        embed = discord.Embed(
            title=f"{race.grade_emoji} {race.display_name}",
            color=config.EMBED_COLOR
        )

        embed.add_field(name="Grade", value=f"{race.grade_emoji} {race.grade_name}", inline=True)
        embed.add_field(name="Distance", value=f"{race.formatted_distance} ({race.distance_category})", inline=True)
        embed.add_field(name="Ground", value=f"{race.ground_emoji} {race.ground_name}", inline=True)
        embed.add_field(name="Track ID", value=race.track_id, inline=True)
        embed.add_field(name="Race ID", value=race.race_id, inline=True)

        embed.set_footer(text="Uma Musume Pretty Derby • Race Database")
        await interaction.followup.send(embed=embed)

    @app_commands.command(name="races", description="List races by grade")
    @app_commands.describe(grade="Race grade")
    @app_commands.choices(grade=[
        app_commands.Choice(name="🥉 Pre-Open", value=1),
        app_commands.Choice(name="🥈 Open", value=2),
        app_commands.Choice(name="🥉 G3", value=3),
        app_commands.Choice(name="🥈 G2", value=4),
        app_commands.Choice(name="🥇 G1", value=5),
    ])
    async def races_list(self, interaction: discord.Interaction, grade: Optional[int] = None):
        """List races, optionally filtered by grade."""
        await interaction.response.defer()

        if grade is not None:
            races = self.manager.get_by_grade(grade)
            race_obj = races[0] if races else None
            title = f"{race_obj.grade_emoji} {race_obj.grade_name} Races" if race_obj else "Races"
        else:
            races = self.manager.get_g1_races()
            title = "🥇 G1 Races"

        if not races:
            await interaction.followup.send("❌ No races found")
            return

        # Sort by distance
        races.sort(key=lambda r: r.distance)

        embed = discord.Embed(
            title=title,
            description=f"{len(races)} race(s) found",
            color=config.EMBED_COLOR
        )

        for race in races[:25]:  # Limit to 25
            embed.add_field(
                name=f"{race.grade_emoji} {race.display_name}",
                value=f"{race.formatted_distance} • {race.ground_emoji} {race.ground_name}",
                inline=True
            )

        if len(races) > 25:
            embed.set_footer(text=f"Showing 25 of {len(races)} races")

        await interaction.followup.send(embed=embed)

    @app_commands.command(name="g1races", description="List all G1 races")
    async def g1_races(self, interaction: discord.Interaction):
        """List all G1 races."""
        await interaction.response.defer()

        races = self.manager.get_g1_races()

        if not races:
            await interaction.followup.send("❌ No G1 races found")
            return

        races.sort(key=lambda r: r.distance)

        embed = discord.Embed(
            title="🥇 G1 Races",
            description=f"{len(races)} G1 races",
            color=0xFFD700
        )

        race_list = []
        for race in races[:30]:  # Limit to 30
            race_list.append(
                f"🏆 **{race.display_name}** - {race.formatted_distance} {race.ground_emoji}"
            )

        # Split into columns if needed
        mid = len(race_list) // 2
        if race_list:
            embed.add_field(
                name="Races (1)",
                value="\n".join(race_list[:mid]) or "None",
                inline=True
            )
            if mid < len(race_list):
                embed.add_field(
                    name="Races (2)",
                    value="\n".join(race_list[mid:]) or "None",
                    inline=True
                )

        if len(races) > 30:
            embed.set_footer(text=f"Showing 30 of {len(races)} races")

        await interaction.followup.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Races(bot))
