import discord
from discord.ext import commands
import os
from dotenv import load_dotenv
from music_cog import MusicCog
import asyncio
import datetime
import traceback


load_dotenv()
# os.system('clear')

intents = discord.Intents.all()
bot = commands.Bot(command_prefix = '-', intents = intents, case_insensitive = True)
password = str(os.getenv("bot_key"))

@bot.event
async def on_error(event, *args, **kwargs):
    embed = discord.Embed(title=':x: Event Error', colour=0xe74c3c) #Red
    embed.add_field(name='Event', value=event)
    embed.description = '```py\n%s\n```' % traceback.format_exc()
    embed.timestamp = datetime.datetime.utcnow()
    await bot.AppInfo.owner.send(embed=embed)

async def main():
    await bot.add_cog(MusicCog(bot))
    await bot.start(password)

asyncio.run(main())