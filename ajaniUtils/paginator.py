# Defines a simple paginator of buttons for the embed.
import disnake
from disnake import HTTPException

from dbManager import db


class Menu(disnake.ui.View):
    def __init__(self, cards: list[dict], extended, initEmbed):
        super().__init__(timeout=30)
        self.msg = None
        self.extended = extended
        self.cards = cards
        self.embed = initEmbed
        self.embed_count = 0

        self.imgs = [cards[0]["png_img"], cards[0]["art_crop"]]
        self.img = self.imgs[0]
        self.isPng = True

        self.blank1.disabled = True
        self.blank2.disabled = True

        self.prev_img.disabled = True
        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = 0 == len(self.cards) - 1
        self.last_page.disabled = 0 == len(self.cards) - 1

    async def changeEmbed(self, interaction):
        card = self.cards[self.embed_count]
        self.embed = db.getCardEmbed(card, interaction.guild.emojis, self.extended)
        self.imgs = [card["png_img"], card["art_crop"]]
        self.img = self.imgs[0] if self.isPng else self.imgs[1]
        self.embed.set_image(url=self.img)
        self.embed.set_footer(text="Card {} of {}".format(self.embed_count + 1, len(self.cards)))

        self.first_page.disabled = self.embed_count == 0
        self.prev_page.disabled = self.embed_count == 0
        self.next_page.disabled = self.embed_count == len(self.cards) - 1
        self.last_page.disabled = self.embed_count == len(self.cards) - 1
        try:
            await interaction.response.edit_message(embed=self.embed, view=self)
        except HTTPException:
            breakpoint()

    async def changeImg(self, interaction):
        self.embed.set_image(url=self.img)

        self.next_img.disabled = not self.isPng
        self.prev_img.disabled = self.isPng
        await interaction.response.edit_message(embed=self.embed, view=self)

    @disnake.ui.button(row=0, label="\u200b")
    async def blank1(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary, row=0)
    async def prev_img(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.img = self.imgs[0]
        self.isPng = True
        await self.changeImg(interaction)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary, row=0)
    async def next_img(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.img = self.imgs[1]
        self.isPng = False
        await self.changeImg(interaction)

    @disnake.ui.button(row=0, label="\u200b")
    async def blank2(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        await interaction.response.defer()

    @disnake.ui.button(emoji="⏪", style=disnake.ButtonStyle.blurple, row=1)
    async def first_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = 0
        await self.changeEmbed(interaction)

    @disnake.ui.button(emoji="◀", style=disnake.ButtonStyle.secondary, row=1)
    async def prev_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count -= 1
        await self.changeEmbed(interaction)

    @disnake.ui.button(emoji="▶", style=disnake.ButtonStyle.secondary, row=1)
    async def next_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count += 1
        await self.changeEmbed(interaction)

    @disnake.ui.button(emoji="⏩", style=disnake.ButtonStyle.blurple, row=1)
    async def last_page(self, button: disnake.ui.Button, interaction: disnake.MessageInteraction):
        self.embed_count = len(self.cards) - 1
        await self.changeEmbed(interaction)

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)
