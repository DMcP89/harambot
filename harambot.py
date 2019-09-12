import os
import json
import yahoo
import logging
import urllib3

import discord
from discord.ext import commands


#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('harambot.py')
logger.setLevel(logging.INFO)

dir_path = os.path.dirname(os.path.realpath(__file__))
with open(dir_path+'/harambot.config', 'r') as f:
    config = json.load(f)


http = urllib3.PoolManager()

bot = commands.Bot(command_prefix="$", description="")
bot.remove_command('help')
TOKEN = config["AUTH"]["TOKEN"]
KEY = config["AUTH"]["CONSUMER_KEY"]
SECRET = config["AUTH"]["CONSUMER_SECRET"]

yahoo_api = yahoo.Yahoo(key=KEY, secret=SECRET)

@bot.event
async def on_ready():
    logger.info("Everything's all ready to go~")


@bot.command()
async def ping(ctx):
    logger.info("Ping called")
    latency = bot.latency  # Included in the Discord.py library
    await ctx.send(latency)

@bot.command(name="RIP")
async def RIP(ctx, *args):
    logger.info("RIP called")
    if args:
        await ctx.send(content="Dicks out for {}".format(args[0]), file=discord.File('harambe-rip.jpg', filename='harambe-rip.jpg'))
    else:
        await ctx.send(content="Dicks out for Harambe", file=discord.File('harambe-rip.jpg', filename='harambe-rip.jpg'))

@bot.command(name="standings")
async def standings(ctx):
    logger.info("standings called")
    await ctx.send(yahoo_api.get_standings())

@bot.command(name="roster")
async def roster(ctx, *, content:str):
    logger.info("roster called")
    await ctx.send(yahoo_api.get_roster(content))

@bot.command(name="player_details")
async def player_details(ctx,  *, content:str):
    logger.info("player_details called")
    details = yahoo_api.get_player_details(content)
    response = http.request('GET', details['url'])
    image_file = open('player_image.png', 'wb')
    image_file.write(response.data)
    image_file.close
    await ctx.send(content=details['text'], file=discord.File('player_image.png', filename='player_image.png'))

@bot.command()
async def help(ctx):
    embed = discord.Embed(title="Harambot", description="Bot for HML", color=0xeee657)
    embed.add_field(name="$ping", value="Gives the latency of harambot", inline=False)
    embed.add_field(name="$RIP", value="Pay respects to Harambe", inline=False)
    embed.add_field(name="$standings", value="Returns the current standings of HML", inline=False)
    embed.add_field(name="$roster team_name", value="Returns the roster of the given team", inline=False)
    embed.add_field(name="$player_details player_name", value="Returns the details of the given player", inline=False)
    await ctx.send(embed=embed)

bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
