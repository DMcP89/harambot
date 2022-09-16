import os

import logging
import discord
import requests
import base64
import time
from yahoo_fantasy_api import game
from yahoo_oauth import OAuth2


from discord.ext import commands
from cogs.meta import Meta
from cogs.misc import Misc
from cogs.yahoo import Yahoo
from config import settings
from database.models import Guild
from utils import configure_guild

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('harambot.py')
logger.setLevel(settings.loglevel)

intents = discord.Intents.default()
intents.members = True
intents.messages = True
intents.message_content = True

bot = commands.Bot(command_prefix="$", description="", intents=intents)
bot.remove_command('help')



@bot.event
async def on_ready():
    await bot.add_cog(Meta(bot))
    await bot.add_cog(Yahoo(bot, settings.yahoo_key, settings.yahoo_secret))
    await bot.add_cog(Misc(bot))
    for guild in bot.guilds:
        bot.tree.copy_global_to(guild=guild)
        await bot.tree.sync(guild=guild)
    logger.info("Everything's all ready to go~")

@bot.event
async def on_guild_join(guild):
    logger.info("Joined {}".format(guild.name))
    if not Guild.select().where(Guild.guild_id == str(guild.id)).exists():
        await configure_guild(bot,guild.owner, guild.id)
        logger.info("Guild not configured!")
    
bot.run(settings.discord_token, reconnect=True)  # Where 'TOKEN' is your bot token