import string
import discord
import wavelink
from discord.ext import commands
from discord import app_commands
import sys
import math
from discord.ui import Select,View
from discord import Color
import validators
import random
import traceback
import logging

class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        self.bot = bot
        self.join_context = {}
        self.is_looping = {}
        self.is_repeating_playlist = {}
        self.previous_song = {}

    @commands.Cog.listener()
    async def on_ready(self):
        # await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="-help"))
        #Make each server an id to a dictionary to distinguish them from one another
        for guild in self.bot.guilds:
            id = int(guild.id)
            self.is_looping[id] = False
            self.is_repeating_playlist[id] = False
            self.previous_song[id] = None
    
    @commands.Cog.listener()
    async def on_command_error(self,ctx,error):
        if isinstance(error, commands.CommandNotFound):
            await ctx.response.send_message("That command does not exist. Use -help for list of all available commands")
            return
        else:
            command_name = ctx.invoked_with

            embed = discord.Embed(title=f"Something went wrong with {command_name}", color=Color.red())
            await ctx.response.send_message(embed=embed)

            error_type = type(error)
            error_traceback = error.__traceback__

            print(command_name,error)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(error_type, error, error_traceback, file=sys.stderr)

            exc_info = (error_type, error, error_traceback)
            logger = logging.getLogger()
            logger.error('Exception occurred', exc_info=exc_info)

            await self.sendDM(command_name,error)
            return


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
    async def on_wavelink_track_end(self, payload: wavelink.TrackEventPayload):
        player = payload.player
        reason = payload.reason
        track = payload.track
        id = int(player.guild.id)
        ctx = self.join_context[id]
        self.previous_song[id] = track
        if str(reason) == "REPLACED":
            return
        if not str(reason) == "FINISHED" and not str(reason) == "STOPPED":
            embed = discord.Embed(title=f"Something went wrong while playing: {track.title}", color=Color.red())
            await ctx.response.send_message(embed=embed)
            await self.sendDM(f"{reason}")
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
    
    async def cog_check(self,ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.response.send_message("Sorry, music commands are not available in DMs. Please join a voice channel in a server containing Realm Tunes to use music commands!")
            return False
        return True
    
    def nowPlaying(self,ctx,track):
        title = track.title
        duration = self.convertDuration(track.duration)
        link = track.uri
        author = ctx.user
        avatar = author.display_avatar.url

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
        author = ctx.user
        avatar = author.display_avatar.url

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
        title = playlist.name
        length = len(playlist.tracks)
        author = ctx.user
        avatar = author.display_avatar.url
        embed = discord.Embed(
            title = f"Playlist Added to Queue",
            description = f'[{title}]({url}) ({length} songs)',
            colour = Color.green()
        )
        thumbnail = img
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Playlist added by {str(author)}',icon_url=avatar)
        return embed

    def convertDuration(self, duration):
        duration = duration/1000
        minutes = str(math.floor(duration/60))
        intermediate_seconds = math.floor(duration%60)
        if(intermediate_seconds != 0):
            intermediate_seconds = intermediate_seconds - 1
        seconds = str(intermediate_seconds)

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


    async def sendDM(self, func):
        user = await self.bot.fetch_user(404491098946273280)
        message = f"Error in: {func} \n"
        await user.send(message)
    
    async def joinVC(self,ctx: discord.Interaction, channel):
        id = int(ctx.guild.id)
        result = None
        player: wavelink.Player = ctx.guild.voice_client
        if player is not None and player.is_connected():
            await player.move_to(channel)
        else:
            result = await channel.connect(cls=wavelink.Player,self_deaf=True)
            if result == None:
                return result
        self.join_context[id] = ctx
        result = True
        return result
    async def chooseSong(self,ctx: discord.Interaction,query,is_playnow=False):
        search_list = None
        search_list = await wavelink.YouTubeTrack.search(query)
        if not search_list:
            await ctx.response.send_message(f"No results for search query: {query}\nPlease try a different search query")
            return
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
        
        async def SongChosen(interaction: discord.Interaction):
            await interaction.response.defer()
            song_number = int(select.values[0])
            select.placeholder = f"Song {song_number} chosen"
            select.disabled = True
            new_view = View()
            new_view.add_item(select)
            await interaction.message.edit(embed=embed,view=new_view)
            player: wavelink.Player = ctx.guild.voice_client
            selection = search_list[song_number-1]
            
            await self.route(ctx,selection,player,is_playnow)
        select.callback = SongChosen
        view = View()
        view.add_item(select)
        msg = await ctx.response.send_message(embed=embed,view=view)
        return 

    async def validatePlay(self,ctx: discord.Interaction):
        if ctx.user.voice:
            user_channel = ctx.user.voice.channel
            if not ctx.guild.voice_client:
                result = await self.joinVC(ctx,user_channel)
                if result == None:
                    embed = discord.Embed(title=f"Something went wrong while connecting to the voice channel!", color=Color.red())
                    await ctx.response.send_message(embed=embed)
                    vars = {
                        "user_channel": user_channel,
                        "result": result
                    }
                    await self.sendDM("play",vars)
                    return False
        else:
            await ctx.response.send_message("You must be connected to a voice channel to play music")
            return False
        return True

    async def validate(self,ctx,player):
        if player == None:
            await ctx.response.send_message("Realm Tunes is not connected to any voice channel")
            return False
        if not player.is_playing():
            await ctx.response.send_message("Nothing is playing right now")
            return False
        return True
    
    async def playSong(self,ctx,search,player):
        track = await player.play(search)
        embed = self.nowPlaying(ctx,track)
        await ctx.response.send_message(embed=embed)

    async def addToQueue(self,ctx,search,player,is_playlist=False):
        await player.queue.put_wait(search)
        len = player.queue.count
        if not is_playlist:
            embed = self.addedSongToQueue(ctx,search,len)
            await ctx.response.send_message(embed=embed)

    
    async def route(self,ctx,track,player,is_playnow,is_playlist = False):
        print("ADDED2!")
        if (player.is_playing() or player.is_paused()) and not is_playnow:
            await self.addToQueue(ctx,track,player,is_playlist)
        else:
            await self.playSong(ctx,track,player)
    
    async def omniPlayer(self,ctx: discord.Interaction,query,is_playnow):
        if len(query) == 0:
            await ctx.response.send_message("Please enter a search term")
            return
        if not await self.validatePlay(ctx):
            return
        if not validators.url(query):
            #Play will occur later, this function only creates an embed menu to select the song
            await self.chooseSong(ctx, query,is_playnow)
            return
        else:
            #When a url is given, play the song immediately
            player: wavelink.Player = ctx.guild.voice_client
            if "list=P" in query:
                if is_playnow:
                    is_playnow = False
                #PLAYLIST TECH
                playlist = await wavelink.YouTubePlaylist.search(query)
                thumbnail = playlist.tracks[0].thumbnail
                embed = self.addedPlaylistToQueue(ctx,playlist,query,thumbnail)
                await ctx.response.send_message(embed=embed)
                for track in playlist.tracks:
                    await self.route(ctx,track,player,is_playnow,True)

            else:
                track = None
                try:
                    track = await wavelink.YouTubeTrack.search(query)
                except:
                    track = await wavelink.node.get_tracks(query, cls=wavelink.Track)
                if not track:
                    await ctx.response.send_message(f"No results for search query: {query}\nPlease try a different search query")
                    return
                track = track[0]
                await self.route(ctx,track,player,is_playnow)
            return

    @app_commands.command(
        name="join",
        description="Realm Tunes joins your current vc if you are in one."
    )
    async def join_command(self, ctx: discord.Interaction):
        if ctx.user.voice:
            user_channel = ctx.user.voice.channel
            result = await self.joinVC(ctx,user_channel)
            if result == None:
                embed = discord.Embed(title=f"Something went wrong while connecting to the voice channel!", color=Color.red())
                await ctx.response.send_message(embed=embed)
                vars = {
                    "user_channel": user_channel,
                    "result": result
                }
                await self.sendDM("join",vars)
            else:
                await ctx.response.send_message(f'Realm Tunes joined ``{user_channel}``')
        else:
            await ctx.response.send_message("You must be connected to a voice channel")

    @app_commands.command(
        name="leave",
        description="Realm Tunes leaves his current vc."
    )
    async def leave_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        id = int(ctx.guild.id)
        if player is None:
            await ctx.response.send_message("Realm Tunes is not connected to any voice channel")
            return
        await player.disconnect()
        self.is_looping[id] = False
        self.is_repeating_playlist[id] = False
        self.previous_song[id] = None
        await ctx.response.send_message("Realm Tunes left the chat")
    
    @app_commands.command(
        name="play",
        description="Realm Tunes will immediately queue up the query if it is a url/playlist, otherwise it will search for the query on YouTube and create a menu where you can choose a song."
    )
    async def play_command(self, ctx: discord.Interaction, *, query: str=""):
        is_nowplaying = False
        await self.omniPlayer(ctx,query,is_nowplaying)


    @app_commands.command(
        name="play_now",
        description="Identical to Play, except the desired song will be play immediately even if there is another song playing."
    )
    async def play_now_command(self, ctx: discord.Interaction, *, query: str=""):
        is_nowplaying = True
        await self.omniPlayer(ctx,query,is_nowplaying)

    
    @app_commands.command(
        name="clear",
        description="Clears the queue and ends the current song."
    )
    async def clear_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return

        await player.stop()
        player.queue.clear()
        await ctx.response.send_message("Playback stopped")
    
    @app_commands.command(
        name="pause",
        description="Switches between pausing and unpausing the music."
    )
    async def pause_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client

        if not (await self.validate(ctx,player)):
            return
        if player.is_paused():
            await player.resume()
            await ctx.response.send_message("Playback resumed")
        else:
            await player.pause()
            await ctx.response.send_message("Playback paused")

    @app_commands.command(
        name="skip",
        description="Skips the current song."
    )
    async def skip_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        await ctx.response.send_message(f"Skipped track: {player.current.title}")
        await player.stop()

    @app_commands.command(
        name="queue",
        description="Shows the current queue. Add a number to select specific page (when more then 10 songs)"
    )
    async def queue_command(self, ctx: discord.Interaction,*, page: int=1):
            player: wavelink.Player = ctx.guild.voice_client
            if not (await self.validate(ctx,player)):
                return
            queue = player.queue
            if queue.is_empty:
                await ctx.response.send_message("The queue is empty")
                return
            message=""
            embed = None
            # try:
            #     page_num = int(page)
            # except:
            #     page_num = 1
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
                await ctx.response.send_message(embed=embed)
            except:
                embed = discord.Embed(title=f"There are only {pages} page(s) in the queue", color=Color.red())
                await ctx.response.send_message(embed=embed)
  
    @app_commands.command(
        name="loop",
        description="Shows the current queue. Add a number to select specific page (when more then 10 songs)"
    )
    async def loop_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        id = int(ctx.guild.id)
        self.is_looping[id] = not self.is_looping[id]
        if self.is_looping[id]:
            await ctx.response.send_message(f"Now looping {player.current.title}")
        else:
            await ctx.response.send_message(f"No longer looping {player.current.title}")

    @app_commands.command(
        name="seek",
    )
    async def seek_command(self, ctx: discord.Interaction, seconds:int=0):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        length = player.current.length
        # try:
        #     seconds = int(to)
        # except:
        #     seconds = 0
        if (seconds <=0 or seconds >= length):
            seconds = 0
        await player.seek(seconds*1000)
        await ctx.response.send_message(f"Seeking to ({self.convertDuration(seconds*1000+1000)}) in the song")

    @app_commands.command(
        name="previous",
    )
    async def previous_command(self, ctx: discord.Interaction, now:str=""):
        id = int(ctx.guild.id)
        player: wavelink.Player = ctx.guild.voice_client
        previous = self.previous_song[id]
        if previous == None:
            await ctx.response.send_message(f"No previous song found")
            return
        if not (await self.validatePlay(ctx)):
            return
        
        is_playingnow = False
        if now == "now":
            is_playingnow = True
        await self.route(ctx,previous,player,is_playingnow)
        
        

    @app_commands.command(
        name="repeat",
    )
    async def repeat_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        id = int(ctx.guild.id)
        self.is_repeating_playlist[id] = not self.is_repeating_playlist[id]
        if self.is_repeating_playlist[id]:
            await ctx.response.send_message(f"Now repeating the queue")
        else:
            await ctx.response.send_message(f"No longer repeating the queue")

    @app_commands.command(
        name="shuffle",
    )
    async def shuffle_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        random.shuffle(player.queue._queue)
        await ctx.response.send_message(f"Shuffled the queue")
        

    @app_commands.command(
        name="volume",
    )
    async def volume_command(self, ctx: discord.Interaction, to:int=None):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        # try:
        #     to = int(to)
        # except:
        #     await ctx.response.send_message("Volume must be a whole number between 0 and 1000 (ex: 50)")
        #     return 
        if to > 1000:
            await ctx.response.send_message("Volume must be between 0 and 1000")
            return
        elif to < 0:
            await ctx.response.send_message("Volume must be between 0 and 1000")
            return
        elif to > 100:
            embed = discord.Embed(title=f"Warning: setting volume over 100% is not recommended. Please be careful!", color=Color.red())
            await ctx.response.send_message(embed=embed)
        await player.set_volume(to)
        await ctx.response.send_message(f"Set volume to {to}%")
    
    @app_commands.command(
        name="currently_playing",
    )
    async def currently_playing_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        embed = self.nowPlaying(ctx, player.current)
        await ctx.response.send_message(embed=embed)

    @app_commands.command(
        name="restart",
    )
    async def restart_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        await player.seek(0)
        await ctx.response.send_message("Starting the song from the beginning")

    # @app_commands.command(
    #     name="speed",
    #     aliases=['f'],
    #     help=""
    # )
    # async def timescale_command(self, ctx: discord.Interaction):
    #     try:
    #         player: wavelink.Player = ctx.guild.voice_client
    #         if not (await self.validate(ctx,player)):
    #             return
    #         # filter = wavelink.Filter(wavelink.k)
    #         await player.set_filter(wavelink.Filter(rotation=wavelink.Rotation(speed = 1.2)))

    #         await ctx.response.send_message("SET FILTER")
    #     except Exception as e:
    #         exc_type, exc_obj, exc_tb = sys.exc_info()
    #         fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    #         print(exc_type, fname, exc_tb.tb_lineno,e)
    
