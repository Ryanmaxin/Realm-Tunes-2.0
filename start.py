import discord
import os 
from dotenv import load_dotenv
import asyncio

from discord.ext import commands

load_dotenv()
password = str(os.getenv("bot_key"))

bot = commands.Bot(command_prefix = '-', intents = discord.Intents.all(), case_insensitive = True)

async def load_extensions():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            # cut off the .py from the file name
            await bot.load_extension(f"cogs.{filename[:-3]}")

@bot.event
async def on_ready():
    print("Bot is ready!")

async def main():
    async with bot:
        await load_extensions()
        await bot.start(password)

asyncio.run(main())