# import discord

# from cogs.music import Music


# class ButtonView(discord.ui.View): # Create a class called MyView that subclasses discord.ui.View
#     def __init__(self,query):
#         # body of the constructor
#         self.query = query
#     @discord.ui.button(label="Search on Youtube Music instead", style=discord.ButtonStyle.red) # Create a button with the label "😎 Click me!" with color Blurple
#     async def button_callback(self, interaction, button):
#         Music.chooseSong(interaction, self.query,)
#         await interaction.response.send_message("You clicked the button!") # Send a message when the button is clicked
