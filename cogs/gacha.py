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
    """View for displaying list of active gacha banners with navigation."""

    def __init__(self, gachas: List[dict], gacha_manager: GachaManager, current_index: int = 0):
        super().__init__(timeout=180)
        self.gachas = gachas
        self.gacha_manager = gacha_manager
        self.current_index = current_index

        # Add navigation buttons
        self._add_buttons()

    def _add_buttons(self):
        """Add navigation buttons."""
        if len(self.gachas) <= 1:
            return

        # Previous button
        prev_button = discord.ui.Button(
            label="◀ Previous",
            style=discord.ButtonStyle.primary,
            disabled=(self.current_index == 0)
        )
        prev_button.callback = self.previous_banner
        self.add_item(prev_button)

        # Next button
        next_button = discord.ui.Button(
            label="Next ▶",
            style=discord.ButtonStyle.primary,
            disabled=(self.current_index >= len(self.gachas) - 1)
        )
        next_button.callback = self.next_banner
        self.add_item(next_button)

    async def previous_banner(self, interaction: discord.Interaction):
        """Go to previous banner."""
        self.current_index = max(0, self.current_index - 1)
        view = GachaListView(self.gachas, self.gacha_manager, self.current_index)
        embed = view.create_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    async def next_banner(self, interaction: discord.Interaction):
        """Go to next banner."""
        self.current_index = min(len(self.gachas) - 1, self.current_index + 1)
        view = GachaListView(self.gachas, self.gacha_manager, self.current_index)
        embed = view.create_embed()
        await interaction.response.edit_message(embed=embed, view=view)

    def create_embed(self) -> discord.Embed:
        """Create embed for current gacha banner."""
        gacha = self.gachas[self.current_index]

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

        # Create embed for this banner
        embed = discord.Embed(
            title=f"{banner_type} (ID: {gacha['id']})",
            color=config.EMBED_COLOR
        )

        # Format dates
        start_dt = datetime.datetime.fromtimestamp(gacha['start_date'])
        end_dt = datetime.datetime.fromtimestamp(gacha['end_date'])
        date_str = f"{start_dt.strftime('%Y-%m-%d %H:%M')} - {end_dt.strftime('%Y-%m-%d %H:%M')}"

        # Add period and cost
        embed.add_field(name="Period", value=date_str, inline=False)
        embed.add_field(name="Cost", value=f"{gacha['cost']} gems per pull", inline=False)

        # Format pickup cards
        pickup_text = []
        for pickup in gacha['pickups'][:5]:  # Limit to 5 pickups
            rarity_emoji = get_rarity_emoji(pickup['rarity'])

            if pickup['type'] == 'support':
                type_emoji = get_support_card_type_emoji(pickup['command_id'])
                pickup_text.append(f"{rarity_emoji} {type_emoji} {pickup['name']}")
            else:  # character
                pickup_text.append(f"{rarity_emoji} {pickup['name']}")

        if pickup_text:
            embed.add_field(name="Featured Cards", value="\n".join(pickup_text), inline=False)
        else:
            embed.add_field(name="Featured Cards", value="No featured pickups", inline=False)

        # Add banner image
        banner_url = f"https://gametora.com/images/umamusume/en/gacha/img_bnr_gacha_{gacha['id']}.png"
        embed.set_image(url=banner_url)

        # Footer with banner counter
        if len(self.gachas) > 1:
            embed.set_footer(text=f"Banner {self.current_index + 1}/{len(self.gachas)} • Uma Musume Pretty Derby")
        else:
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
