from discord.ext import commands

import discord
import logging

logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Meta(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot

    @commands.command("help")
    async def help(self, ctx):
        embed = discord.Embed(title="Harambot", description="Yahoo Fantasy Sports Bot for Discord", color=0xeee657)
        embed.add_field(name="$ping", value="Gives the latency of harambot", inline=False)
        embed.add_field(name="$RIP", value="Pay respects to Harambe", inline=False)
        embed.add_field(name="$standings", value="Returns the current standings of your league", inline=False)
        embed.add_field(name="$roster team_name", value="Returns the roster of the given team", inline=False)
        embed.add_field(name="$player_details player_name", value="Returns the details of the given player", inline=False)
        embed.add_field(name="$trade", value="Propose a trade for league approval", inline=False)
        embed.add_field(name="$matchups", value="Returns the current weeks matchups", inline=False)
        await ctx.send(embed=embed)

    @commands.command("ping")
    async def ping(self, ctx):
        logger.info("Ping called")
        latency = self.bot.latency  # Included in the Discord.py library
        await ctx.send(latency)