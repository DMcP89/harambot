import os
import json
import yahoo

from discord.ext import commands

dir_path = os.path.dirname(os.path.realpath(__file__))
print('dir_path: '+dir_path)
with open(dir_path+'/harambot.config', 'r') as f:
    config = json.load(f)


bot = commands.Bot(command_prefix="$")
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
    print("standings called")
    await ctx.send(yahoo.get_standings())    

bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token
