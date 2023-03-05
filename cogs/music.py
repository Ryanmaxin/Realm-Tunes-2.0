import discord
import wavelink
from discord.ext import commands
import os
import sys
import math
from discord.ui import Select,View
from discord import Color
import validators
import traceback
import random

class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        bot.loop.create_task(self.create_nodes())

        self.join_context = {}
        self.is_looping = {}
        self.is_repeating_playlist = {}
        self.previous_song = {}


    @commands.Cog.listener()
    async def on_ready(self):
        #Make each server an id to a dictionary to distinguish them from one another
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.is_looping[id] = False
            self.is_repeating_playlist[id] = False
            self.previous_song[id] = None
        print("Bot Online")

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        id = int(member.guild.id)
        player: wavelink.Player = member.guild.voice_client
        if not member.bot and before.channel != None and after.channel != before.channel:
            remaining_channel_members = before.channel.members
            if len(remaining_channel_members) == 1 and remaining_channel_members[0].bot and player.is_connected():
                await player.disconnect()
                join_context = self.join_context[id]
                self.is_looping[id] = False
                self.is_repeating_playlist[id] = False
                self.previous_song[id] = None
                await join_context.channel.send(f"Realm Tunes left because there were no members remaining in ``{before.channel}``")


    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        """Event fired when a node has finished connecting."""
        print(f'Node: <{node.identifier}> is ready!')

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        id = int(player.guild.id)
        ctx = self.join_context[id]
        self.previous_song[id] = track
        if str(reason) == "REPLACED":
            return
        if not str(reason) == "FINISHED" and not str(reason) == "STOPPED":
            embed = discord.Embed(title=f"Something went wrong while playing: {track.title}", color=Color.red())
            await ctx.send(embed=embed)
            vars = {
                    "player": player,
                    "reason": reason,
                    "queue": player.queue,
                }
            await self.sendDM("on_wavelink_track_end(unexpected reason)",vars)
            return
        
        if self.is_looping[id]:
            await self.playSong(ctx,track,player)
            await player.seek(0)
        elif not player.queue.is_empty:
            if self.is_repeating_playlist[id]:
                await player.queue.put_wait(track)
            new = await player.queue.get_wait()
            await self.playSong(ctx,new,player)
            await player.seek(0)
        else:
            await player.stop()

    #Helper functions
    async def cog_command_error(self, ctx, error):
        print(error)
    
    async def cog_check(self,ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.send("Sorry, music commands are not available in DMs. Please join a voice channel in a server containing Realm Tunes to use music commands!")
            return False
        return True
    
    def nowPlaying(self,ctx,track):
        title = track.title
        duration = self.convertDuration(track.duration)
        link = track.uri
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}]({link}) ({duration})',
            colour = Color.green()
        )
        if type(track) == wavelink.YouTubeTrack:
            thumbnail = track.thumbnail
            embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by {str(author)}',icon_url=avatar)
        return embed
    
    def addedSongToQueue(self,ctx,track,qlen):
        title = track.title
        duration = self.convertDuration(track.duration)
        link = track.uri
        author = ctx.author
        avatar = author.avatar.url

        embed = discord.Embed(
            title = f"Added to Queue ({qlen})",
            description = f'[{title}]({link}) ({duration})',
            colour = Color.green()
        )
        if type(track) == wavelink.YouTubeTrack:
            thumbnail = track.thumbnail
            embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by {str(author)}',icon_url=avatar)
        return embed

    def addedPlaylistToQueue(self,ctx,playlist,url,img):
        try:
            title = playlist.name
            length = len(playlist.tracks)
            author = ctx.author
            avatar = author.avatar.url
            embed = discord.Embed(
                title = f"Playlist Added to Queue",
                description = f'[{title}]({url}) ({length} songs)',
                colour = Color.green()
            )
            thumbnail = img
            embed.set_thumbnail(url=thumbnail)
            embed.set_footer(text=f'Playlist added by {str(author)}',icon_url=avatar)
            return embed
        except Exception as e:
            error = traceback.format_exc()
            print(error)
            print(e)
            return

    def convertDuration(self, duration):
        minutes = str(math.floor(duration/60))
        seconds = str(int(duration%60))
        if len(seconds) == 1:
            seconds = "0" + seconds
        return f"{minutes}:{seconds}"

    def buildResponse(self,length):
        options=[
            discord.SelectOption(value="1",label="One",emoji="1️⃣"),
            discord.SelectOption(value="2", label="Two",emoji="2️⃣"),
            discord.SelectOption(value="3", label="Three",emoji="3️⃣"),
            discord.SelectOption(value="4", label="Four",emoji="4️⃣"),
            discord.SelectOption(value="5", label="Five",emoji="5️⃣"),
            discord.SelectOption(value="6", label="Six",emoji="6️⃣"),
            discord.SelectOption(value="7", label="Seven",emoji="7️⃣"),
            discord.SelectOption(value="8", label="Eight",emoji="8️⃣"),
            discord.SelectOption(value="9", label="Nine",emoji="9️⃣"),
            discord.SelectOption(value="10", label="Ten",emoji="🔟")
            ]
        options = options[:length]
        return options


    async def sendDM(self,func, error):
        #vars:dict for previous iteration
        user = await self.bot.fetch_user(404491098946273280)
        message = f"Error in: {func}"
        message += error
        # for var in vars:
        #     message += f"\n{var}: {vars[var]}"
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
        id = int(ctx.guild.id)
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
    async def chooseSong(self,ctx,query,is_playnow=False):
        try:
            search_list = None
            search_list = await wavelink.YouTubeTrack.search(query=query)
            #Soundcloud Disabled until I can find a fix for the 30 second cutoff
            i=0
            length = 10
            if len(search_list) < 10:
                length = len(search_list)
            message=""
            emoji_list = ["1️⃣","2️⃣","3️⃣","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
            for track in search_list[:length]:
                title = track.title
                duration = self.convertDuration(track.duration)
                link = track.uri
                message += f"{emoji_list[i]} [{title}]({link}) ({duration})\n\n"
                i+=1
            embed = discord.Embed(
                title = f"Youtube Search Results For: {query}",
                description = message,
                colour = Color.green()
            )
            select = Select(
                placeholder="Choose a song",
                min_values="1",
                max_values="1",
                options=self.buildResponse(length)
            )
            
            async def SongChosen(interaction):
                await interaction.response.defer()
                song_number = int(select.values[0])
                select.placeholder = f"Song {song_number} chosen"
                select.disabled = True
                new_view = View()
                new_view.add_item(select)
                await msg.edit(embed=embed,view=new_view)
                player: wavelink.Player = ctx.voice_client
                selection = search_list[song_number-1]
                await self.route(ctx,selection,player,is_playnow)
            select.callback = SongChosen
            view = View()
            view.add_item(select)
            msg = await ctx.send(embed=embed,view=view)
            return 
        except IndexError:
            await ctx.send(f"No results for search query: {query}\nPlease try a different search query")
            return
        except Exception as e:
            embed = discord.Embed(title=f"Something went wrong while searching for: {query}", color=Color.red())
            await ctx.send(embed=embed)
            vars = {
                    "error": e,
                    "query": query,
                    "search": search_list
                }
            await self.sendDM("play_command",vars)
            return

    async def validatePlay(self,ctx):
        if ctx.author.voice:
            user_channel = ctx.author.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                embed = discord.Embed(title=f"Something went wrong while connecting to the voice channel!", color=Color.red())
                await ctx.send(embed=embed)
                vars = {
                    "user_channel": user_channel,
                    "result": result
                }
                await self.sendDM("play",vars)
                return False
        else:
            await ctx.send("You must be connected to a voice channel to play music")
            return False
        return True

    async def validate(self,ctx,player):
        if player == None:
            await ctx.send("Realm Tunes is not connected to any voice channel")
            return False
        if not player.is_playing():
            await ctx.send("Nothing is playing right now")
            return False
        return True
    
    async def playSong(self,ctx,search,player):
        try:
            track = await player.play(search)
            embed = self.nowPlaying(ctx,track)
            await ctx.send(embed=embed)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(exc_type, fname, exc_tb.tb_lineno,e)

    async def addToQueue(self,ctx,search,player):
        await player.queue.put_wait(search)
        len = player.queue.count
        if type(search) == wavelink.tracks.PartialTrack:
            pass
        elif type(search) != wavelink.tracks.PartialTrack:
            embed = self.addedSongToQueue(ctx,search,len)
            await ctx.send(embed=embed)

    
    async def route(self,ctx,track,player,is_playnow):
        if (player.is_playing() or player.is_paused()) and not is_playnow:
            await self.addToQueue(ctx,track,player)
        else:
            await self.playSong(ctx,track,player)
    
    async def omniPlayer(self,ctx,query,is_playnow):
        try:
            if len(query) == 0:
                await ctx.send("Please enter a search term")
                return
            if not await self.validatePlay(ctx):
                return
            if not validators.url(query):
                #Play will occur later, this function only creates an embed menu to select the song
                await self.chooseSong(ctx, query,is_playnow)
                return
            else:
                #When a url is given, play the song immediately
                player: wavelink.Player = ctx.voice_client
                if "playlist?" in query:
                    if is_playnow:
                        is_playnow = False
                    #PLAYLIST TECH
                    playlist = await wavelink.YouTubePlaylist.search(query=query)
                    thumbnail = playlist.tracks[0].thumbnail
                    embed = self.addedPlaylistToQueue(ctx,playlist,query,thumbnail)
                    await ctx.send(embed=embed)
                    for track in playlist.tracks:
                        partial_track= wavelink.PartialTrack(query=track.title)
                        await self.route(ctx,partial_track,player,is_playnow)

                else:
                    track = None
                    try:
                        track = await player.YouTubeTrack.search(query=query)
                    except:
                        track = await player.node.get_tracks(query=query, cls=wavelink.Track)
                        track = track[0]
                    await self.route(ctx,track,player,is_playnow)
                return
        except IndexError:
            await ctx.send(f"No results for search query: {query}\nPlease try a different search query")
            return
        except Exception as e:
            embed = discord.Embed(title=f"Something went wrong while searching for: {query}", color=Color.red())
            await ctx.send(embed=embed)
            error = traceback.format_exc()
            print(error)
            # vars = {
            #         "error": e,
            #         "query": query,
            #     }
            await self.sendDM("play_command",error)
            return

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
                embed = discord.Embed(title=f"Something went wrong while connecting to the voice channel!", color=Color.red())
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
        id = int(ctx.guild.id)
        if player is None:
            await ctx.send("Realm Tunes is not connected to any voice channel")
            return
        await player.disconnect()
        self.is_looping[id] = False
        self.is_repeating_playlist[id] = False
        self.previous_song[id] = None
        await ctx.send("Realm Tunes left the chat")
    
    @commands.command(
        name="play",
        aliases=['p'],
        help=""
    )
    async def play_command(self, ctx: commands.Context, *, query: str=""):
        is_nowplaying = False
        await self.omniPlayer(ctx,query,is_nowplaying)


    @commands.command(
        name="play_now",
        aliases=['pn','now'],
        help=""
    )
    async def play_now_command(self, ctx: commands.Context, *, query: str=""):
        is_nowplaying = True
        await self.omniPlayer(ctx,query,is_nowplaying)

    
    @commands.command(
        name="clear",
        aliases=['c'],
        help=""
    )
    async def clear_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return

        await player.stop()
        player.queue.clear()
        await ctx.send("Playback stopped")
    
    @commands.command(
        name="toggle",
        aliases=['t'],
        help=""
    )
    async def toggle_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client

        if not (await self.validate(ctx,player)):
            return
        if player.is_paused():
            await player.resume()
            await ctx.send("Playback resumed")
        else:
            await player.pause()
            await ctx.send("Playback paused")

    @commands.command(
        name="skip",
        aliases=['s'],
        help=""
    )
    async def skip_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        await ctx.send(f"Skipped track: {player.track.title}")
        await player.stop()

    @commands.command(
        name="display_queue",
        aliases=['queue,''q','dq'],
        help=""
    )
    async def display_queue_command(self, ctx: commands.Context,*, page: str=""):
        try:
            player: wavelink.Player = ctx.voice_client
            if not (await self.validate(ctx,player)):
                return
            queue = player.queue
            if queue.is_empty:
                await ctx.send("The queue is empty")
                return
            message=""
            embed = None
            try:
                page_num = int(page)
            except:
                page_num = 1
            if page_num <= 0:
                page_num = 1
            start = page_num * 10 - 10
            pages = math.ceil(queue.count / 10)
            for num in range(0,10):
                current_song = start+num
                try:
                    track = queue[current_song]
                except:
                    break
                title = track.title
                message += f"({current_song+1}) {title}\n\n"
                embed = discord.Embed(
                    title = f"Music Queue - Page {page_num}/{pages}",
                    description = message,
                    colour = Color.green()
                )
            try:
                await ctx.send(embed=embed)
            except:
                embed = discord.Embed(title=f"There are only {pages} page(s) in the queue", color=Color.red())
                await ctx.send(embed=embed)
        except Exception as e:
            embed = discord.Embed(title=f"Something went wrong while displaying the queue", color=Color.red())
            await ctx.send(embed=embed)
            error = traceback.format_exc()
            print(error)
            # vars = {
            #         "error": e,
            #         "query": query,
            #     }
            await self.sendDM("display_queue_command",error)
            return
  
    @commands.command(
        name="loop",
        aliases=[],
        help=""
    )
    async def loop_command(self, ctx: commands.Context, to=None):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        id = int(ctx.guild.id)
        self.is_looping[id] = not self.is_looping[id]
        if self.is_looping[id]:
            await ctx.send(f"Now looping {player.track.title}")
        else:
            await ctx.send(f"No longer looping {player.track.title}")

    @commands.command(
        name="seek",
        aliases=[],
        help=""
    )
    async def seek_command(self, ctx: commands.Context, to):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        length = player.track.length
        try:
            seconds = int(to)
        except:
            seconds = 0
        if (seconds <=0 or seconds >= length):
            seconds = 0
        await player.seek(seconds*1000)

    @commands.command(
        name="previous",
        aliases=["pp","prev"],
        help=""
    )
    async def previous_command(self, ctx: commands.Context, now=""):
        id = int(ctx.guild.id)
        try:
            player: wavelink.Player = ctx.voice_client
            if not (await self.validatePlay(ctx)):
                return
            previous = self.previous_song[id]
            if previous == None:
                await ctx.send(f"No previous song found")
                return
            else:
                is_playingnow = False
                if now == "now":
                    is_playingnow = True
                await self.route(ctx,previous,player,is_playingnow)
            
        except Exception as e:
            embed = discord.Embed(title=f"Something went wrong while playing the previous song the queue", color=Color.red())
            await ctx.send(embed=embed)
            error = traceback.format_exc()
            print(error)
            # vars = {
            #         "error": e,
            #         "query": query,
            #     }
            await self.sendDM("previous_command",error)
            return
        

    @commands.command(
        name="repeat",
        aliases=['r','re'],
        help=""
    )
    async def repeat_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        id = int(ctx.guild.id)
        self.is_repeating_playlist[id] = not self.is_repeating_playlist[id]
        if self.is_repeating_playlist[id]:
            await ctx.send(f"Now repeating the queue")
        else:
            await ctx.send(f"No longer repeating the queue")

    @commands.command(
        name="shuffle",
        aliases=["shuf","sh"],
        help=""
    )
    async def shuffle_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        random.shuffle(player.queue._queue)
        await ctx.send(f"Shuffled the queue")
        

    @commands.command(
        name="volume",
        aliases=['v'],
        help=""
    )
    async def volume_command(self, ctx: commands.Context, to=None):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
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
            embed = discord.Embed(title=f"Warning: setting volume over 100% is not recommended. Please be careful!", color=Color.red())
            await ctx.send(embed=embed)
        await player.set_volume(to)
        await ctx.send(f"Set volume to {to}%")
    
    @commands.command(
        name="currently_playing",
        aliases=['cu','current','cp'],
        help=""
    )
    async def currently_playing_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        embed = self.nowPlaying(ctx, player.track)
        await ctx.send(embed=embed)

    @commands.command(
        name="restart",
        aliases=['res'],
        help=""
    )
    async def restart_command(self, ctx: commands.Context):
        player: wavelink.Player = ctx.voice_client
        if not (await self.validate(ctx,player)):
            return
        await player.seek(0)
        await ctx.send("Starting the song from the beginning")

    # @commands.command(
    #     name="speed",
    #     aliases=['f'],
    #     help=""
    # )
    # async def timescale_command(self, ctx: commands.Context):
    #     try:
    #         player: wavelink.Player = ctx.voice_client
    #         if not (await self.validate(ctx,player)):
    #             return
    #         # filter = wavelink.Filter(wavelink.k)
    #         await player.set_filter(wavelink.Filter(rotation=wavelink.Rotation(speed = 1.2)))

    #         await ctx.send("SET FILTER")
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #         print(exc_type, fname, exc_tb.tb_lineno,e)
        
async def setup(bot):
    await bot.add_cog(Music(bot))
    print("Loaded music cog")
