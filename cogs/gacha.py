"""Gacha commands and views."""
import discord
from discord import app_commands
from discord.ext import commands
import sys
from pathlib import Path
from typing import List
import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.gacha_manager import GachaManager
from constants import get_rarity_emoji, get_support_card_type_emoji
import config


class GachaListView(discord.ui.View):
    """View for displaying list of active gacha banners."""

    def __init__(self, gachas: List[dict], gacha_manager: GachaManager):
        super().__init__(timeout=180)
        self.gachas = gachas
        self.gacha_manager = gacha_manager

    def create_embed(self) -> discord.Embed:
        """Create the gacha list embed."""
        embed = discord.Embed(
            title="🎰 Active Gacha Banners",
            description="Currently available gacha banners:",
            color=config.EMBED_COLOR
        )

        for gacha in self.gachas:
            # Determine banner type
            if gacha['card_type'] == 1:
                banner_type = "⭐ Character Banner"
            elif gacha['card_type'] == 2:
                banner_type = "🎴 Support Card Banner"
            else:
                banner_type = f"Banner Type {gacha['card_type']}"

            # Add "One Time Only" if applicable
            if gacha.get('only_once', False):
                banner_type = f"{banner_type} (One Time Only)"

            # Format dates
            start_dt = datetime.datetime.fromtimestamp(gacha['start_date'])
            end_dt = datetime.datetime.fromtimestamp(gacha['end_date'])
            date_str = f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%Y-%m-%d %H:%M')}"

            # Format pickup cards
            pickup_text = []
            for pickup in gacha['pickups'][:5]:  # Limit to 5 pickups
                rarity_emoji = get_rarity_emoji(pickup['rarity'])

                if pickup['type'] == 'support':
                    type_emoji = get_support_card_type_emoji(pickup['command_id'])
                    pickup_text.append(f"{rarity_emoji} {type_emoji} {pickup['name']}")
                else:  # character
                    pickup_text.append(f"{rarity_emoji} {pickup['name']}")

            if not pickup_text:
                pickup_text.append("No featured pickups")

            field_value = f"**Period:** {date_str}\n**Cost:** {gacha['cost']} gems\n\n**Featured:**\n" + "\n".join(pickup_text)

            embed.add_field(
                name=f"{banner_type} (ID: {gacha['id']})",
                value=field_value,
                inline=False
            )

        embed.set_footer(text="Uma Musume Pretty Derby")
        return embed


class Gacha(commands.Cog):
    """Commands for viewing gacha banners."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = GachaManager()

    @app_commands.command(name="gacha", description="View currently active gacha banners")
    async def gacha(self, interaction: discord.Interaction):
        """List all currently active gacha banners."""
        await interaction.response.defer()

        gachas = self.manager.get_active_gacha_banners()

        if not gachas:
            await interaction.followup.send("No active gacha banners at this time.")
            return

        view = GachaListView(gachas, self.manager)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Gacha(bot))
