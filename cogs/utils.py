from typing import Literal, Optional

from discord import app_commands
from discord.ext import commands
from discord.ext.commands import Context, Greedy  # or a subclass of yours


class Utils(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot

    @commands.command(
        name="sync",
    )
    @commands.is_owner()
    async def sync(self, ctx):
        print("syncing...")
        guild = ctx.guild
        try:
            # ctx.bot.tree.copy_global_to(guild=guild)
            synced = await ctx.bot.tree.sync()
            await ctx.send(f"Synced {len(synced)} command(s).")
        except Exception as e:
            print(f"sync error: {e}")
        print("synced!")

    @commands.command(
        name="ping",
    )
    @commands.is_owner()
    async def ping(self, ctx):
        await ctx.send(f"Pong! ({self.bot.latency*1000}ms)")
            
