import discord
from discord.ext import commands
from discord import Color
from discord import app_commands

class Help(commands.Cog):
    def __init__(self,bot: commands.Bot):
        pass

    @app_commands.command(
        name="help",
    )
    async def help_command(self,ctx:discord.Interaction):
            author = ctx.user
            embed = discord.Embed(
                title = "Realm Tunes Command Guide",
                colour = discord.Colour.yellow()
            )
            embed.add_field(name='Join', value= 'Realm Tunes joins your current vc if you are in one.\n\nUsage: {-join/-j}', inline=False)
            embed.add_field(name='Leave', value= 'Realm Tunes leaves his current vc.\n\nUsage: {-leave/-l}', inline=False)
            embed.add_field(name='Play', value= 'Realm Tunes will immediately queue up the query if it is a url/playlist, otherwise it will search for the query on YouTube and create a menu where you can choose a song.\n\nUsage: {-play/-p} {query}', inline=False)
            embed.add_field(name='Play Now', value= 'Identical to Play, except the desired song will be play immediately even if there is another song playing.\n\nUsage: {-play_now/-pn/-now} {query}', inline=False)
            embed.add_field(name='Clear', value='Clears the queue and ends the current song.\n\nUsage: {-clear/-c}', inline=False)
            embed.add_field(name='Pause', value= 'Switches between pausing and unpausing the music.\n\nUsage: {-toggle/-t}', inline=False)
            embed.add_field(name='Skip', value= 'Skips the current song.\n\nUsage: {-skip/-s}', inline=False)
            embed.add_field(name='Queue', value= 'Shows the current queue. Add a number to select specific page (when more then 10 songs)\n\nUsage: {-display_queue/-queue/-q/-dq} {page}', inline=False)
            embed.add_field(name='Loop', value= 'Toggles on or off looping. looping repeats the current song after it ends.\n\nUsage: {-loop}', inline=False)
            embed.add_field(name='Seek', value= 'Begins playing at the specified number of seconds into the song.\n\nUsage: {-seek} {seconds}', inline=False)
            embed.add_field(name='Previous', value= 'Puts the previously played song into the queue. You can add "now" to the end to play the song now.\n\nUsage: {-previous/-pp/-prev} {now}', inline=False)
            embed.add_field(name='Repeat', value= 'Toggles on or off repeating the current queue\n\nUsage: {-repeat/-r/-re}', inline=False)
            embed.add_field(name='Volume', value= 'Sets the volume of Realm Tunes to the specified amount\n\nUsage: {-volume/-v} {volume}', inline=False)
            embed.add_field(name='Currently Playing', value= 'Shows the song that is currently playing\n\nUsage: {-currently_playing/-cu/-current/-cp}', inline=False)
            embed.add_field(name='Restart', value= 'Begins playing the current song from the beginning\n\nUsage: {-restart/-res}', inline=False)

            await author.response.send_message(embed=embed)
