from discord.ext import commands

import discord
import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Misc(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command("RIP")
    async def RIP(self, ctx, *args):
        logger.info("RIP called")
        if args:
            await ctx.send(content="Dicks out for {}".format(args[0]), file=discord.File('static/images/harambe-rip.jpg', filename='harambe-rip.jpg'))
        else:
            await ctx.send(content="Dicks out for Harambe", file=discord.File('static/images/harambe-rip.jpg', filename='harambe-rip.jpg'))
