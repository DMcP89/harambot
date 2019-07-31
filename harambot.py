import os
import json
import yahoo
import logging

from discord.ext import commands

logging.basicConfig(level=logging.INFO)

dir_path = os.path.dirname(os.path.realpath(__file__))
print('dir_path: '+dir_path)
with open(dir_path+'/harambot.config', 'r') as f:
    config = json.load(f)


bot = commands.Bot(command_prefix="$")
TOKEN = config["AUTH"]["TOKEN"]

@bot.event
async def on_ready():
    print("Everything's all ready to go~")
    print("League Id: "+ str(yahoo.league_id))


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


@bot.command()
async def echo(ctx, *, content:str):
    await ctx.send(content)


@bot.command(name="sayHello")
async def say_hello(ctx):
    print("sayHello called")
    await ctx.send("Hello")


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
async def standings(ctx,  *, content:str):
    yahoo.refresh_access_token()
    print("player_details called")
    details = yahoo.get_player_details(content)
    await ctx.send(content=details['text'] + '\n' + details['url'])  

bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
