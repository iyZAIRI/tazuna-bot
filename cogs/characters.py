"""Character commands using the database."""
import discord
from discord.ext import commands
import config
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.character_manager import CharacterManager

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

    @commands.command(name='character', aliases=['char', 'uma'])
    async def character(self, ctx, *, name: str = None):
        """Look up information about a Uma Musume character.

        Usage: !character <name> or !uma <name>
        Example: !character Special Week
        """
        if not name:
            # Show random character if no name provided
            char = self.manager.get_random()
            if not char:
                await ctx.send("❌ No characters available")
                return
        else:
            # Search for character by name
            char = self.manager.get_by_name(name)

            if not char:
                await ctx.send(f"❌ Character '{name}' not found. Try `{config.COMMAND_PREFIX}list` to see available characters.")
                return

        # Create embed
        embed = discord.Embed(
            title=f"🏇 {char.display_name}",
            color=char.get_hex_color()
        )

        # Character info
        if char.birth_date:
            embed.add_field(name="Birthday", value=char.birth_date, inline=True)

        embed.add_field(name="Character ID", value=char.chara_id, inline=True)
        embed.add_field(name="Cards", value=char.card_count, inline=True)

        # Card information
        if char.cards:
            card_info = []
            for card in char.cards[:5]:  # Show max 5 cards
                card_info.append(
                    f"{card.rarity_stars} - {card.running_style_emoji} {card.running_style_name}"
                )

            embed.add_field(
                name=f"Available Cards ({len(char.cards)})",
                value="\n".join(card_info) or "None",
                inline=False
            )

            # Talents from highest rarity card
            highest_card = max(char.cards, key=lambda c: c.rarity)
            talent_text = (
                f"Speed: {highest_card.talent_speed} | "
                f"Stamina: {highest_card.talent_stamina} | "
                f"Power: {highest_card.talent_power}\n"
                f"Guts: {highest_card.talent_guts} | "
                f"Wisdom: {highest_card.talent_wisdom}"
            )
            embed.add_field(
                name="Base Talents (Highest Rarity Card)",
                value=talent_text,
                inline=False
            )

        embed.set_footer(text=f"Uma Musume Pretty Derby • {char.highest_rarity}★ Max")
        await ctx.send(embed=embed)

    @commands.command(name='list', aliases=['characters', 'charlist'])
    async def list_characters(self, ctx, page: int = 1):
        """List all available Uma Musume characters.

        Usage: !list [page]
        Example: !list 2
        """
        all_chars = self.manager.get_all()

        if not all_chars:
            await ctx.send("❌ No characters available")
            return

        # Sort by ID
        all_chars.sort(key=lambda c: c.chara_id)

        # Pagination
        per_page = 15
        total_pages = (len(all_chars) + per_page - 1) // per_page

        if page < 1 or page > total_pages:
            await ctx.send(f"❌ Invalid page. Available pages: 1-{total_pages}")
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

        embed.set_footer(text=f"Use {config.COMMAND_PREFIX}character <name> for details • Page {page}/{total_pages}")
        await ctx.send(embed=embed)

    @commands.command(name='random', aliases=['randomuma', 'randomchar'])
    async def random_character(self, ctx):
        """Get a random Uma Musume character."""
        char = self.manager.get_random()

        if not char:
            await ctx.send("❌ No characters available")
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

        embed.set_footer(text="Uma Musume Pretty Derby")
        await ctx.send(embed=embed)

    @commands.command(name='search', aliases=['find', 'charsearch'])
    async def search(self, ctx, *, query: str):
        """Search for characters by name.

        Usage: !search <query>
        Example: !search week
        """
        results = self.manager.search(query)

        if not results:
            await ctx.send(f"❌ No characters found matching '{query}'")
            return

        embed = discord.Embed(
            title=f"🔍 Search Results for '{query}'",
            description=f"Found {len(results)} character(s)",
            color=config.EMBED_COLOR
        )

        for char in results[:15]:  # Limit to 15 results
            embed.add_field(
                name=f"{char.highest_rarity}★ {char.display_name}",
                value=f"ID: {char.chara_id}",
                inline=True
            )

        if len(results) > 15:
            embed.set_footer(text=f"Showing 15 of {len(results)} results")

        await ctx.send(embed=embed)

    @commands.command(name='ssr', aliases=['ssrchars'])
    async def ssr_characters(self, ctx):
        """List all characters with SSR cards."""
        ssr_chars = self.manager.get_by_rarity(3)

        if not ssr_chars:
            await ctx.send("❌ No SSR characters found")
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

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Characters(bot))
