import datetime
import math
import random

from disnake import Embed
from disnake.ext.commands import slash_command, Cog

from dbManager import db

jobs = [
    "card sorter",
    "referee in a MTG tournament",
    "somewhat popular youtuber",
    "garbage collector in Python",
    "Cookie Clicker grandma",
    "hunter that hunts monsters",
    "very short psycho in Las Vegas",
    "pretty honest politician",
    "fanfiction writter",
    "freelance NSFW artist",
    "robot-human double spy",
    "hollow-earth apologist"
]


class MoneyCog(Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command()
    async def work(self, inter):
        await inter.response.defer()
        msg = await inter.original_message()
        user = db.getUser(inter.user.id)
        lastDate = datetime.datetime.strptime(user["last_job"].split(".")[0], "%Y-%m-%d %H:%M:%S") if user["last_job"] is not None else datetime.datetime.fromtimestamp(0)
        if (datetime.datetime.utcnow() - lastDate).total_seconds() > 24*60*60:
            money = round((user["job_count"] / (user["job_count"] + 200)) * (100 + (random.random() * 10 - 5) * 5) + 10, 2)
            db.getSalary(inter.user.id, money, True)
            await msg.edit(embed=Embed(
                title="You worked a day as a " + random.choice(jobs),
                description="You got {} :dollar: for a work nicely done".format(money)
            ))
        else:
            timeLeft = (24 * 3600) - (datetime.datetime.utcnow() - lastDate).total_seconds()
            seconds = math.floor(timeLeft % 60)
            minutes = math.floor((timeLeft % 3600) / 60)
            hours = math.floor((timeLeft % 86400) / 3600)
            await msg.edit(embed=Embed(
                title="You can't work yet!!",
                description="Next work opportunity will be in {}h {}m {}s".format(
                    hours,
                    minutes,
                    seconds
                )
            ))
