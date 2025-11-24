"""Event commands and views."""
import discord
from discord import app_commands
from discord.ext import commands
import sys
from pathlib import Path
from typing import List, Optional
import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))

from managers.event_manager import EventManager
import config


class EventListView(discord.ui.View):
    """View for displaying list of events with buttons."""

    def __init__(self, events: List[dict], event_manager: EventManager):
        super().__init__(timeout=180)
        self.events = events
        self.event_manager = event_manager

        # Create buttons for each event (limit to 25 - Discord limit)
        for idx, event in enumerate(events[:25]):
            button = discord.ui.Button(
                label=event['name'],
                style=discord.ButtonStyle.primary,
                custom_id=f"event_{event['event_id']}",
                row=idx // 5
            )
            button.callback = self.create_event_callback(event)
            self.add_item(button)

    def create_event_callback(self, event):
        """Create a callback for a specific event button."""
        async def callback(interaction: discord.Interaction):
            # Get event details and show mission groups
            event_detail = self.event_manager.get_event_details(event['event_id'])
            if event_detail:
                view = EventDetailView(event_detail, self, self.event_manager)
                embed = view.create_embed()
                await interaction.response.edit_message(embed=embed, view=view)

        return callback

    def create_embed(self) -> discord.Embed:
        """Create the event list embed."""
        embed = discord.Embed(
            title="📅 Time-Limited Mission Events",
            description="Select an event to view details and missions:",
            color=config.EMBED_COLOR
        )

        events_text = []
        for event in self.events:
            start_dt = datetime.datetime.fromtimestamp(event['start_date'])
            end_dt = datetime.datetime.fromtimestamp(event['end_date'])
            date_str = f"{start_dt.strftime('%Y-%m-%d')} to {end_dt.strftime('%Y-%m-%d')}"
            events_text.append(f"**{event['name']}**\n  {date_str}")

        if events_text:
            embed.add_field(
                name="Available Events",
                value="\n\n".join(events_text),
                inline=False
            )

        embed.set_footer(text="Uma Musume Pretty Derby • Select an event below")
        return embed


class EventDetailView(discord.ui.View):
    """View for displaying event details with mission group buttons."""

    def __init__(self, event: dict, parent_list: EventListView, event_manager: EventManager):
        super().__init__(timeout=180)
        self.event = event
        self.parent_list = parent_list
        self.event_manager = event_manager

        # Add back button
        back_button = discord.ui.Button(
            label="⬅ Back to Events",
            style=discord.ButtonStyle.secondary,
            row=0
        )
        back_button.callback = self.go_back
        self.add_item(back_button)

        # Create buttons for each mission group
        for idx, group_id in enumerate(event['mission_groups'][:20], 1):
            # Try to get group name from text_data
            group_name = self.get_mission_group_name(event['event_id'], group_id)

            button = discord.ui.Button(
                label=group_name,
                style=discord.ButtonStyle.primary,
                custom_id=f"group_{group_id}",
                row=(idx // 5) + 1
            )
            button.callback = self.create_group_callback(group_id, group_name)
            self.add_item(button)

    def get_mission_group_name(self, event_id: int, group_id: int) -> str:
        """Get a readable name for the mission group."""
        # For Half Anniversary, groups might map to Part 1, 2, 3
        if event_id == 1001:  # Half Anniversary
            if group_id <= 5:
                return f"Part 1 - Group {group_id}"
            elif group_id <= 15:
                return f"Part 2 - Group {group_id}"
            else:
                return f"Part 3 - Group {group_id}"
        else:
            return f"Mission Group {group_id}"

    def create_group_callback(self, group_id: int, group_name: str):
        """Create a callback for a specific mission group button."""
        async def callback(interaction: discord.Interaction):
            # Get missions for this group
            missions = self.event_manager.get_mission_group_missions(
                self.event['event_id'], group_id
            )
            view = MissionGroupView(
                self.event, group_id, group_name, missions, self, self.event_manager
            )
            embed = view.create_embed()
            await interaction.response.edit_message(embed=embed, view=view)

        return callback

    async def go_back(self, interaction: discord.Interaction):
        """Go back to event list."""
        embed = self.parent_list.create_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_list)

    def create_embed(self) -> discord.Embed:
        """Create the event detail embed."""
        event = self.event
        embed = discord.Embed(
            title=f"📅 {event['name']}",
            description="Select a mission group to view details:",
            color=config.EMBED_COLOR
        )

        # Event dates
        start_dt = datetime.datetime.fromtimestamp(event['start_date'])
        end_dt = datetime.datetime.fromtimestamp(event['end_date'])
        embed.add_field(
            name="Event Period",
            value=f"{start_dt.strftime('%Y-%m-%d %H:%M')} to\n{end_dt.strftime('%Y-%m-%d %H:%M')}",
            inline=False
        )

        # Mission groups count
        embed.add_field(
            name="Mission Groups",
            value=f"{len(event['mission_groups'])} groups available",
            inline=True
        )

        # Bonus support cards (show top 5)
        if event['bonus_cards']:
            bonus_text = []
            for card in event['bonus_cards'][:5]:
                rarity_str = '★' * card['rarity']
                bonus_text.append(
                    f"{card['name']} ({rarity_str}): +{card['bonus_min']}% to +{card['bonus_max']}%"
                )

            if len(event['bonus_cards']) > 5:
                bonus_text.append(f"... and {len(event['bonus_cards']) - 5} more")

            embed.add_field(
                name="Bonus Support Cards",
                value="\n".join(bonus_text),
                inline=False
            )

        embed.set_footer(text="Select a mission group below")
        return embed


