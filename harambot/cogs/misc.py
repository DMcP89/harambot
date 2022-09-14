from discord.ext import commands


import discord
import logging

from models.models import Guild

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Misc(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command("RIP")
    async def RIP(self, ctx, *args):
        logger.info("RIP called")
        guild = Guild.get(Guild.guild_id == str(ctx.guild.id))
        respected = args[0] if args else "Harambe"
        message = guild.RIP_text +" "+ respected
        embed = discord.Embed(title="", description='', color=0xeee657)
        embed.set_image(url=guild.RIP_image_url)
        
        await ctx.send(content=message,embed=embed)
