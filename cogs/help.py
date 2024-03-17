import discord
from discord import Color, app_commands
from discord.ext import commands


class Help(commands.Cog):
    def __init__(self,bot: commands.Bot):
        pass

    @app_commands.command(
        name="help",
        description="Displays list of available commands"
    )
    async def help_command(self,ctx:discord.Interaction):
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
            embed.add_field(name='Pause', value= 'Pauses the music.', inline=False)
            embed.add_field(name='Resume', value= 'Resumes the music.', inline=False)
            embed.add_field(name='Skip', value= 'Skips the current song.', inline=False)
            embed.add_field(name='Queue', value= 'Shows the current queue. Add a number to select specific page (when more then 10 songs).', inline=False)
            embed.add_field(name='Loop', value= 'Toggles on or off looping. looping repeats the current song after it ends.', inline=False)
            embed.add_field(name='Seek', value= 'Begins playing at the specified number of seconds into the song.', inline=False)
            embed.add_field(name='Previous', value= 'Puts the previously played song into the queue. You can add "now" to the end to play the song now.', inline=False)
            embed.add_field(name='Repeat', value= 'Toggles on or off repeating the current queue.', inline=False)
            embed.add_field(name='Shuffle', value= 'Puts the current queue in a random order.', inline=False)
            embed.add_field(name='Volume', value= 'Sets the volume of Realm Tunes to the specified amount.', inline=False)
            embed.add_field(name='Restart', value= 'Begins playing the current song from the beginning.', inline=False)
            embed.add_field(name='Now Playing', value= 'Shows the currently playing song.', inline=False)

            embed.add_field(name='Timescale', value= 'Set the current song to nightcore, slowed, regular, or custom.', inline=False)
            embed.add_field(name='Distortion', value= 'Distort the current song.', inline=False)
            embed.add_field(name='EightD Audio', value= 'Makes the audio sound 8D.', inline=False)
            embed.add_field(name='Bass Boost', value= 'Boosts the bass of the current audio', inline=False)

            await ctx.response.send_message(embed=embed,ephemeral=True)
