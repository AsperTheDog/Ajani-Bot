from datetime import datetime

from disnake.ext.commands import Cog, slash_command

from ajaniUtils.paginator import Menu
from ajaniUtils.setPaginator import SetMenu
from dbManager import db, Rarities

argSetTempls = {
    "set": ("code", "="),
    "name": ("name", "LIKE"),
    "after": ("released_at", ">"),
    "before": ("released_at", "<"),
    "size": ("card_count", "="),
    "digital": ("digital", "IS"),
    "nonfoil": ("nonfoil_only", "IS"),
    "foil": ("foil_only", "IS")
}
argTempls = {
    "set": ("set_code", "="),
    "name": ("name", "LIKE"),
    "color": ("colors", "LIKE"),
    "ID": ("id", "="),
    "lang": ("lang", "="),
    "after": ("released_at", ">"),
    "before": ("released_at", "<"),
    "layout": ("layout", "="),
    "hd": ("highres", "IS"),
    "foil": ("foil", "IS"),
    "nonfoil": ("nonfoil", "IS"),
    "etched": ("etched", "IS"),
    "glossy": ("glossy", "IS"),
    "type": ("type_line", "LIKE"),
    "power": ("card_power", "="),
    "toughness": ("toughness", "="),
    "big": ("oversized", "IS"),
    "promo": ("promo", "IS"),
    "reprint": ("reprint", "IS"),
    "variation": ("variation", "IS"),
    "rarity": ("rarity", "="),
    "artist": ("artist", "LIKE"),
    "border": ("border_color", "="),
    "frame": ("frame", "="),
    "full": ("full_art", "IS"),
    "booster": ("booster", "IS"),
}


def parseArgs(args: str, useSet: bool = False):
    global argTempls, argSetTempls
    templToUse = argSetTempls if useSet else argTempls
    parsed = []
    args = args.split("$")
    for arg in args:
        elems = tuple([elem.strip() for elem in arg.split(":", 1)])
        if len(elems) != 2:
            continue
        par, val = elems
        if par in templToUse:
            if par == "rarity":
                val = Rarities[val].value
            if par == "color":
                val = "{}{}{}{}{}".format(
                    "B" if "B" in val else "",
                    "G" if "G" in val else "",
                    "R" if "R" in val else "",
                    "U" if "U" in val else "",
                    "W" if "W" in val else ""
                )
            elif par == "after" or par == "before":
                val = datetime.strptime(val, "%Y-%m-%d")

            if par == "type":
                vals = val.split("-")
                if len(vals) > 1:
                    parsed.append(("type_line", vals[0] + "%", templToUse[par][1]))
                    parsed.append(("type_line", "%" + vals[1], templToUse[par][1]))
                else:
                    parsed.append(("type_line", "%" + vals[0] + "%", templToUse[par][1]))
            else:
                if templToUse[par][1] == "IS":
                    val = val.lower() == "true"
                parsed.append((templToUse[par][0], ("%" + val + "%") if templToUse[par][1] == "LIKE" else val, templToUse[par][1]))
    return parsed


def parseOrderArgs(args: str, useSet: bool = False):
    global argTempls, argSetTempls
    templToUse = argSetTempls if useSet else argTempls
    args = args.split("$")
    parsed = []
    for arg in args:
        if arg in templToUse:
            parsed.append(templToUse[arg][0])
    return parsed


class SearchCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def search(self, inter, ands, ors, order, flags=""):
        await inter.response.defer()
        if "h" in flags:
            await inter.response.send_message("Wiki to do")
            return
        isSet = "s" in flags
        info = db.search(parseArgs(ands, isSet), parseArgs(ors, isSet), (parseOrderArgs(order, isSet), "d" in flags), True, isSet)
        if len(info) == 0:
            await inter.response.send_message("No match was found")
            return
        if "s" not in flags:
            embed = db.getCardEmbed(info[0], inter.guild.emojis, "e" in flags)
            embed.set_footer(text=f"Card 1 of {len(info)}")
            view = Menu(info, "e" in flags, embed)
        else:
            embed = db.getSetEmbed(info[0], "e" in flags)
            embed.set_footer(text=f"Set 1 of {len(info)}")
            view = SetMenu(info, "e" in flags, embed)
        view.msg = await inter.original_message()
        await view.msg.edit(embed=embed, view=view)
