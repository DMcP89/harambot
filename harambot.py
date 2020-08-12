import os
import json
import logging

import discord
from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo


#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('harambot.py')
logger.setLevel(logging.INFO)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path+'/harambot.config', 'r') as f:
    config = json.load(f)


bot = commands.Bot(command_prefix="$", description="")
bot.remove_command('help')
TOKEN = config["AUTH"]["TOKEN"]
KEY = config["AUTH"]["CONSUMER_KEY"]
SECRET = config["AUTH"]["CONSUMER_SECRET"]


@bot.event
async def on_ready():
    logger.info("Everything's all ready to go~")

bot.add_cog(Meta(bot))
bot.add_cog(Misc(bot))
bot.add_cog(Yahoo(bot, KEY, SECRET))

bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
