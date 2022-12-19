import discord
from discord.ext import commands
import asyncio
from asyncio import run_coroutine_threadsafe
from urllib import parse,request
import re
import json
import os
from youtube_dl import YoutubeDL

class MusicCog(commands.Cog):
    def __init__(self,bot):
        self.bot = bot
        #Allow the bot to play on multiple servers
        self.is_playing = {}
        self.is_paused = {}
        self.music_queue = {}
        self.queue_index = {}

        self.YTDL_OPTIONS = {
            'format': 'bestaudio',
            'noplaylist': 'True'
        }
        self.FFMPEG_OPTIONS = {
            'before_options': '-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5', 
            'options': '-vn'
        }

        self.EMBED_BLUE = 0x2c6dd
        self.EMBED_RED = 0xdf1141
        self.EMBED_GREEN = 0x0eaa51


        self.vc = {}

    @commands.Cog.listener()
    async def on_ready(self):
        #Make each server an id to a dictionary to distinguish them from one another
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.music_queue[id] = []
            self.queue_index[id] = 0
            self.vc[id] = None
            self.is_paused[id] = self.is_playing[id] = False
        print("Bot Online")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        bot= self.bot.user.id
        if member.id != bot and before.channel != None and after.channel != before.channel:
            remaining_channel_members = before.channel.members
            if len(remaining_channel_members) == 1 and remaining_channel_members[0].id == bot and self.vc[id].is_connected():
                await self.reset()
                await self.vc[id].disconnect()


    #Helper functions
    def nowPlaying(self,ctx,song):
        title = song['title']
        duration = song['duration']
        link = song['link']
        thumbnail = song['thumbnail']
        author = song[ctx.author]
        avatar = author.avatar_url

        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title} ({duration})]({link})',
            colour = self.EMBED_BLUE
        )
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by {str(author)}',icon_url=avatar)
        return embed

    async def joinVC(self,ctx,channel):
        id = int(ctx.guild.id)
        if self.vc[id] == None or not self.vc[id].is_connected():
            #if not connected to a channel already
            self.vc[id] = await channel.connect()
            if self.vc[id] == None:
                await ctx.send("Unable to connect to the voice channel")
                return
        else: 
            #if already connected to a channel
            await self.vc[id].move_to(channel)

    async def reset(self):
        self.is_playing[id] = self.is_paused[id] = False
        self.music_queue[id] = []
        self.queue_index[id] = 0

    def search_YT(self,search):
        query_string = parse.urlencode({'search_query': search})
        html_content = request.urlopen("http://www.youtube.com/results?" + query_string)
        search_results = re.findall('/watch\?v=(.{11})', html_content.read().decode())
        return search_results[0:10]

    def extract_YT(self,url):
        with YoutubeDL(self.YTDL_OPTIONS) as ydl:
            try:
                info = ydl.extract_info(url,download=False)
            except:
                return False
        return {
            'link': 'https://www.youtube.com/watch?v=' + url,
            'thumbnail': 'https://i.ytimg.com/vi/' + url + '/hqdefault.jpg?sqp=-oaymwEcCOADEI4CSFXyq4qpAw4IARUAAIhCGAFwAcABBg==&rs=AOn4CLD5uL4xKN-IUfez6KIW_j5y70mlig',
            'source': info['formats'][0]['url'],
            'title': info['title'],
            'duration': info['duration']
        }
    
    def playNext(self,ctx):
        id = int(ctx.guild.id)
        if not self.is_playing[id]:
            return
        if self.queue_index[id] + 1 < len(self.music_queue[id]):
            self.is_playing[id] = True
            self.queue_index[id] += 1

            song = self.music_queue[id][self.queue_index[id]][0]
            message = ctx.now_playing(ctx,song)
            coro = ctx.send(embed=message)
            fut = run_coroutine_threadsafe(coro,self.bot.loop)
            try:
                fut.result()
            except:
                pass
        
            self.vc[id].play(discord.FFmpeg(
                song['source'], **self.FFMPEG_OPTIONS),
                after=lambda e: self.playNext(ctx)
            )
        else:
            coro = ctx.send(message)
            fut = run_coroutine_threadsafe(coro,self.bot.loop)
            try:
                fut.result()
            except:
                pass
            self.queue_index[id] += 1
            self.is_playing[id] = False
        

    async def playMusic(self,ctx):
        id = int(ctx.guild.id)
        if self.queue_index[id] < len(self.music_queue[id]):
            self.is_playing[id] = True
            self.is_paused = False
            #I dont understand this part?
            await self.joinVC(ctx,self.music_queue[id][self.queue_index[id][1]])
            song = self.music_queue[id][self.queue_index[id]][0]

            message = ctx.now_playing(ctx,song)
            await ctx.send(embed=message)

            self.vc[id].play(discord.FFmpeg(
                song['source'], **self.FFMPEG_OPTIONS),
                after=lambda e: self.playNext(ctx)
            )
        else:
            await ctx.send("There are no songs in the queue ")
            self.queue_index[id] += 1
            self.is_playing[id] = False

    #Commands
    @commands.command(
        name="play",
        aliases=['p'],
        help=""
    )
    async def play(self,ctx,*args):
        search = " ".join(args)
        id = int(ctx.guild.id)
        try:
            user_channel = ctx.author.voice.channel
        except:
            await ctx.send("You must be connected to a voice channel")
        if not args:
            #No search terms put in
            if len(self.music_queue[id]) == 0:
                await ctx.send("There are no songs to be played in the queue")
                return
            elif not self.is_playing[id]:
                if self.music_queue[id] == None or self.vc[id] == None:
                    await self.playMusic(ctx)
                else:
                    self.is_paused[id] = False
                    self.is_playing[id] = True
                    self.vc[id].resume()
            else:
                return
        else: #




    @commands.command(
        name="join",
        aliases=['j'],
        help=""
    )
    async def join(self,ctx):
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            await self.joinVC(ctx,user_channel)
            await ctx.send(f'Realm Tunes joined {user_channel}')
        else:
            await ctx.send("You must be connected to a voice channel")

    @commands.command(
        name="leave",
        aliases=['l'],
        help=""
    )
    async def leave(self,ctx):
        id = int(ctx.guild.id)
        await self.reset()
        if self.vc[id] != None:
            await self.vc[id].disconnect()
            await ctx.send("Realm Tunes left the chat")




