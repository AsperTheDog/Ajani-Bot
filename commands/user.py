from disnake import ApplicationCommandInteraction, Member

from ajaniUtils.holdPaginator import HoldMenu
from dbManager import db

from disnake.ext.commands import Cog, slash_command


class UserCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def start(self, inter: ApplicationCommandInteraction):
        new, usr = db.insertUser(inter.user.id)
        if new:
            embed = db.getStartEmbed()
        else:
            embed = db.getUserEmbed(usr, inter.user)
        await inter.response.send_message(embed=embed)

    @slash_command()
    async def user(self, inter, user: Member = None):
        if not user:
            user = inter.user
        usr = db.getUser(user.id)
        if not usr:
            await inter.response.send_message("User not found")
        else:
            await inter.response.send_message(embed=db.getUserEmbed(usr, user))

    @slash_command()
    async def favcard(self, inter, cardid):
        usr = db.getUser(inter.user.id)
        if not usr:
            await inter.response.send_message("User not found")
        else:
            db.changeUserCard(inter.user.id, cardid)
            await inter.response.send_message("Favourite card changed")

    @slash_command()
    async def userstash(self, inter):
        await inter.response.defer()
        info = db.getStash(inter.user.id)
        if len(info) == 0:
            await (await inter.original_message()).edit("This user has no cards yet")
            return
        embed, _ = db.getHoldingCardEmbed(info[0], inter.guild.emojis)
        embed.set_footer(text=f"Card 1 of {len(info)}")
        view = HoldMenu(info, embed)
        view.msg = await inter.original_message()
        await view.msg.edit(embed=embed, view=view)
