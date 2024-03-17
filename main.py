import asyncio
import logging
import os
import sys
import time

import discord
import wavelink
from discord.ext import commands
from dotenv import load_dotenv

from cogs.exceptions import ExceptionHandler
from cogs.help import Help
from cogs.music import Music
from cogs.utils import Utils

load_dotenv()
password = str(os.getenv("BOT_KEY"))

server_pass = str(os.getenv("SERVER_KEY"))
server_host = str(os.getenv("SERVER_HOST"))


class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        case_insensitive = True
        activity = discord.Activity(type=discord.ActivityType.listening, name="/help")
        discord.utils.setup_logging(level=logging.INFO)
        super().__init__(command_prefix='-', intents=intents,case_insensitive=case_insensitive,activity=activity)

    async def on_ready(self) -> None:
        print("Realm Tunes Online")

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(uri=server_host, password=server_pass)
        await wavelink.Pool.connect(client=self, nodes=[node])

    async def on_wavelink_node_ready(self, payload: wavelink.NodeReadyEventPayload):
        """Event fired when a node has finished connecting."""
        print(f'Node {payload.node}is ready!')

async def main():
    bot = Bot()
    print("Bot Initialized")
    bot.remove_command('help')
    async with bot:
        await bot.add_cog(Music(bot))
        print("Initialized Music Cog")
        await bot.add_cog(Help(bot))
        print("Initialized Help Cog")
        await bot.add_cog(Utils(bot))
        print("Initialized Utils Cog")
        await bot.add_cog(ExceptionHandler(bot))
        print("Initialized ExceptionHandler Cog")
        await bot.start(password)

if __name__ == "__main__":
    time.sleep(5)
    asyncio.run(main())
