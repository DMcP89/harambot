import os

import logging


from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from datastore import GuildsDatastore
from config import settings


#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('harambot.py')
logger.setLevel(settings.loglevel)


bot = commands.Bot(command_prefix="$", description="")
bot.remove_command('help')

@bot.event
async def on_ready():
    logger.info("Everything's all ready to go~")

@bot.event
async def on_guild_join(guild):
    logger.info("Joined {}".format(guild.name))

bot.add_cog(Meta(bot))
bot.add_cog(Misc(bot))

guilds = GuildsDatastore(settings.guilds_datastore_loc)

bot.add_cog(Yahoo(bot, settings.yahoo_key, settings.yahoo_secret, guilds))

bot.run(settings.discord_token, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
