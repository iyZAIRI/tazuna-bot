"""Uma Musume specific commands."""
import discord
from discord.ext import commands
import config
import random

class UmaMusume(commands.Cog):
    """Uma Musume Pretty Derby commands."""

    def __init__(self, bot):
        self.bot = bot
        # Sample data - this will be expanded later with real game data
        self.sample_characters = [
            {
                "name": "Special Week",
                "rarity": "★★★",
                "type": "Speed",
                "description": "A promising horse girl from Hokkaido with big dreams!"
            },
            {
                "name": "Silence Suzuka",
                "rarity": "★★★",
                "type": "Runner",
                "description": "Known for her overwhelming speed and lone wolf racing style."
            },
            {
                "name": "Tokai Teio",
                "rarity": "★★★",
                "type": "Runner",
                "description": "The undefeated emperor with incredible talent!"
            },
            {
                "name": "Vodka",
                "rarity": "★★★",
                "type": "Runner",
                "description": "A competitive racer who always gives her all!"
            },
            {
                "name": "Gold Ship",
                "rarity": "★★★",
                "type": "Runner",
                "description": "An unpredictable and quirky horse girl who marches to her own beat."
            }
        ]

    @commands.command(name='character', aliases=['char', 'uma'])
    async def character(self, ctx, *, name: str = None):
        """Look up information about a Uma Musume character.

        Usage: !character <name> or !uma <name>
        Example: !character Special Week
        """
        if not name:
            # Show random character if no name provided
            char = random.choice(self.sample_characters)
        else:
            # Search for character by name
            char = None
            for c in self.sample_characters:
                if name.lower() in c['name'].lower():
                    char = c
                    break

            if not char:
                await ctx.send(f"❌ Character '{name}' not found. Try `{config.COMMAND_PREFIX}list` to see available characters.")
                return

        embed = discord.Embed(
            title=f"🏇 {char['name']}",
            description=char['description'],
            color=config.EMBED_COLOR
        )
        embed.add_field(name="Rarity", value=char['rarity'], inline=True)
        embed.add_field(name="Type", value=char['type'], inline=True)
        embed.set_footer(text="Uma Musume Pretty Derby")
        await ctx.send(embed=embed)

    @commands.command(name='list', aliases=['characters'])
    async def list_characters(self, ctx):
        """List all available Uma Musume characters."""
        embed = discord.Embed(
            title="🏇 Uma Musume Characters",
            description="Here are the available characters:",
            color=config.EMBED_COLOR
        )

        for char in self.sample_characters:
            embed.add_field(
                name=f"{char['rarity']} {char['name']}",
                value=f"Type: {char['type']}",
                inline=False
            )

        embed.set_footer(text=f"Use {config.COMMAND_PREFIX}character <name> for more info")
        await ctx.send(embed=embed)

    @commands.command(name='random', aliases=['randomuma'])
    async def random_character(self, ctx):
        """Get a random Uma Musume character."""
        char = random.choice(self.sample_characters)
        embed = discord.Embed(
            title="🎲 Random Uma Musume!",
            description=f"You got **{char['name']}**!",
            color=config.EMBED_COLOR
        )
        embed.add_field(name="Rarity", value=char['rarity'], inline=True)
        embed.add_field(name="Type", value=char['type'], inline=True)
        embed.add_field(name="About", value=char['description'], inline=False)
        await ctx.send(embed=embed)

    @commands.command(name='gacha', aliases=['roll', 'pull'])
    async def gacha(self, ctx, rolls: int = 1):
        """Simulate a gacha roll!

        Usage: !gacha [number_of_rolls]
        Example: !gacha 10
        """
        if rolls < 1 or rolls > 10:
            await ctx.send("❌ You can roll between 1 and 10 times!")
            return

        results = []
        for _ in range(rolls):
            # Simple gacha simulation with rarity weights
            roll = random.randint(1, 100)
            if roll <= 3:  # 3% SSR
                rarity = "★★★ (SSR)"
            elif roll <= 18:  # 15% SR
                rarity = "★★ (SR)"
            else:  # 82% R
                rarity = "★ (R)"

            char = random.choice(self.sample_characters)
            results.append(f"{rarity} {char['name']}")

        embed = discord.Embed(
            title="🎰 Gacha Results!",
            description=f"You rolled {rolls} time(s):",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="Results",
            value="\n".join(results),
            inline=False
        )
        embed.set_footer(text="Good luck, Trainer!")
        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(UmaMusume(bot))
