import logging
import math
import random
import string
import sys
import traceback

import discord
import validators
import wavelink
from discord import Color, app_commands
from discord.ext import commands
from discord.ui import Select, View

from helpers import sendDM


class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
        # await self.change_presence(activity=discord.Activity(type=discord.ActivityType.listening, name="-help"))
        #Make each server an id to a dictionary to distinguish them from one another
        pass


    @commands.Cog.listener()
    async def on_voice_state_update(self, member: discord.Member, before: discord.VoiceState, after: discord.VoiceState):
        player: wavelink.Player = member.guild.voice_client
        if not member.bot and before.channel != None and after.channel != before.channel:
            remaining_channel_members = before.channel.members
            if len(remaining_channel_members) == 1 and remaining_channel_members[0].bot and player.connected:
                await player.disconnect()
                await player.home.send(f"Realm Tunes left because there were no members remaining in {before.channel.mention}")



    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload):
        player = payload.player
        reason = payload.reason
        track = payload.track
        if str(reason) == "REPLACED":
            return
        if not str(reason) == "finished" and not str(reason) == "stopped":
            embed = discord.Embed(title=f"Something went wrong while playing: {track.title}", color=Color.red())
            await player.home.send(embed=embed)
            await sendDM(self,reason,f"Something went wrong while playing: {track.title}")
            return
        # if not player.queue.is_empty:
        #     if self.is_repeating_playlist[id]:
        #         await player.queue.put_wait(track)
        #     new = await player.queue.get_wait()
        #     await self.playSong(ctx,new,player)
        #     await player.seek(0)
        # else:
        #     await player.stop()
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload):
        print("HELLO")
        player = payload.player
        if not player:
            raise Exception("No player")
        
        track = payload.track
        title = track.title
        duration = self.convertDuration(track.length)
        link = track.uri

        user: discord.User | discord.Member = payload.original.requester
        author = user.name
        avatar = user.display_avatar.url

        embed = discord.Embed(
            title = "Now Playing",
            description = f'[{title}]({link}) ({duration})',
            colour = Color.green()
        )

        if track.artwork:
            embed.set_thumbnail(url=track.artwork)

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        embed.set_footer(text=f'Song added by {str(author)}',icon_url=avatar)

        await player.home.send(embed=embed)
    
    async def cog_check(self,ctx):
        if isinstance(ctx.channel, discord.DMChannel):
            await ctx.response.send_message("Sorry, music commands are not available in DMs. Please join a voice channel in a server containing Realm Tunes to use music commands!")
            return False
        return True
    
    def addedSongToQueue(self,ctx,track,qlen):
        title = track.title
        duration = self.convertDuration(track.length)
        link = track.uri
        author = ctx.user
        avatar = author.display_avatar.url

        embed = discord.Embed(
            title = f"Added to Queue ({qlen})",
            description = f'[{title}]({link}) ({duration})',
            colour = Color.green()
        )
        if track.artwork:
            thumbnail = track.artwork
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
    
    async def joinVC(self,ctx: discord.Interaction, channel):
        result = None
        player: wavelink.Player = ctx.guild.voice_client
        if player is not None and player.is_connected():
            await player.move_to(channel)
        else:
            result = await channel.connect(cls=wavelink.Player,self_deaf=True)
            if result == None:
                return result
        result = True
        return result
    async def chooseSong(self,ctx: discord.Interaction,query,is_playnow=False):
        try:
            search_list = None
            search_list = await wavelink.Playable.search(query, source=wavelink.TrackSource.YouTube)
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
                duration = self.convertDuration(track.length)
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
                try:
                    await interaction.response.defer()
                    song_number = int(select.values[0])
                    select.placeholder = f"Song {song_number} chosen"
                    select.disabled = True
                    new_view = View()
                    new_view.add_item(select)
                    await interaction.followup.send(embed=embed,view=new_view)
                    player: wavelink.Player = ctx.guild.voice_client
                    selection = search_list[song_number-1]
                    await self.route(ctx,selection,player,is_playnow)
                except Exception as e:
                    print(e)
            select.callback = SongChosen
            view = View()
            view.add_item(select)
            await ctx.response.send_message(embed=embed,view=view)
            return 
        except Exception as e:
            print(e)

    async def validatePlay(self,ctx: discord.Interaction):
        if ctx.user.voice:
            user_channel = ctx.user.voice.channel
            if not ctx.guild.voice_client:
                result = await self.joinVC(ctx,user_channel)
                if result == None:
                    embed = discord.Embed(title=f"Something went wrong while connecting to the voice channel!", color=Color.red())
                    await ctx.response.send_message(embed=embed)
                    raise Exception("Something went wrong while connecting to the voice channel!")
                    # await self.sendDM("play",vars)
                    # return False
        else:
            await ctx.response.send_message("You must be connected to a voice channel to play music")
            return False
        player: wavelink.Player = ctx.guild.voice_client
        player.autoplay = wavelink.AutoPlayMode.partial
        if not hasattr(player, "home"):
            player.home = ctx.channel
        elif player.home != ctx.channel:
            await ctx.response.send_message(f"You can only use commands in {player.home.mention}, as the player has already started there.")
            return
        return True

    async def validate(self,ctx,player):
        if player == None:
            await ctx.response.send_message("Realm Tunes is not connected to any voice channel")
            return False
        if hasattr(player, "home") and player.home != ctx.channel:
            await ctx.response.send_message(f"You can only use commands in {player.home.mention}, as the player has already started there.")
            return False
        if not player.playing:
            await ctx.response.send_message("Nothing is playing right now")
            return False
        return True
    
    async def omniPlayer(self,ctx: discord.Interaction,query,is_playnow):
        if not await self.validatePlay(ctx):
            return
        player: wavelink.Player = ctx.guild.voice_client
        if not validators.url(query):
            #Play will occur later, this function only creates an embed menu to select the song
            await self.chooseSong(ctx, query,is_playnow)
        else:
            #When a url is given, play the song immediately
            # player: wavelink.Player = ctx.guild.voice_client
            result = await wavelink.Playable.search(query)
            if not result:
                await ctx.response.send_message(f"No results for search query: {query}\nPlease try a different search query")
                return
            if isinstance(result, wavelink.Playlist):
                for track in result:
                    track.requester = ctx.user
                thumbnail = result.artwork
                embed = self.addedPlaylistToQueue(ctx,result,query,thumbnail)
                await ctx.response.send_message(embed=embed)
                await player.queue.put_wait(result)
            else:
                track: wavelink.Playable = result[0]
                track.requester = ctx.user
                await player.queue.put_wait(track)
                len = player.queue.count
                if player.playing or player.paused:
                    embed = self.addedSongToQueue(ctx,track,len)
                    await ctx.response.send_message(embed=embed)
                else:
                    # await ctx.response.defer(ephemeral=True)
                    await ctx.response.send_message("Success",delete_after=2)
                    # await ctx.

        if not (player.playing or player.paused) or is_playnow:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get())
        return

    @app_commands.command(
        name="join",
        description="Realm Tunes joins your current vc if you are in one."
    )
    @commands.guild_only()
    async def join_command(self, ctx: discord.Interaction):
        if await self.validatePlay(ctx):
            await ctx.response.send_message(f'Realm Tunes joined {ctx.user.voice.channel.mention}')

    @app_commands.command(
        name="leave",
        description="Realm Tunes leaves his current vc."
    )
    @commands.guild_only()
    async def leave_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if player is None:
            await ctx.response.send_message("Realm Tunes is not connected to any voice channel")
            return
        if hasattr(player, "home") and player.home != ctx.channel:
            await ctx.response.send_message(f"You can only use commands in {player.home.mention}, as the player has already started there.")
            return False
        await player.disconnect()
        await ctx.response.send_message("Realm Tunes left the chat")
    
    @app_commands.command(
        name="play",
        description="Queue the song designated in the query if it is a url, otherwise brings up a menu to choose a song."
    )
    @commands.guild_only()
    @app_commands.describe(query='Can be a url (including playlist) to be played directly, or a song title to be searched on youtube.')
    async def play_command(self, ctx: discord.Interaction, query: str):
        is_nowplaying = False
        await self.omniPlayer(ctx,query,is_nowplaying)


    @app_commands.command(
        name="play_now",
        description="Like Play, except the desired song will be play immediately even if there is another song playing."
    )
    @commands.guild_only()
    async def play_now_command(self, ctx: discord.Interaction, query: str):
        is_nowplaying = True
        await self.omniPlayer(ctx,query,is_nowplaying)

    
    @app_commands.command(
        name="clear",
        description="Clears the queue and ends the current song."
    )
    @commands.guild_only()
    async def clear_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return

        await player.stop()
        player.queue.clear()
        await ctx.response.send_message("Playback stopped")
    
    @app_commands.command(
        name="pause",
        description="Pauses the music, if it is unpaused."
    )
    @commands.guild_only()
    async def pause_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client

        if not (await self.validate(ctx,player)):
            return
        if player.paused:
            await ctx.response.send_message("Music is already paused")
        else:
            await player.pause(True)
            await ctx.response.send_message("Playback paused")
    
    @app_commands.command(
        name="resume",
        description="unpauses the music, if it is paused."
    )
    @commands.guild_only()
    async def resume_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client

        if not (await self.validate(ctx,player)):
            return
        if player.paused:
            await ctx.response.send_message("Playback resumed")
        else:
            await player.pause(True)
            await ctx.response.send_message("Music is already unpaused")

    @app_commands.command(
        name="skip",
        description="Skips the current song."
    )
    @commands.guild_only()
    async def skip_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        await player.skip()
        await ctx.response.send_message(f"Skipped track: {player.current.title}")

    @app_commands.command(
        name="queue",
        description="Shows the current queue. Add a number to select specific page (when more then 10 songs)"
    )
    @commands.guild_only()
    async def queue_command(self, ctx: discord.Interaction,*, page_number: int=1):
            player: wavelink.Player = ctx.guild.voice_client
            if not (await self.validate(ctx,player)):
                return
            queue = player.queue
            if queue.is_empty:
                await ctx.response.send_message("The queue is empty")
                return
            message=""
            embed = None
            if page_number <= 0:
                page_number = 1
            start = page_number * 10 - 10
            pages = math.ceil(queue.count / 10)
            if page_number > pages:
                embed = discord.Embed(title=f"There are only {pages} page(s) in the queue", color=Color.red())
                await ctx.response.send_message(embed=embed)
                return
            for num in range(0,10):
                current_song = start+num
                try:
                    track = queue[current_song]
                except:
                    break
                title = track.title
                message += f"({current_song+1}) {title}\n\n"
                embed = discord.Embed(
                    title = f"Music Queue - Page {page_number}/{pages}",
                    description = message,
                    colour = Color.green()
                )
            await ctx.response.send_message(embed=embed)
                
  
    @app_commands.command(
        name="loop",
        description="Toggles on or off looping. looping repeats the current song after it ends."
    )
    @commands.guild_only()
    async def loop_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        if player.queue.mode != wavelink.QueueMode.loop:
            #Turn looping off
            player.queue.mode = wavelink.QueueMode.loop
            await ctx.response.send_message(f"Now looping {player.current.title}")
            
        else:
            #Turn looping on
            player.queue.mode = wavelink.QueueMode.normal
            await ctx.response.send_message(f"No longer looping {player.current.title}")
            

    @app_commands.command(
        name="seek",
        description="Begins playing at the specified number of seconds into the song."
    )
    @commands.guild_only()
    async def seek_command(self, ctx: discord.Interaction, seconds:int):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        length = player.current.length
        if (seconds <=0 or seconds >= length):
            seconds = 0
        await player.seek(seconds*1000)
        await ctx.response.send_message(f"Seeking to ({self.convertDuration(seconds*1000+1000)}) in the song")

    @app_commands.command(
        name="previous",
        description="Puts the previously played song into the queue. You can add 'now' to the end to play the song now."
    )
    @app_commands.describe(priority='Whether to play the command immediately or just add it to the queue' )
    @app_commands.choices(priority=[
        discord.app_commands.Choice(name='now', value=1),
        discord.app_commands.Choice(name='queue', value=0)])
    @commands.guild_only()
    async def previous_command(self, ctx: discord.Interaction, priority:discord.app_commands.Choice[int]=0):
        if not (await self.validatePlay(ctx)):
            return
        player: wavelink.Player = ctx.guild.voice_client
        history = player.queue.history
        try:
            previous = history.get()
        except wavelink.QueueEmpty:
            await ctx.response.send_message(f"No previous song found")
            return
        await history.delete(0)
        
        
        is_playingnow = False
        if priority:
            is_playingnow = True
        await self.route(ctx,previous,player,is_playingnow)
        
        

    @app_commands.command(
        name="repeat",
        description="Toggles on or off repeating the current queue."
    )
    @commands.guild_only()
    async def repeat_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        if player.queue.mode != wavelink.QueueMode.loop_all:
            #Turn repeating off
            player.queue.mode = wavelink.QueueMode.loop_all
            await ctx.response.send_message(f"Now repeating the queue")
            
        else:
            #Turn repeating on
            player.queue.mode = wavelink.QueueMode.normal
            await ctx.response.send_message(f"No longer repeating the queue")

    @app_commands.command(
        name="shuffle",
        description="Puts the current queue in a random order."
    )
    @commands.guild_only()
    async def shuffle_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        player.queue.shuffle()
        await ctx.response.send_message(f"Shuffled the queue")
        

    @app_commands.command(
        name="volume",
        description="Sets the volume of Realm Tunes to the specified amount."
    )
    @commands.guild_only()
    async def volume_command(self, ctx: discord.Interaction, percent:int):
        player: wavelink.Player = ctx.guild.voice_client
        if not (await self.validate(ctx,player)):
            return
        if percent > 1000:
            await ctx.response.send_message("Volume must be between 0 and 1000")
            return
        elif percent < 0:
            await ctx.response.send_message("Volume must be between 0 and 1000")
            return
        elif percent > 100:
            embed = discord.Embed(title=f"Warning: setting volume over 100% is not recommended. Please be careful!", color=Color.red())
            await ctx.response.send_message(embed=embed)
        await player.set_volume(percent)
        await ctx.response.send_message(f"Set volume to {percent}%")

    @app_commands.command(
        name="restart",
        description="Begins playing the current song from the beginning"
    )
    @commands.guild_only()
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
        
    @app_commands.command(
    name="help2",
    description="Displays list of available commands"
    )
    async def help2_command(self,ctx:discord.Interaction):
            author = ctx.user
            embed = discord.Embed(
                title = "Realm Tunes Command Guide",
                colour = discord.Colour.yellow()
            )
            embed.add_field(name='Join', value= 'Realm Tunes joins your current vc if you are in one.', inline=False)
            embed.add_field(name='Leave', value= 'Realm Tunes leaves his current vc.', inline=False)
            embed.add_field(name='Play', value= 'Realm Tunes will immediately queue up the query if it is a url/playlist, otherwise it will search for the query on YouTube and create a menu where you can choose a song.', inline=False)
            embed.add_field(name='Play Now', value= 'Identical to Play, except the desired song will be play immediately even if there is another song playing.', inline=False)
            embed.add_field(name='Clear', value='Clears the queue and ends the current song.', inline=False)
            embed.add_field(name='Pause', value= 'Switches between pausing and unpausing the music.', inline=False)
            embed.add_field(name='Skip', value= 'Skips the current song.', inline=False)
            embed.add_field(name='Queue', value= 'Shows the current queue. Add a number to select specific page (when more then 10 songs)', inline=False)
            embed.add_field(name='Loop', value= 'Toggles on or off looping. looping repeats the current song after it ends.', inline=False)
            embed.add_field(name='Seek', value= 'Begins playing at the specified number of seconds into the song.', inline=False)
            embed.add_field(name='Previous', value= 'Puts the previously played song into the queue. You can add "now" to the end to play the song now.', inline=False)
            embed.add_field(name='Repeat', value= 'Toggles on or off repeating the current queue', inline=False)
            embed.add_field(name='Shuffle', value= 'Puts the current queue in a random order.', inline=False)
            embed.add_field(name='Volume', value= 'Sets the volume of Realm Tunes to the specified amount.', inline=False)
            embed.add_field(name='Current', value= 'Shows the song that is currently playing', inline=False)
            embed.add_field(name='Restart', value= 'Begins playing the current song from the beginning', inline=False)

            await author.response.send_message(embed=embed)
    
