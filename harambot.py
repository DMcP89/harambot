import os
import json
import yahoo
import logging
import urllib3

import discord
from discord.ext import commands

#logging.basicConfig(level=logging.INFO)
logger = logger = logging.getLogger()
logger.setLevel(logging.INFO)

dir_path = os.path.dirname(os.path.realpath(__file__))
print('dir_path: '+dir_path)
with open(dir_path+'/harambot.config', 'r') as f:
    config = json.load(f)


http = urllib3.PoolManager()

bot = commands.Bot(command_prefix="$", description="")
TOKEN = config["AUTH"]["TOKEN"]

@bot.event
async def on_ready():
    print("Everything's all ready to go~")


@bot.command()
async def ping(ctx):
    '''
    This text will be shown in the help command
    '''
    print("Ping called")
    # Get the latency of the bot
    latency = bot.latency  # Included in the Discord.py library
    # Send it to the user
    await ctx.send(latency)

@bot.command(name="saydicksoutRIP")
async def say_hello(ctx):
    print("saydicksoutRIP called")
    await ctx.send("Dicks out for Harambe")

@bot.command(name="standings")
async def standings(ctx):
    yahoo.refresh_access_token()
    print("standings called")
    await ctx.send(yahoo.get_standings())

@bot.command(name="player_details")
async def player_details(ctx,  *, content:str):
    yahoo.refresh_access_token()
    print("player_details called")
    details = yahoo.get_player_details(content)
    response = http.request('GET', details['url'])
    image_file = open('player_image.png', 'wb')
    image_file.write(response.data)
    image_file.close
    await ctx.send(content=details['text'], file=discord.File('player_image.png', filename='player_image.png'))

yahoo.refresh_access_token()
bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
