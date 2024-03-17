import logging
import sys
import traceback

import discord
from discord.ext import commands

from helpers import sendDM


class ExceptionHandler(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        bot.tree.error(coro = self.__dispatch_to_app_command_handler)

    async def __dispatch_to_app_command_handler(self, interaction: discord.Interaction, error: discord.app_commands.AppCommandError):
        self.bot.dispatch("app_command_error", interaction, error)

    @commands.Cog.listener("on_app_command_error")
    async def get_app_command_error(self, ctx: discord.Interaction, error: discord.app_commands.AppCommandError):
        if isinstance(error, commands.CommandNotFound):
            await ctx.response.send_message("That command does not exist. Use -help for list of all available commands")
            return
        else:
            command_name = ctx.command.name

            embed = discord.Embed(title=f"Something went wrong with {command_name}", color=discord.Color.red())
            await ctx.response.send_message(embed=embed)

            error_type = type(error)
            error_traceback = error.__traceback__

            print(command_name,error)
            print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
            traceback.print_exception(error_type, error, error_traceback, file=sys.stderr)

            exc_info = (error_type, error, error_traceback)
            logger = logging.getLogger()
            logger.error('Exception occurred', exc_info=exc_info)

            await sendDM(self,command_name,error)
            return
        
    # @commands.Cog.listener()
    # async def on_command_error(self,ctx,error):
    #     print("ERROR1!!!")
    #     if isinstance(error, commands.CommandNotFound):
    #         await ctx.response.send_message("That command does not exist. Use -help for list of all available commands")
    #         return
    #     else:
    #         command_name = ctx.invoked_with

    #         embed = discord.Embed(title=f"Something went wrong with {command_name}", color=Color.red())
    #         await ctx.response.send_message(embed=embed)

    #         error_type = type(error)
    #         error_traceback = error.__traceback__

    #         print(command_name,error)
    #         print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
    #         traceback.print_exception(error_type, error, error_traceback, file=sys.stderr)

    #         exc_info = (error_type, error, error_traceback)
    #         logger = logging.getLogger()
    #         logger.error('Exception occurred', exc_info=exc_info)

    #         await sendDM(self,command_name,error)
    #         return

