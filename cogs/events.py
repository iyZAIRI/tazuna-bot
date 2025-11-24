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
            # Get mission groups for this event
            groups = self.event_manager.get_event_mission_groups(event['event_id'])
            view = EventDetailView(event, groups, self, self.event_manager)
            embed = view.create_embed()
            await interaction.response.edit_message(embed=embed, view=view)

        return callback

    def create_embed(self) -> discord.Embed:
        """Create the event list embed."""
        embed = discord.Embed(
            title="📅 Active Mission Events",
            description="Currently active time-limited missions. Select an event to view mission groups:",
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
        else:
            embed.description = "No active mission events at this time."

        embed.set_footer(text="Uma Musume Pretty Derby • Select an event below")
        return embed


class EventDetailView(discord.ui.View):
    """View for displaying event details with mission group buttons."""

    def __init__(self, event: dict, groups: List[dict], parent_list: EventListView,
                 event_manager: EventManager):
        super().__init__(timeout=180)
        self.event = event
        self.groups = groups
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
        for idx, group in enumerate(groups[:20]):  # Limit to 20 groups
            button = discord.ui.Button(
                label=f"{group['name']} ({group['mission_count']})",
                style=discord.ButtonStyle.primary,
                custom_id=f"group_{group['step_group_id']}",
                row=(idx // 5) + 1
            )
            button.callback = self.create_group_callback(group)
            self.add_item(button)

    def create_group_callback(self, group):
        """Create a callback for a specific mission group button."""
        async def callback(interaction: discord.Interaction):
            # Get missions for this group
            missions = self.event_manager.get_missions_by_group(
                self.event['event_id'], group['step_group_id']
            )
            view = MissionGroupView(
                self.event, group, missions, self, self.event_manager
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
            description="Select a mission group to view missions:",
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
        total_missions = sum(g['mission_count'] for g in self.groups)
        embed.add_field(
            name="Mission Groups",
            value=f"{len(self.groups)} groups | {total_missions} total missions",
            inline=True
        )

        # List mission groups
        if self.groups:
            groups_text = []
            for group in self.groups[:10]:  # Show first 10
                groups_text.append(f"**{group['name']}**: {group['mission_count']} missions")

            if len(self.groups) > 10:
                groups_text.append(f"... and {len(self.groups) - 10} more groups")

            embed.add_field(
                name="Available Groups",
                value="\n".join(groups_text),
                inline=False
            )

        embed.set_footer(text="Select a mission group below")
        return embed


class MissionGroupView(discord.ui.View):
    """View for displaying missions in a mission group."""

    def __init__(self, event: dict, group: dict, missions: List[dict],
                 parent_detail: EventDetailView, event_manager: EventManager):
        super().__init__(timeout=180)
        self.event = event
        self.group = group
        self.missions = missions
        self.parent_detail = parent_detail
        self.event_manager = event_manager

        # Add back button
        back_button = discord.ui.Button(
            label="⬅ Back to Groups",
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
            title=f"📋 {self.event['name']}",
            description=f"**{self.group['name']}**",
            color=config.EMBED_COLOR
        )

        # Group missions
        mission_text = []
        for idx, mission in enumerate(self.missions[:25], 1):  # Limit to 25 to avoid embed size issues
            # Format reward
            reward = f"Item {mission['reward_item_id']} x{mission['reward_amount']}"

            mission_text.append(f"{idx}. {mission['description']}\n   → {reward}")

        if mission_text:
            # Split into chunks if needed (Discord field value limit is 1024 chars)
            current_chunk = []
            current_length = 0
            field_num = 1

            for line in mission_text:
                line_length = len(line) + 2  # +2 for newlines
                if current_length + line_length > 1000:  # Leave some margin
                    # Add current chunk as field
                    embed.add_field(
                        name=f"Missions (Part {field_num})" if field_num > 1 else "Missions",
                        value="\n\n".join(current_chunk),
                        inline=False
                    )
                    current_chunk = [line]
                    current_length = line_length
                    field_num += 1
                else:
                    current_chunk.append(line)
                    current_length += line_length

            # Add remaining chunk
            if current_chunk:
                embed.add_field(
                    name=f"Missions (Part {field_num})" if field_num > 1 else "Missions",
                    value="\n\n".join(current_chunk),
                    inline=False
                )

        if len(self.missions) > 25:
            embed.set_footer(text=f"Showing 25 of {len(self.missions)} missions")
        else:
            embed.set_footer(text=f"{len(self.missions)} missions")

        return embed


class Events(commands.Cog):
    """Commands for viewing time-limited mission events."""

    def __init__(self, bot: commands.Bot):
        self.bot = bot
        self.manager = EventManager()

    @app_commands.command(name="events", description="View currently active time-limited mission events")
    async def events(self, interaction: discord.Interaction):
        """List all currently active mission events."""
        await interaction.response.defer()

        events = self.manager.get_active_events()

        if not events:
            await interaction.followup.send("No active mission events at this time.")
            return

        view = EventListView(events, self.manager)
        embed = view.create_embed()
        await interaction.followup.send(embed=embed, view=view)


async def setup(bot: commands.Bot):
    await bot.add_cog(Events(bot))
