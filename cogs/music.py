import discord
import wavelink
from discord.ext import commands
import os
import sys
import math

class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())

        self.join_context = {}

        self.play_mode = {}
        self.search_mode = {}
        self.VALID_PLAY_MODE = ['youtube','spotify','soundcloud']
        self.VALID_SEARCH_MODE = ['single','list']

        self.EMBED_BLUE = 0x2c6dd
        self.EMBED_RED = 0xdf1141
        self.EMBED_GREEN = 0x0eaa51


    @commands.Cog.listener()
    async def on_ready(self):
        #Make each server an id to a dictionary to distinguish them from one another
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.play_mode[id] = "youtube"
            self.search_mode[id] = "single"
        print("Bot Online")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        player: wavelink.Player = member.guild.voice_client
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

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        ctx = self.join_context
        if str(reason) == "FINISHED":
            if not player.queue.is_empty:
                new = await player.queue.get_wait()
                try:
                    await player.play(new)
                except Exception as e:
                    embed = discord.Embed(title=f"Something went wrong while playing: {new.title}", color=self.EMBED_RED)
                    await ctx.send(embed=embed)
                    vars = {
                            "player": player,
                            "reason": reason,
                            "queue": player.queue,
                            "error": e
                        }
                    return

                embed = self.nowPlaying(ctx,new)
                await ctx.send(embed=embed)
            else:
                await player.stop()
        else:
            embed = discord.Embed(title=f"Something went wrong while playing: {track.title}", color=self.EMBED_RED)
            await ctx.send(embed=embed)
            vars = {
                    "player": player,
                    "reason": reason,
                    "queue": player.queue,
                }
            await self.sendDM("on_wavelink_track_end",vars)

    #Helper functions
    async def cog_command_error(self, ctx, error):
        print(error)
    
    async def cog_check(self,ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Sorry, music commands are not available in DMs. Please join a voice channel in a server containing Realm Tunes to use music commands!")
            return False
        return True
    
    def nowPlaying(self,ctx,track):
        id = int(ctx.guild.id)
        title = track.title
        duration = self.convertDuration(track.duration)
        link = track.uri
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}]({link}) ({duration})',
            colour = self.EMBED_GREEN
        )
        if self.play_mode == "youtube":
            thumbnail = track.thumbnail
            embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by {str(author)}',icon_url=avatar)
        return embed
    
    def convertDuration(self, duration):
        minutes = str(math.floor(duration/60))
        seconds = str(int(duration%60))
        if len(seconds) == 1:
            seconds = seconds + "0"
        return f"{minutes}:{seconds}"

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
        player: wavelink.Player = ctx.voice_client
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
                embed = discord.Embed(title=f"Something went wrong while connecting to this voice channel!", color=self.EMBED_RED)
                await ctx.send(embed=embed)
                vars = {
                    "user_channel": user_channel,
                    "result": result
                }
                await self.sendDM("join",vars)
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
        player: wavelink.Player = ctx.voice_client

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
        id = int(ctx.guild.id)
        if len(query) == 0:
            await ctx.send("Please enter a search term")
            return
        try:
            if self.play_mode[id] == "youtube":
                search = await wavelink.YouTubeTrack.search(query=query, return_first=True)
            elif self.play_mode[id] == "soundcloud":
                search = await wavelink.SoundCloudTrack.search(query=query, return_first=True)
        except IndexError:
            await ctx.send(f"No results for search query: {query}\nPlease try a different search query")
            return
        except Exception as e:
            embed = discord.Embed(title=f"Something went wrong while searching for: {query}", color=self.EMBED_RED)
            await ctx.send(embed=embed)
            vars = {
                    "error": e,
                    "query": query,
                }
            await self.sendDM("play_command",vars)
            return
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                await ctx.send("Unable to connect to the voice channel to play music")
                return
        else:
            await ctx.send("You must be connected to a voice channel to play music")
            return
        
        player: wavelink.Player = ctx.voice_client
        await player.play(search)

        embed = self.nowPlaying(ctx,search)
        await ctx.send(embed=embed)
    
    @commands.command(
        name="stop",
        aliases=['s'],
        help=""
    )
    async def stop_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client

        if player == None:
            await ctx.send("Bot is not connected to any voice channel")
            return 
        if not player.is_playing():
            await ctx.send("Nothing is playing right now")
            return 
        if player.is_playing:
            await player.stop()
            await ctx.send("Playback stopped")
        else:
            await ctx.send("Nothing Is playing right now")
            return 
    
    @commands.command(
        name="pause",
        aliases=['t','timeout'],
        help=""
    )
    async def pause_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client

        if player is None:
            await ctx.send("Bot is not connected to any voice channel")
            return 
        if not player.is_playing():
            await ctx.send("Nothing is playing right now")
            return 
        if not player.is_paused():
                await player.pause()
                await ctx.send("Playback Paused")
        else:
            await ctx.send("Playback is already paused")
            return
    
    @commands.command(
        name="resume",
        aliases=['r'],
        help=""
    )
    async def resume_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client

        if player is None:
            await ctx.send("Bot is not connnected to any voice channel")
            return
        if not player.is_playing():
            await ctx.send("Nothing is playing right now")
            return 
        if player.is_paused():
            await player.resume()
            await ctx.send("Playback resumed")
        else:
            await ctx.send("Playback is not paused")
            return

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

        player: wavelink.Player = ctx.voice_client
        await player.set_volume(to)
        await ctx.send(f"Set volume to {to}%")
    
    @commands.command(
        name="play_config",
        aliases=['spc'],
        help=""
    )
    async def set_play_config_command(self, ctx: commands.Context, play_mode:str,search_mode:str):
        id = int(ctx.guild.id)
        if play_mode.lower() in self.VALID_PLAY_MODE and search_mode.lower() in self.VALID_SEARCH_MODE:
            self.play_mode[id] = play_mode.lower()
            self.search_mode[id] = search_mode.lower()
            if search_mode.lower() == "list":
                search_mode = "list of songs"
            else:
                search_mode = "single song"
            author = ctx.author
            avatar = author.avatar.url
            embed = discord.Embed(
            title = "Successfully Configured",
            description = f'Search songs from {play_mode.lower()}\nSearch for a {search_mode}',
            colour = self.EMBED_GREEN
        )
            embed.set_footer(text=f'Play command configured by {str(author)}',icon_url=avatar)
            await ctx.send(embed=embed)
        else:
            await ctx.send("Please enter a valid configuration for play_mode ['youtube','spotify','soundcloud'], and search_mode ['single','list']")
    
async def setup(bot):
    await bot.add_cog(Music(bot))
    print("Loaded music cog")