class MissionGroupView(discord.ui.View):
    """View for displaying missions in a mission group."""

    def __init__(self, event: dict, group_id: int, group_name: str,
                 missions: List[dict], parent_detail: EventDetailView,
                 event_manager: EventManager):
        super().__init__(timeout=180)
        self.event = event
        self.group_id = group_id
        self.group_name = group_name
        self.missions = missions
        self.parent_detail = parent_detail
        self.event_manager = event_manager

        # Add back button
        back_button = discord.ui.Button(
            label="⬅ Back to Event",
            style=discord.ButtonStyle.secondary
        )
        back_button.callback = self.go_back
        self.add_item(back_button)

    async def go_back(self, interaction: discord.Interaction):
        """Go back to event detail."""
        embed = self.parent_detail.create_embed()
        await interaction.response.edit_message(embed=embed, view=self.parent_detail)

    def create_embed(self) -> discord.Embed:
        """Create the mission group embed."""
        embed = discord.Embed(
            title=f"📋 {self.event['name']} - {self.group_name}",
            description=f"Mission Group {self.group_id}",
            color=config.EMBED_COLOR
        )

        # Group missions by step order
        mission_text = []
        for mission in self.missions[:20]:  # Limit to avoid embed size issues
            # Format mission info
            desc = mission['description'] if mission['description'] else f"Mission {mission['mission_id']}"

            # Add condition number if relevant
            if mission['condition_num'] > 1:
                desc += f" (x{mission['condition_num']})"

            # Format reward
            reward = f"Reward: Item {mission['reward_item_id']} x{mission['reward_amount']}"

            mission_text.append(f"**{desc}**\n  {reward}")

        if mission_text:
            # Split into chunks if too long
            chunk_size = 10
            for i in range(0, len(mission_text), chunk_size):
                chunk = mission_text[i:i + chunk_size]
                field_name = f"Missions {i+1}-{min(i+chunk_size, len(mission_text))}" if len(mission_text) > chunk_size else "Missions"
                embed.add_field(
                    name=field_name,
                    value="\n\n".join(chunk),
                    inline=False
                )

        if len(self.missions) > 20:
            embed.set_footer(text=f"Showing 20 of {len(self.missions)} missions")
        else:
            embed.set_footer(text=f"{len(self.missions)} missions")

        return embed


class Events(commands.Cog):
    """Commands for viewing time-limited mission events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = EventManager()

    @app_commands.command(name="events", description="View time-limited mission events")
    async def events(self, interaction: discord.Interaction):
        """List all available mission events."""
        await interaction.response.defer()

        events = self.manager.get_all_events()

        if not events:
            await interaction.followup.send("No events found in the database.")
            return

        view = EventListView(events, self.manager)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
