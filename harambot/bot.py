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

#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('harambot.py')
logger.setLevel(settings.loglevel)

intents = discord.Intents.default()
intents.members = True

bot = commands.Bot(command_prefix="$", description="", intents=intents)
bot.remove_command('help')



@bot.event
async def on_ready():
    logger.info("Everything's all ready to go~")

@bot.event
async def on_guild_join(guild):
    logger.info("Joined {}".format(guild.name))
    if not Guild.select().where(Guild.guild_id == str(guild.id)).exists():
        await configure_guild(guild.owner, guild.id)
        logger.info("Guild not configured!")
    

async def configure_guild(owner, id):

    def check(m):
        return m.author == owner

    await owner.send("Thank you for adding Harambot to your server!")
    await owner.send("Please open the following link to authorize with Yahoo, respond with the code given after authorization")
    await owner.send("https://api.login.yahoo.com/oauth2/request_auth?redirect_uri=oob&response_type=code&client_id={}".format(settings.yahoo_key))
    code = await bot.wait_for('message', timeout=60, check=check)
    encoded_creds = base64.b64encode(('{0}:{1}'.format(settings.yahoo_key, settings.yahoo_secret )).encode('utf-8'))
    details = requests.post(
        url='https://api.login.yahoo.com/oauth2/get_token',
        data={"code": code.clean_content, 'redirect_uri': 'oob', 'grant_type': 'authorization_code'},
        headers = {
            'Authorization': 'Basic {0}'.format(encoded_creds.decode('utf-8')),
            'Content-Type': 'application/x-www-form-urlencoded'
        }
    ).json()
    details['token_time'] = time.time()
    await owner.send("Enter Yahoo League ID")
    leauge_id = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter Yahoo League Type(nfl, nhl, nba, mlb)")
    leauge_type = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter text to use with $RIP command")
    RIP_text = await bot.wait_for('message', timeout=60, check=check)
    await owner.send("Enter image url to use with $RIP command")
    RIP_image_url = await bot.wait_for('message', timeout=60, check=check)
    details["league_id"] = leauge_id.clean_content
    details["league_type"] = leauge_type.clean_content
    details["RIP_text"] = RIP_text.clean_content
    details["RIP_image_url"] = RIP_image_url.clean_content
    Guild.create(guild_id=id,**details)
    return

bot.add_cog(Meta(bot))
bot.add_cog(Yahoo(bot, settings.yahoo_key, settings.yahoo_secret))
bot.add_cog(Misc(bot))

bot.run(settings.discord_token, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token