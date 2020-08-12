from discord.ext import commands

import discord
import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Meta(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="help")
    async def help(self, ctx):
        embed = discord.Embed(title="Harambot", description="Bot for HML", color=0xeee657)
        embed.add_field(name="$ping", value="Gives the latency of harambot", inline=False)
        embed.add_field(name="$RIP", value="Pay respects to Harambe", inline=False)
        embed.add_field(name="$standings", value="Returns the current standings of HML", inline=False)
        embed.add_field(name="$roster team_name", value="Returns the roster of the given team", inline=False)
        embed.add_field(name="$player_details player_name", value="Returns the details of the given player", inline=False)
        await ctx.send(embed=embed)

    @commands.command(name="ping")
    async def ping(self, ctx):
        logger.info("Ping called")
        latency = self.bot.latency  # Included in the Discord.py library
        await ctx.send(latency)