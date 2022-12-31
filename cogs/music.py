import discord
import wavelink
from discord.ext import commands
import os
import sys
import typing

class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())

        self.node = None
        self.join_context = {}

        self.EMBED_BLUE = 0x2c6dd
        self.EMBED_RED = 0xdf1141
        self.EMBED_GREEN = 0x0eaa51


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
    async def on_ready(self):
        print("Bot Online")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player = self.node.get_player(member.guild)
        if not member.bot and before.channel != None and after.channel != before.channel:
            remaining_channel_members = before.channel.members
            if len(remaining_channel_members) == 1 and remaining_channel_members[0].bot and player.is_connected():
                await player.disconnect()
                join_context = self.join_context[id]
                await join_context.channel.send(f"Realm Tunes left because there were no members remaining in ``{before.channel}``")


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')
        self.node = wavelink.NodePool.get_node()

    #Helper functions
    async def cog_command_error(self, ctx, error):
        print(error)
    
    async def cog_check(self,ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Sorry, music commands are not available in DMs. Please join a voice channel in a server containing Realm Tunes to use music commands!")
            return False
        return True

    async def sendDM(self,func,vars: dict):
        user = await self.bot.fetch_user(404491098946273280)
        message = f"Error in: {func}"
        await user.send(f"Error in: {func}")
        for var in vars:
            message += f"\n{var}: {vars[var]}"
        await user.send(message)
    

    async def create_nodes(self):
        """Connect to our Lavalink nodes."""
        
        await self.bot.wait_until_ready()
        await wavelink.NodePool.create_node(bot=self.bot,
                                            host='127.0.0.1',
                                            port=2333,
                                            password='youshallnotpass',
                                            region='US CENTRAL')
    
    async def joinVC(self,ctx, channel):
        result = None
        player = self.node.get_player(ctx.guild)
        if player is not None and player.is_connected():
            await player.move_to(channel)
        else:
            result = await channel.connect(cls=wavelink.Player)
            if result == None:
                return result
        self.join_context[id] = ctx
        result = True
        return result


    @commands.command(
        name="join",
        aliases=['j'],
        help=""
    )
    async def join_command(self, ctx: commands.Context):
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                await ctx.send("Unable to connect to the voice channel")
            else:
                await ctx.send(f'Realm Tunes joined ``{user_channel}``')
        else:
            await ctx.send("You must be connected to a voice channel")

    @commands.command(
        name="leave",
        aliases=['l'],
        help=""
    )
    async def leave_command(self, ctx: commands.Context):
        player = self.node.get_player(ctx.guild)

        if player is None:
            await ctx.send("Realm Tunes is not connected to any voice channel")
            return
        await player.disconnect()
        await ctx.send("Realm Tunes left the chat")
    
    @commands.command(
        name="play",
        aliases=['p'],
        help=""
    )
    async def play_command(self, ctx: commands.Context, *, query: str=""):
        if len(query) == 0:
            await ctx.send("Please enter a search term")
            return
        search = await wavelink.YouTubeTrack.search(query=query, return_first=True)
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                await ctx.send("Unable to connect to the voice channel to play music")
                return
        else:
            await ctx.send("You must be connected to a voice channel to play music")
            return
        
        player = player = self.node.get_player(ctx.guild)
        await player.play(search)

        mbed = discord.Embed(title=f"Now Playing {search}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)
    
    @commands.command(
        name="soundcloud_play",
        aliases=['scp'],
        help=""
    )
    async def soundcloud_play_command(self, ctx: commands.Context, *, query: str=""):
        if len(query) == 0:
            await ctx.send("Please enter a search term")
            return
        search = await wavelink.SoundCloudTrack.search(query=query, return_first=True)
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                await ctx.send("Unable to connect to the voice channel to play music")
                return
        else:
            await ctx.send("You must be connected to a voice channel to play music")
            return
        
        player = player = self.node.get_player(ctx.guild)
        await player.play(search)

        mbed = discord.Embed(title=f"Now Playing {search}", color=discord.Color.from_rgb(255, 255, 255))
        await ctx.send(embed=mbed)
    
    @commands.command(name="stop")
    async def stop_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("Bot is not connected to any voice channel")
        
        if player.is_playing:
            await player.stop()
            mbed = discord.Embed(title="Playback Stoped", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("Nothing Is playing right now")
    
    @commands.command(name="pause")
    async def pause_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("Bot is not connected to any voice channel")
        
        if not player.is_paused():
            if player.is_playing():
                await player.pause()
                mbed = discord.Embed(title="Playback Paused", color=discord.Color.from_rgb(255, 255, 255))
                return await ctx.send(embed=mbed)
            else:
                return await ctx.send("Nothing is playing right now")
        else:
            return await ctx.send("Playback is Already paused")
    
    @commands.command(name="resume")
    async def resume_command(self, ctx: commands.Context):
        node = wavelink.NodePool.get_node()
        player = node.get_player(ctx.guild)

        if player is None:
            return await ctx.send("bot is not connnected to any voice channel")
        
        if player.is_paused():
            await player.resume()
            mbed = discord.Embed(title="Playback resumed", color=discord.Color.from_rgb(255, 255, 255))
            return await ctx.send(embed=mbed)
        else:
            return await ctx.send("playback is not paused")

    @commands.command(
        name="volume",
        aliases=['v'],
        help=""
    )
    async def volume_command(self, ctx: commands.Context, to=None):
        
        
        try:
            to = int(to)
        except:
            await ctx.send("Volume must be a whole number between 0 and 1000 (ex: 50)")
            return 
        if to > 1000:
            await ctx.send("Volume must be between 0 and 1000")
            return
        elif to < 1:
            await ctx.send("Volume must be between 0 and 1000")
            return
        elif to > 100:
            embed = discord.Embed(title=f"Warning: setting volume over 100% is not recommended. Please be careful!", color=self.EMBED_RED)
            await ctx.send(embed=embed)

        player = self.node.get_player(ctx.guild)
        await player.set_volume(to)
        await ctx.send(f"Set volume to {to}%")
    
async def setup(bot):
    await bot.add_cog(Music(bot))
    print("Loaded music cog")
