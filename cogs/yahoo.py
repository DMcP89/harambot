from discord.ext import commands

import discord
import logging
import urllib3
import yahoo_api


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)

class Yahoo(commands.Cog):
    
    def __init__(self, bot, KEY, SECRET):
        self.bot = bot
        self.yahoo_api = yahoo_api.Yahoo(key=KEY, secret=SECRET)
        self.http = urllib3.PoolManager()
    
    @commands.command(name="standings")
    async def standings(self,ctx):
        logger.info("standings called")
        await ctx.send(embed=self.yahoo_api.get_standings())

    @commands.command(name="roster")
    async def roster(self, ctx, *, content:str):
        logger.info("roster called")
        await ctx.send(self.yahoo_api.get_roster(content))

    @commands.command(name="player_details")
    async def player_details(self, ctx,  *, content:str):
        logger.info("player_details called")
        details = self.yahoo_api.get_player_details(content)
        if details:
            response = self.http.request('GET', details['url'])
            image_file = open('player_image.png', 'wb')
            image_file.write(response.data)
            image_file.close
            await ctx.send(content=details['text'], file=discord.File('player_image.png', filename='player_image.png'))
        else:
            await ctx.send("Player not found")