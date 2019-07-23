from discord.ext import commands
bot = commands.Bot(command_prefix="$")
TOKEN = "NjAzMDA5MzU4MDAzMTc1NDI0.XTZLEQ.e4Ja7S9d5f6aQGSDkU9yvVLh6rE"

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


bot.run(TOKEN, bot=True, reconnect=True)  # Where 'TOKEN' is your bot token