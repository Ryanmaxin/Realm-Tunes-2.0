

async def sendDM(self, func, error):
        user = await self.bot.fetch_user(404491098946273280)
        message = f"Error in: {func}: \n {error}"
        await user.send(message)
