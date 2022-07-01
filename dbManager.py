import datetime
import sqlite3
from enum import Enum

from disnake import Embed, Emoji, User


class Rarities(Enum):
    common = 0
    uncommon = 1
    rare = 2
    mythic = 3
    special = 4
    bonus = 5


def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
        if col[0] == "rarity":
            d[col[0]] = Rarities(d[col[0]]).name
    return d


class DbManager:
    def __init__(self):
        self.dbName = 'magic.sqlite'
        self.con = sqlite3.connect(self.dbName)
        self.con.row_factory = dict_factory

    def conClose(self):
        self.con.close()

    def search(self, ands, ors, order, hasImage, searchSet):
        cur = self.con.cursor()
        where = []
        if len(ands) > 0:
            where.append("(" + " AND ".join([param + " {} ?".format(op) for param, _, op in ands]) + ")")
        if len(ors) > 0:
            where.append("(" + " OR ".join([param + " {} ?".format(op) for param, _, op in ors]) + ")")
        query = """SELECT * FROM {}""".format("cards" if not searchSet else "sets")
        if len(where) > 0:
            query += """ WHERE {}""".format(where[0])
            if len(where) > 1:
                query += """ AND {}""".format(where[1])
            if hasImage and not searchSet:
                query += """ AND png_img IS NOT NULL"""
        else:
            if hasImage and not searchSet:
                query += """ WHERE png_img IS NOT NULL"""
        if len(order[0]) != 0:
            order = [data + (" DESC" if order[1] else " ASC") for data in order[0]]
            query += " ORDER BY " + ", ".join(order)
        cur.execute(query, tuple([param for _, param, _ in ands] + [param for _, param, _ in ors]))
        data = cur.fetchall()

        self.con.commit()
        return data

    def getSet(self, setCode):
        cur = self.con.cursor()

        cur.execute('''SELECT * FROM sets WHERE code = ?''', (setCode,))

        data = cur.fetchone()
        self.con.commit()
        return data

    def getUser(self, userID):
        cur = self.con.cursor()

        cur.execute('''SELECT * FROM users WHERE id = ?''', (userID,))

        data = cur.fetchone()
        self.con.commit()
        return data

    def getStash(self, userID):
        cur = self.con.cursor()

        cur.execute('''SELECT * FROM holdings WHERE user = ?''', (userID,))

        data = cur.fetchall()
        self.con.commit()
        return data

    def getCompletionRates(self, user):
        cur = self.con.cursor()
        types = {"nonfoil": 0, "foil": 0, "etched": 0, "glossy": 0}
        for finish in types:
            cur.execute('''SELECT ((stash / CAST(cardNum AS FLOAT)) * 100) as perc FROM
                             (SELECT COUNT(*) as cardNum FROM cards WHERE {} IS TRUE),
                             (SELECT COUNT(*) as stash FROM holdings WHERE type = ? AND user = ?)'''.format(finish), (finish, user))
            types[finish] = cur.fetchone()["perc"]
        self.con.commit()
        return types

    def insertUser(self, userID):
        cur = self.con.cursor()

        cur.execute('''SELECT * FROM users WHERE id = ?''', (userID,))

        data = cur.fetchone()
        if data:
            self.con.commit()
            return False, data

        cur.execute('''INSERT OR IGNORE INTO users(id) VALUES (?)''', (userID,))
        cur.execute('''SELECT * FROM users WHERE id = ?''', (userID,))
        data = cur.fetchone()
        self.con.commit()
        return True, data

    def changeUserCard(self, userID, cardID):
        cur = self.con.cursor()

        cur.execute('''SELECT * FROM holdings WHERE user = ? AND card = ?''', (userID, cardID))
        cur.execute('''UPDATE users SET selectedCard = ? WHERE id = ?''', (cardID if cur.fetchone() else None, userID))

        self.con.commit()

    def getSalary(self, user, money, isJob):
        cur = self.con.cursor()
        cur.execute('''UPDATE users SET money = money + ? WHERE id = ?''', (money, user))
        if isJob:
            cur.execute('''UPDATE users SET job_count = job_count + 1, last_job = ? WHERE id = ?''', (datetime.datetime.utcnow(), user))
        self.con.commit()

    def getCardEmbed(self, cardInfo, emojis: list[Emoji], extended=False):
        setData = self.getSet(cardInfo["set_code"])
        emoj = str([emoji for emoji in emojis if emoji.name == "mythic"][0])
        for emoji in emojis:
            emoj = str(emoji) if emoji.name == cardInfo["rarity"] else emoj
        if not extended:
            descr = "Rarity: {}\nSet: {}\nID: {}".format(
                emoj + cardInfo["rarity"] + emoj,
                setData["code"].upper(),
                "*" + cardInfo["id"] + "*"
            )
        else:
            descr = "Rarity: {}\nSet: {} ({})\nID: {}\nIllustration ID: {}\nRelease date: {}\nLang: {}\nColor: {}\nTags: {}\n\n".format(
                emoj + cardInfo["rarity"] + emoj,
                setData["code"].upper(),
                setData["name"],
                "*" + cardInfo["id"] + "*",
                "*" + cardInfo["illust_id"] + "*",
                cardInfo["released_at"],
                cardInfo["lang"],
                cardInfo["colors"],
                ", ".join(filter(lambda x: x is not None, [
                    "HD" if cardInfo["highres_image"] else None,
                    "foil" if cardInfo["foil"] else None,
                    "no foil" if cardInfo["nonfoil"] else None,
                    "oversized" if cardInfo["oversized"] else None,
                    "promotion" if cardInfo["promo"] else None,
                    "reprint" if cardInfo["reprint"] else None,
                    "variation" if cardInfo["variation"] else None,
                    "full art" if cardInfo["full_art"] else None,
                    "textless" if cardInfo["textless"] else None,
                    "booster" if cardInfo["booster"] else None,
                    "story spotlight" if cardInfo["story_spotlight"] else None,
                ]))
            )
            if cardInfo["nonfoil"]:
                descr += "Normal price: *{}$*\n".format(cardInfo["nonfoil_price"] if cardInfo["nonfoil_price"] is not None else "untradeable")
            if cardInfo["foil"]:
                descr += "Foil price: *{}$*\n".format(cardInfo["foil_price"] if cardInfo["foil_price"] is not None else "untradeable")
            if cardInfo["etched"]:
                descr += "Etched price: *{}$*\n".format(cardInfo["etched_price"] if cardInfo["etched_price"] is not None else "untradeable")
        embed = Embed(title=cardInfo["name"], description=descr)
        if cardInfo["gatherer"]:
            embed.url = cardInfo["gatherer"]
        embed.set_author(name=cardInfo["artist"])
        embed.set_image(url=cardInfo["png_img"])
        return embed

    def getHoldingCardEmbed(self, holdingInfo, emojis: list[Emoji]):
        cardInfo = self.search([("id", holdingInfo["card"], "=")], [], True, False)[0]
        setData = self.getSet(cardInfo["set_code"])
        emoj = str([emoji for emoji in emojis if emoji.name == "mythic"][0])
        for emoji in emojis:
            emoj = str(emoji) if emoji.name == cardInfo["rarity"] else emoj
        descr = "Rarity: {}\nSet: {}\nID: *{}*\nType: *{}*\n\n".format(
            emoj + cardInfo["rarity"] + emoj,
            setData["code"].upper(),
            cardInfo["id"],
            "normal" if holdingInfo["type"] == "nonfoil" else holdingInfo["type"]
        )

        if cardInfo.get(holdingInfo["type"] + "_price") is not None:
            descr += "Price: *{}*\n\n".format(str(cardInfo.get(holdingInfo["type"] + "_price")) + " :dollar:")
        else:
            descr += "Price: *untradeable*\n\n"

        descr += "You have: {}\n".format(holdingInfo["count"])
        if cardInfo.get(holdingInfo["type"] + "_price") is not None:
            descr += "Total value: {} :dollar:\nAuctioning: {}\n".format(cardInfo.get(holdingInfo["type"] + "_price") * holdingInfo["count"], holdingInfo["auctioned"])
        embed = Embed(title=cardInfo["name"], description=descr)
        if cardInfo["gatherer"]:
            embed.url = cardInfo["gatherer"]
        embed.set_author(name=cardInfo["artist"])
        embed.set_image(url=cardInfo["png_img"])
        return embed, [cardInfo["png_img"], cardInfo["art_crop"]]

    def getSetEmbed(self, setInfo, extended=False):
        if not extended:
            descr = "Size: {} cards\nRelease date: {}".format(
                setInfo["card_count"],
                setInfo["released_at"],
            )
        else:
            descr = "Size: {} cards\nRelease date: {}\nTags: {}".format(
                setInfo["card_count"],
                setInfo["released_at"],
                ", ".join(filter(lambda x: x is not None, [
                    "foil only" if setInfo["foil_only"] else None,
                    "non foil only" if setInfo["nonfoil_only"] else None,
                    "digital" if setInfo["digital"] else None
                ]))
            )
        embed = Embed(title=setInfo["name"], description=descr)
        embed.set_author(name=setInfo["code"].upper())
        return embed

    def getUserEmbed(self, user, discAccount: User):
        cards = db.getStash(user["id"])
        rates = db.getCompletionRates(user["id"])
        descr = "Level: {}\nExp: {}\nMoney: {}:dollar:\nJob level: {}\nTournament level: {}\nShash size: {} cards\n\nNormal MagicDex: {}\nFoil MagicDex: {}\nEtched MagicDex: {}\nGlossy MagicDex: {}".format(
            user["level"],
            user["exp"],
            user["money"],
            user["job_count"],
            user["tournament_level"],
            len(cards),
            str(round(rates["nonfoil"], 4)) + ("% :star:" if rates["nonfoil"] == 100 else "%"),
            str(round(rates["foil"], 4)) + ("% :star:" if rates["foil"] == 100 else "%"),
            str(round(rates["etched"], 4)) + ("% :star:" if rates["etched"] == 100 else "%"),
            str(round(rates["glossy"], 4)) + ("% :star:" if rates["glossy"] == 100 else "%")
        )
        embed = Embed(title=discAccount.display_name + " ({}#{})".format(discAccount.name, discAccount.discriminator), description=descr)
        embed.set_author(name=str(discAccount.id))
        if user["selectedCard"] is not None:
            card = db.search([("id", user["selectedCard"], "=")], [], True, False)
            embed.set_thumbnail(url=card[0]["art_crop"])
        else:
            embed.set_thumbnail(url=discAccount.display_avatar.url)
        return embed

    def getStartEmbed(self):
        descr = "Insert welcome info here"
        embed = Embed(title="Welcome, plainswalker", description=descr)
        embed.set_thumbnail(url="https://images.pling.com/img/00/00/11/74/84/1108370/104822-1.png")
        return embed


db = DbManager()
