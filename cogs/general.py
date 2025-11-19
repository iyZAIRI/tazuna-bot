"""General commands for the bot."""
import discord
from discord.ext import commands
import config
import time

class General(commands.Cog):
    """General bot commands."""

    def __init__(self, bot):
        self.bot = bot

    @commands.command(name='ping')
    async def ping(self, ctx):
        """Check bot latency."""
        start_time = time.time()
        message = await ctx.send("🏇 Pinging...")
        end_time = time.time()

        embed = discord.Embed(
            title="🏁 Pong!",
            color=config.EMBED_COLOR
        )
        embed.add_field(
            name="Bot Latency",
            value=f"{round(self.bot.latency * 1000)}ms",
            inline=True
        )
        embed.add_field(
            name="Response Time",
            value=f"{round((end_time - start_time) * 1000)}ms",
            inline=True
        )
        await message.edit(content=None, embed=embed)

    @commands.command(name='info', aliases=['about'])
    async def info(self, ctx):
        """Display bot information."""
        embed = discord.Embed(
            title="🏇 Uma Musume Bot Information",
            description=config.BOT_DESCRIPTION,
            color=config.EMBED_COLOR
        )
        embed.add_field(name="Version", value=config.BOT_VERSION, inline=True)
        embed.add_field(name="Prefix", value=config.COMMAND_PREFIX, inline=True)
        embed.add_field(name="Servers", value=len(self.bot.guilds), inline=True)
        embed.add_field(
            name="Library",
            value=f"discord.py {discord.__version__}",
            inline=True
        )
        embed.set_footer(text="Uma Musume Pretty Derby Discord Bot")
        await ctx.send(embed=embed)

    @commands.command(name='invite')
    async def invite(self, ctx):
        """Get bot invite link."""
        if self.bot.user:
            invite_url = discord.utils.oauth_url(
                self.bot.user.id,
                permissions=discord.Permissions(
                    read_messages=True,
                    send_messages=True,
                    embed_links=True,
                    attach_files=True,
                    read_message_history=True,
                    add_reactions=True
                )
            )
            embed = discord.Embed(
                title="📨 Invite Me!",
                description=f"[Click here to invite me to your server!]({invite_url})",
                color=config.EMBED_COLOR
            )
            await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(General(bot))
