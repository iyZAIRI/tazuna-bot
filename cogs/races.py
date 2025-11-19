"""Race commands using the database."""
import discord
from discord.ext import commands
import config
import sys
from pathlib import Path

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

    @commands.command(name='race')
    async def race(self, ctx, *, name: str):
        """Look up information about a race.

        Usage: !race <name>
        Example: !race Japan Cup
        """
        race = self.manager.get_by_name(name)

        if not race:
            await ctx.send(f"❌ Race '{name}' not found.")
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
        await ctx.send(embed=embed)

    @commands.command(name='races', aliases=['racelist'])
    async def races_list(self, ctx, grade: int = None):
        """List races, optionally filtered by grade.

        Usage: !races [grade]
        Grades: 1 (Pre-Open), 2 (Open), 3 (G3), 4 (G2), 5 (G1)
        Example: !races 5
        """
        if grade is not None:
            if grade < 1 or grade > 5:
                await ctx.send("❌ Grade must be between 1 and 5")
                return
            races = self.manager.get_by_grade(grade)
            race_obj = races[0] if races else None
            title = f"{race_obj.grade_emoji} {race_obj.grade_name} Races" if race_obj else "Races"
        else:
            races = self.manager.get_g1_races()
            title = "🥇 G1 Races"

        if not races:
            await ctx.send("❌ No races found")
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

        await ctx.send(embed=embed)

    @commands.command(name='g1races', aliases=['g1'])
    async def g1_races(self, ctx):
        """List all G1 races."""
        races = self.manager.get_g1_races()

        if not races:
            await ctx.send("❌ No G1 races found")
            return

        races.sort(key=lambda r: r.distance)

        embed = discord.Embed(
            title="🥇 G1 Races",
            description=f"{len(races)} G1 races",
            color=0xFFD700
        )

        race_list = []
        for race in races:
            race_list.append(
                f"🏆 **{race.display_name}** - {race.formatted_distance} {race.ground_emoji}"
            )

        # Split into columns if too many
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

        await ctx.send(embed=embed)

    @commands.command(name='searchrace', aliases=['findrace'])
    async def search_race(self, ctx, *, query: str):
        """Search for races by name.

        Usage: !searchrace <query>
        Example: !searchrace cup
        """
        results = self.manager.search(query)

        if not results:
            await ctx.send(f"❌ No races found matching '{query}'")
            return

        embed = discord.Embed(
            title=f"🔍 Race Search: '{query}'",
            description=f"Found {len(results)} race(s)",
            color=config.EMBED_COLOR
        )

        for race in results[:20]:
            embed.add_field(
                name=f"{race.grade_emoji} {race.display_name}",
                value=f"{race.formatted_distance} • {race.ground_emoji}",
                inline=True
            )

        if len(results) > 20:
            embed.set_footer(text=f"Showing 20 of {len(results)} results")

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Races(bot))
