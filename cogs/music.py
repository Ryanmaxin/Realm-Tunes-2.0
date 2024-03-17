import math

import discord
import validators
import wavelink
from discord import Color, app_commands
from discord.ext import commands
from discord.ui import Select, View

# from cogs.button import ButtonView
from helpers import sendDM

# from discord_slash.model import ButtonStyle
# from discord_slash.utils.manage_components import (create_actionrow,
#                                                    create_button)



class Music(commands.Cog):
    def __init__(self,bot: commands.Bot):
        pass

    @commands.Cog.listener()
    async def on_ready(self):
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
        if str(reason) == "replaced":
            return
        if str(reason) != "finished" and str(reason) != "stopped":
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

        # if track.album.name:
        #     embed.add_field(name="Album", value=track.album.name)

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
            colour = Color.blurple()
        )
        if track.artwork:
            thumbnail = track.artwork
            embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Song added by {author.name}',icon_url=avatar)
        return embed

    def addedPlaylistToQueue(self,ctx,playlist,url,img):
        title = playlist.name
        length = len(playlist.tracks)
        author = ctx.user
        avatar = author.display_avatar.url
        embed = discord.Embed(
            title = f"Playlist Added to Queue",
            description = f'[{title}]({url}) ({length} songs)',
            colour = Color.blurple()
        )
        thumbnail = img
        embed.set_thumbnail(url=thumbnail)
        embed.set_footer(text=f'Playlist added by {author.name}',icon_url=avatar)
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

        # buttons = [
        #     create_button(
        #         style=ButtonStyle.green,
        #         label="A Green Button"
        #     ),
        #   ]

        # action_row = create_actionrow(*buttons)
        
        async def songChosen(interaction: discord.Interaction):
            await interaction.response.defer()
            song_number = int(select.values[0])
            select.placeholder = f"Song {song_number} chosen"
            select.disabled = True
            new_view = View()
            new_view.add_item(select)
            await interaction.message.edit(embed=embed,view=new_view)
            player: wavelink.Player = ctx.guild.voice_client
            selection = search_list[song_number-1]

            selection.requester = ctx.user
            await player.queue.put_wait(selection)
            len = player.queue.count
            queue_embed = self.addedSongToQueue(ctx,selection,len)
            await interaction.followup.send(embed=queue_embed)

            if not (player.playing or player.paused) or is_playnow:
                # Play now since we aren't playing anything...
                await player.play(player.queue.get())
            
            # await self.route(ctx,selection,player,is_playnow)
        select.callback = songChosen
        view = View()
        view.add_item(select)
        await ctx.response.send_message(embed=embed,view=view)
        return 

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
            return
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
                embed = self.addedSongToQueue(ctx,track,len)
                await ctx.response.send_message(embed=embed)
                # if player.playing or player.paused:
                #     embed = self.addedSongToQueue(ctx,track,len)
                #     await ctx.response.send_message(embed=embed)
                # else:
                #     await ctx.response.send_message("Success",ephemeral=True)

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

        player.queue.mode = wavelink.QueueMode.normal
        player.queue.clear()
        await player.stop()
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
        current_song = player.current.title
        await player.skip()
        await ctx.response.send_message(f"Skipped track: {current_song}")

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
        discord.app_commands.Choice(name='now', value=1)])
    @commands.guild_only()
    async def previous_command(self, ctx: discord.Interaction, priority:discord.app_commands.Choice[int]=0):
        if not (await self.validatePlay(ctx)):
            return
        player: wavelink.Player = ctx.guild.voice_client
        history = player.queue.history
        previous = None
        try:
            previous = history.get()
        except wavelink.QueueEmpty:
            await ctx.response.send_message(f"No previous song found")
            return
        
        
        is_playingnow = False
        if priority:
            is_playingnow = True
        previous.requester = ctx.user
        await player.queue.put_wait(previous)
        len = player.queue.count
        queue_embed = self.addedSongToQueue(ctx,previous,len)
        await ctx.response.send_message(embed=queue_embed)

        if not (player.playing or player.paused) or is_playingnow:
            # Play now since we aren't playing anything...
            await player.play(player.queue.get())
    
        

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
            await ctx.followup.send(embed=embed)
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

    @app_commands.command(
        name="timescale",
        description="Set the current song to nightcore, slowed, or regular"
    )
    @app_commands.choices(option=[
        discord.app_commands.Choice(name='custom', value=3),
        discord.app_commands.Choice(name='slowed', value=2),
        discord.app_commands.Choice(name='nightcore', value=1),
        discord.app_commands.Choice(name='regular', value=0)])
    @commands.guild_only()
    async def timescale_command(self, ctx: discord.Interaction, option:discord.app_commands.Choice[int], 
                             pitch: float = 1.0, speed: float=1.0,rate: float=1.0) -> None:
        chosen = None
        if option.value:
            chosen = option.value
        else:
            chosen = 0
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters

        if chosen == 3:
            filters.timescale.set(pitch=pitch, speed=speed, rate=rate)
        elif chosen == 2:
            filters.timescale.set(pitch=0.85, speed=0.85, rate=1)
        elif chosen == 1:
            filters.timescale.set(pitch=1.2, speed=1.2, rate=1)

        await player.set_filters(filters)

        if chosen == 0:
            await ctx.response.send_message("Set to regular... This may take a couple seconds")
        if chosen == 1:
            await ctx.response.send_message("Set to nightcore... This may take a couple seconds")
        if chosen == 2:
            await ctx.response.send_message("Set to slowed... This may take a couple seconds")
        if chosen == 3:
            await ctx.response.send_message("Set to custom timescale... This may take a couple seconds")

    @app_commands.command(
        name="distortion",
        description="Distort the current song"
    )
    @commands.guild_only()
    async def distortion_command(self, ctx: discord.Interaction) -> None:
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters

        filters.distortion.set(
            sin_offset=0.5,    # Adjusting sin offset to add some cool effects
            sin_scale=1.2,     # Increasing sin scale for a more pronounced effect
            cos_offset=0.3,    # Fine-tuning cos offset for additional coolness
            cos_scale=1.5,     # Increasing cos scale for a stronger effect
            tan_offset=0.2,    # Adding a slight tan offset for variety
            tan_scale=1.1,     # Adjusting tan scale for a nuanced effect
            offset=0.0,        # Keeping offset at default (optional)
            scale=1.0          # Keeping scale at default (optional)
        )

        await player.set_filters(filters)

        await ctx.response.send_message("Added distortion... This may take a couple of seconds")

    @app_commands.command(
        name="instrumental",
        description="Makes the current song instrumental"
    )
    @commands.guild_only()
    async def instrumental_command(self, ctx: discord.Interaction) -> None:
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters

        filters.karaoke.set(
            level=1.0,          # Setting the level to maximum (1.0) for full vocal removal effect
            mono_level=1.0     # Setting mono_level to maximum (1.0) for full mono effect, which can help in removing center-panned vocals
            # filter_band=1000.0, # Setting filter_band to a value that targets vocal frequencies (adjust as needed)
            # filter_width=500.0  # Setting filter_width to a moderate value to encompass a range of vocal frequencies
        )      # Keeping scale at default (optional)

        await player.set_filters(filters)

        await ctx.response.send_message("Removing vocals... This may take a couple of seconds")

    @app_commands.command(
        name="bass_boost",
        description="Boosts the bass of the current audio"
    )
    @commands.guild_only()
    async def bass_boost_command(self, ctx: discord.Interaction) -> None:
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters

        bands = [
            {"band": 0, "gain": 0.2}, {"band": 1, "gain": 0.15}, {"band": 2, "gain": 0.1},
            {"band": 3, "gain": 0.05}, {"band": 4, "gain": 0.0}, {"band": 5, "gain": -0.05},
            {"band": 6, "gain": -0.1}, {"band": 7, "gain": -0.1}, {"band": 8, "gain": -0.1},
            {"band": 9, "gain": -0.1}, {"band": 10, "gain": -0.1}, {"band": 11, "gain": -0.1},
            {"band": 12, "gain": -0.1}, {"band": 13, "gain": -0.1}, {"band": 14, "gain": -0.1}
        ]

        filters.equalizer.set(bands=bands)   

        await player.set_filters(filters)

        await ctx.response.send_message("Boosting bass... This may take a couple of seconds")

    @app_commands.command(
        name="eightd_audio",
        description="Makes the audio sound '8D'"
    )
    @commands.guild_only()
    async def eightd_audio_command(self, ctx: discord.Interaction) -> None:
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters


        filters.rotation.set(
            rotation_hz=0.2
        )      

        await player.set_filters(filters)

        await ctx.response.send_message("Adding rotation... This may take a couple of seconds")

    @app_commands.command(
        name="reset_filters",
        description="Reset all filters so that the song sounds normal again"
    )
    @commands.guild_only()
    async def reset_filters(self, ctx: discord.Interaction) -> None:
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            return
        if not (await self.validate(ctx,player)):
            return
        
        filters: wavelink.Filters = player.filters

        filters.reset()

        await player.set_filters(filters)

        await ctx.response.send_message("Resetting filters... This may take a couple of seconds")

    @app_commands.command(
        name="now_playing",
        description="Shows the currently playing song"
    )
    @commands.guild_only()
    async def now_playing_command(self, ctx: discord.Interaction):
        player: wavelink.Player = ctx.guild.voice_client
        if not player:
            raise Exception("No player")
        
        track = player.current
        if not track:
            ctx.response.send_message("No song is currently playing")
        title = track.title
        duration = self.convertDuration(track.length)
        link = track.uri

        user: discord.User | discord.Member = track.requester
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
    
