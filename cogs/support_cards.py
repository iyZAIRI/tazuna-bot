"""Support card commands using the database."""
import discord
from discord.ext import commands
import config
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.support_card_manager import SupportCardManager

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

    @commands.command(name='support', aliases=['supportcard', 'sc'])
    async def support(self, ctx, *, name: str):
        """Look up information about a support card.

        Usage: !support <name>
        Example: !support Special Week
        """
        card = self.manager.get_by_name(name)

        if not card:
            await ctx.send(f"❌ Support card '{name}' not found.")
            return

        embed = discord.Embed(
            title=f"{card.type_emoji} {card.display_name}",
            color=card.type_color
        )

        embed.add_field(name="Rarity", value=card.rarity_stars, inline=True)
        embed.add_field(name="Type", value=f"{card.type_emoji} {card.type_name}", inline=True)
        embed.add_field(name="Card ID", value=card.card_id, inline=True)

        if card.character_name:
            embed.add_field(name="Character", value=card.character_name, inline=True)

        embed.add_field(name="Character ID", value=card.chara_id, inline=True)

        embed.set_footer(text="Uma Musume Pretty Derby • Support Cards")
        await ctx.send(embed=embed)

    @commands.command(name='supports', aliases=['supportlist', 'sclist'])
    async def supports_list(self, ctx, filter_type: str = None):
        """List support cards, optionally filtered by type.

        Usage: !supports [type]
        Types: speed, stamina, power, guts, wisdom, friend
        Example: !supports speed
        """
        if filter_type:
            type_map = {
                'speed': 1,
                'stamina': 2,
                'power': 3,
                'guts': 4,
                'wisdom': 5,
                'friend': 6
            }

            type_lower = filter_type.lower()
            if type_lower not in type_map:
                await ctx.send(f"❌ Invalid type. Use: {', '.join(type_map.keys())}")
                return

            cards = self.manager.get_by_type(type_map[type_lower])
            title = f"{cards[0].type_emoji} {cards[0].type_name} Support Cards" if cards else "Support Cards"
            color = cards[0].type_color if cards else config.EMBED_COLOR
        else:
            cards = self.manager.get_ssr_cards()
            title = "✨ SSR Support Cards"
            color = 0xFFD700

        if not cards:
            await ctx.send("❌ No support cards found")
            return

        # Sort by rarity descending
        cards.sort(key=lambda c: c.rarity, reverse=True)

        embed = discord.Embed(
            title=title,
            description=f"{len(cards)} card(s) found",
            color=color
        )

        for card in cards[:25]:  # Limit to 25
            embed.add_field(
                name=f"{card.rarity_stars} {card.character_name or 'Unknown'}",
                value=f"{card.type_emoji} {card.type_name}",
                inline=True
            )

        if len(cards) > 25:
            embed.set_footer(text=f"Showing 25 of {len(cards)} cards")

        await ctx.send(embed=embed)

    @commands.command(name='ssrsupports')
    async def ssr_supports(self, ctx):
        """List all SSR support cards."""
        cards = self.manager.get_ssr_cards()

        if not cards:
            await ctx.send("❌ No SSR support cards found")
            return

        embed = discord.Embed(
            title="✨ SSR Support Cards",
            description=f"{len(cards)} SSR support cards",
            color=0xFFD700
        )

        # Group by type
        type_groups = {}
        for card in cards:
            type_name = card.type_name
            if type_name not in type_groups:
                type_groups[type_name] = []
            type_groups[type_name].append(card)

        for type_name, type_cards in sorted(type_groups.items()):
            if type_cards:
                emoji = type_cards[0].type_emoji
                card_names = [c.character_name or "Unknown" for c in type_cards[:10]]
                embed.add_field(
                    name=f"{emoji} {type_name} ({len(type_cards)})",
                    value="\n".join(card_names) or "None",
                    inline=True
                )

        await ctx.send(embed=embed)

    @commands.command(name='searchsupport', aliases=['findsupport'])
    async def search_support(self, ctx, *, query: str):
        """Search for support cards.

        Usage: !searchsupport <query>
        Example: !searchsupport vodka
        """
        results = self.manager.search(query)

        if not results:
            await ctx.send(f"❌ No support cards found matching '{query}'")
            return

        embed = discord.Embed(
            title=f"🔍 Support Card Search: '{query}'",
            description=f"Found {len(results)} card(s)",
            color=config.EMBED_COLOR
        )

        for card in results[:20]:
            embed.add_field(
                name=f"{card.rarity_stars} {card.character_name or 'Unknown'}",
                value=f"{card.type_emoji} {card.type_name}",
                inline=True
            )

        if len(results) > 20:
            embed.set_footer(text=f"Showing 20 of {len(results)} results")

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(SupportCards(bot))
