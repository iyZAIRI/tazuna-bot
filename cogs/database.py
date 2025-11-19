"""Database-powered commands for Uma Musume bot."""
import discord
from discord.ext import commands
import config
import sys
from pathlib import Path

# Add utils to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.db_reader import MasterDBReader

class Database(commands.Cog):
    """Database exploration and information commands."""

    def __init__(self, bot):
        self.bot = bot
        self.db = MasterDBReader()
        self.connected = False

        # Try to connect to database
        if self.db.connect():
            self.connected = True
            print("✅ Connected to master.mdb database")
        else:
            print("⚠️  master.mdb not found - database commands will be limited")
            print("   Run: python utils/download_masterdb.py")

    def cog_unload(self):
        """Clean up database connection when cog is unloaded."""
        if self.connected:
            self.db.close()

    @commands.command(name='dbstatus', aliases=['dbinfo'])
    async def db_status(self, ctx):
        """Check database connection status."""
        embed = discord.Embed(
            title="🗄️ Database Status",
            color=config.EMBED_COLOR if self.connected else config.ERROR_COLOR
        )

        if self.connected:
            tables = self.db.get_tables()
            embed.description = "✅ Connected to master.mdb"
            embed.add_field(name="Tables", value=len(tables), inline=True)

            # Get some stats
            total_rows = 0
            for table in tables[:10]:  # Count first 10 tables as sample
                result = self.db.query(f"SELECT COUNT(*) as count FROM {table}")
                if result:
                    total_rows += result[0]['count']

            embed.add_field(name="Sample Row Count", value=f"~{total_rows:,}", inline=True)
        else:
            embed.description = "❌ Not connected to database"
            embed.add_field(
                name="How to fix",
                value="Run: `python utils/download_masterdb.py`",
                inline=False
            )

        await ctx.send(embed=embed)

    @commands.command(name='dbtables', aliases=['tables'])
    async def db_tables(self, ctx, search: str = None):
        """List database tables, optionally filtered by search term."""
        if not self.connected:
            await ctx.send("❌ Database not connected. Run `!dbstatus` for info.")
            return

        tables = self.db.get_tables()

        # Filter tables if search term provided
        if search:
            tables = [t for t in tables if search.lower() in t.lower()]

        if not tables:
            await ctx.send(f"❌ No tables found matching '{search}'")
            return

        # Paginate results
        per_page = 20
        total_pages = (len(tables) + per_page - 1) // per_page

        # Show first page
        page_tables = tables[:per_page]

        embed = discord.Embed(
            title="🗄️ Database Tables",
            description=f"Found {len(tables)} table(s)" + (f" matching '{search}'" if search else ""),
            color=config.EMBED_COLOR
        )

        table_list = []
        for table in page_tables:
            result = self.db.query(f"SELECT COUNT(*) as count FROM {table}")
            count = result[0]['count'] if result else 0
            table_list.append(f"`{table}` ({count:,} rows)")

        embed.add_field(
            name=f"Tables (Page 1/{total_pages})",
            value="\n".join(table_list) or "None",
            inline=False
        )

        if total_pages > 1:
            embed.set_footer(text=f"Showing {len(page_tables)} of {len(tables)} tables")

        await ctx.send(embed=embed)

    @commands.command(name='dbquery', aliases=['query'])
    @commands.is_owner()  # Restrict to bot owner for security
    async def db_query(self, ctx, *, sql: str):
        """
        Execute a SQL query (Bot owner only).

        Example: !dbquery SELECT * FROM table_name LIMIT 5
        """
        if not self.connected:
            await ctx.send("❌ Database not connected. Run `!dbstatus` for info.")
            return

        # Security check - only allow SELECT queries
        if not sql.strip().upper().startswith('SELECT'):
            await ctx.send("❌ Only SELECT queries are allowed for security reasons.")
            return

        try:
            results = self.db.query(sql)

            if not results:
                await ctx.send("✅ Query executed successfully (0 results)")
                return

            # Format results
            embed = discord.Embed(
                title="📊 Query Results",
                description=f"Found {len(results)} row(s)",
                color=config.EMBED_COLOR
            )

            # Show first few results
            import json
            result_text = json.dumps(results[:3], indent=2, ensure_ascii=False)

            # Truncate if too long
            if len(result_text) > 1900:
                result_text = result_text[:1900] + "..."

            embed.add_field(
                name="Results (first 3 rows)",
                value=f"```json\n{result_text}\n```",
                inline=False
            )

            if len(results) > 3:
                embed.set_footer(text=f"Showing 3 of {len(results)} results")

            await ctx.send(embed=embed)

        except Exception as e:
            await ctx.send(f"❌ Query failed: {str(e)}")

    @commands.command(name='dbschema')
    async def db_schema(self, ctx, table_name: str):
        """Show the schema (columns) of a database table."""
        if not self.connected:
            await ctx.send("❌ Database not connected. Run `!dbstatus` for info.")
            return

        schema = self.db.get_table_schema(table_name)

        if not schema:
            await ctx.send(f"❌ Table '{table_name}' not found or has no schema.")
            return

        embed = discord.Embed(
            title=f"📋 Schema: {table_name}",
            description=f"{len(schema)} column(s)",
            color=config.EMBED_COLOR
        )

        # Format schema info
        columns = []
        for col in schema:
            pk = " 🔑" if col['pk'] else ""
            null = "" if col['notnull'] else " (nullable)"
            columns.append(f"`{col['name']}` - {col['type']}{pk}{null}")

        # Split into multiple fields if too many columns
        chunk_size = 10
        for i in range(0, len(columns), chunk_size):
            chunk = columns[i:i+chunk_size]
            embed.add_field(
                name=f"Columns {i+1}-{min(i+chunk_size, len(columns))}",
                value="\n".join(chunk),
                inline=False
            )

        await ctx.send(embed=embed)

async def setup(bot):
    """Setup function for cog."""
    await bot.add_cog(Database(bot))
