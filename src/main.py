import configparser
import os
import sys

from disnake.ext.commands import InteractionBot

from commands.economy import MoneyCog
from commands.search import SearchCog
from commands.user import UserCog
from dbManager import db

token = ""
ownerID = 0


def configure():
    global token, ownerID
    config = configparser.ConfigParser()
    config.read('config.cfg')
    try:
        token = config["BOT"]["token"]
        ownerID = config["BOT"]["owner"]
    except KeyError:
        config = configparser.ConfigParser()
        config["BOT"] = {
            "token": "TOKEN HERE",
            "owner": 0
        }
        with open("config.cfg", "w") as cfgFile:
            config.write(cfgFile)


client = InteractionBot(
    sync_commands_debug=False,
    test_guilds=[818849848366465025]
)
client.add_cog(SearchCog(client))
client.add_cog(UserCog(client))
client.add_cog(MoneyCog(client))


@client.event
async def on_ready():
    print(f'Logged on as {client.user}!')


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "env":
        token = os.environ['TOKEN']
    else:
        configure()
        client.owner_id = ownerID
    client.run(token)
    db.conClose()
