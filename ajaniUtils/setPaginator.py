# Defines a simple paginator of buttons for the embed.
import disnake

from dbManager import db


class SetMenu(disnake.ui.View):
    def __init__(self, sets: list[dict], extended, initEmbed):
        super().__init__(timeout=30)
        self.msg = None
        self.extended = extended
        self.sets = sets
        self.embed = initEmbed
        self.embed_count = 0

        self.first_page.disabled = True
        self.prev_page.disabled = True
        self.next_page.disabled = 0 == len(self.sets) - 1
        self.last_page.disabled = 0 == len(self.sets) - 1

    async def changeEmbed(self, interaction):
        card = self.sets[self.embed_count]
        self.embed = db.getSetEmbed(card, self.extended)
        self.embed.set_footer(text="Set {} of {}".format(self.embed_count + 1, len(self.sets)))

        self.first_page.disabled = self.embed_count == 0
        self.prev_page.disabled = self.embed_count == 0
        self.next_page.disabled = self.embed_count == len(self.sets) - 1
        self.last_page.disabled = self.embed_count == len(self.sets) - 1
        await interaction.response.edit_message(embed=self.embed, view=self)

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
        self.embed_count = len(self.sets) - 1
        await self.changeEmbed(interaction)

    async def on_timeout(self) -> None:
        await self.msg.edit(view=None)
