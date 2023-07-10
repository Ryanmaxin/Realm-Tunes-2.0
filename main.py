import discord
import os 
from dotenv import load_dotenv
import asyncio
import logging
import sys
import time
from cogs.help import Help
from cogs.music import Music
import wavelink

from discord.ext import commands

load_dotenv()
password = str(os.getenv("bot_key"))

server_pass = str(os.getenv("password"))
server_host = str(os.getenv("localhost"))


class Bot(commands.Bot):

    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.message_content = True
        case_insensitive = True
        activity = discord.Activity(type=discord.ActivityType.listening, name="-help")
        super().__init__(command_prefix='-', intents=intents,case_insensitive=case_insensitive,activity=activity)

    async def on_ready(self) -> None:
        print("Realm Tunes Online")

    async def setup_hook(self) -> None:
        node: wavelink.Node = wavelink.Node(uri="http://localhost:2333", password="youshallnotpass")
        await wavelink.NodePool.connect(client=self, nodes=[node])

    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

async def main():
    bot = Bot()
    print("Bot Initialized")
    bot.remove_command('help')
    async with bot:
        await bot.add_cog(Music(bot))
        print("Initialized Music Cog")
        await bot.add_cog(Help(bot))
        print("Initialized Help Cog")
        await bot.start(password)

if __name__ == "__main__":
    # time.sleep(20)
    asyncio.run(main())
