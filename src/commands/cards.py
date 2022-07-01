from disnake.ext.commands import Cog, slash_command


class CardsCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def buy(self, inter, cardSet):
        pass

    @slash_command()
    async def sell(self, inter, card):
        pass