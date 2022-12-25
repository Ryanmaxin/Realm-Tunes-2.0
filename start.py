import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from music_cog import MusicCog
import logging
import sys, os, asyncio


load_dotenv()
# os.system('clear')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '-', intents = intents, case_insensitive = True)
password = str(os.getenv("bot_key"))

logging.basicConfig(stream=sys.stdout, level=logging.CRITICAL)

async def main():
    await bot.add_cog(MusicCog(bot))
    await bot.start(password, reconnect=True)

if __name__ == "__main__":
    asyncio.run(main())