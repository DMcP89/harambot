from discord.ext import commands


import discord
import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Misc(commands.Cog):
    
    def __init__(self, bot, guilds):
        self.bot = bot
        self.guilds = guilds

    @commands.command("RIP")
    async def RIP(self, ctx, *args):
        logger.info("RIP called")
        league_details = self.guilds.getGuildDetails(ctx.guild.id)
        respected = args[0] if args else "Harambe"
        message = league_details["RIP_text"] +" "+ respected
        embed = discord.Embed(title="", description='', color=0xeee657)
        embed.set_image(url=league_details["RIP_image_url"])
        
        await ctx.send(content=message,embed=embed)
