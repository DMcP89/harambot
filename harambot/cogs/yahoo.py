from discord import embeds
from discord.ext import commands
from yahoo_oauth import OAuth2


import discord
import logging
import urllib3
import yahoo_api



logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


# Decorators

def oauth(func):
    async def setup(cog, ctx, *, content=None):
        league_details = cog.guilds.getGuildDetails(ctx.guild.id)
        cog.yahoo_api = yahoo_api.Yahoo(OAuth2(cog.KEY, cog.SECRET, **league_details), league_details["league_id"])
        if content:
            await func(cog, ctx, content=content)
        else:
            await func(cog, ctx)
    return setup


class Yahoo(commands.Cog):

    error_message = "I'm having trouble getting that right now please try again later"

    def __init__(self, bot, KEY, SECRET, guilds):
        self.bot = bot
        self.http = urllib3.PoolManager()
        self.KEY = KEY
        self.SECRET = SECRET
        self.guilds = guilds
        self.yahoo_api = None
    
    
    @commands.command("standings")
    @oauth
    async def standings(self,ctx):
        logger.info("standings called")
        embed = self.yahoo_api.get_standings()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)

    @commands.command("roster")
    @oauth
    async def roster(self, ctx, *, content:str):
        logger.info("roster called")
        roster = self.yahoo_api.get_roster(content)
        if roster:
            await ctx.send(embed=roster)
        else:
            await ctx.send(self.error_message)
        

    @commands.command("trade")
    @oauth
    async def trade(self, ctx):
        logger.info("trade called")
        
        def check(m):
            return m.author == author


        author = ctx.message.author
        await author.send("Lets wheel & deal")
        await author.send("Who's trading with who? Reply with the manager names in this format: Manager 1, Manager 2")
        managers = await self.bot.wait_for('message', timeout=30, check=check)
        managers = managers.content.split(",")

        await author.send("What players are {} trading? Reply with the player names in this format: Player 1, Player 2".format(managers[0]))
        player_set0 = await self.bot.wait_for('message', timeout=30, check=check)
        player_set0 = player_set0.content.split(",")

        await author.send("What players are {} trading? Reply with the player names in this format: Player 1, Player 2".format(managers[1]))
        player_set1 = await self.bot.wait_for('message', timeout=30, check=check)
        player_set1 = player_set1.content.split(",")

        confirm_trade_message = "{} sends {} to {} for {}".format(managers[0],', '.join(player_set0),managers[1],', '.join(player_set1))
        await author.send("Okay here is what I got: \n{}".format(confirm_trade_message))
        await author.send("is this correct? Reply YES to announce trade")
        confirmation = await self.bot.wait_for('message', timeout=30, check=check)
        confirmation = confirmation.content
        if confirmation.upper() == "YES":
            
            player_set0_details = ""
            for player in player_set0:
                api_details = self.yahoo_api.get_player_details(player.strip())["text"]+"\n"
                if api_details: 
                    player_set0_details = player_set0_details + api_details
                else:
                    await author.send(self.error_message)
                    return


            player_set1_details = ""
            for player in player_set1:
                api_details = self.yahoo_api.get_player_details(player.strip())["text"]+"\n"
                if api_details: 
                    player_set1_details = player_set1_details + api_details
                else:
                    await author.send(self.error_message)
                    return


            announcement = "There's collusion afoot!\n"
            embed = discord.Embed(title="The following trade is up for approval:", description=confirm_trade_message, color=0xeee657)
            embed.add_field(name="{} sends:".format(managers[0]), value=player_set0_details, inline=False)
            embed.add_field(name="to {} for:".format(managers[1]), value=player_set1_details, inline=False)
            embed.add_field(name="Voting", value=" Click :white_check_mark: for yes, :no_entry_sign: for no")
            msg = await ctx.send(content=announcement, embed=embed)    
            yes_emoji = '\U00002705'
            no_emoji = '\U0001F6AB'        
            await msg.add_reaction(yes_emoji)
            await msg.add_reaction(no_emoji)
        else:
            await author.send("Seems like I got something wrong, run the $trade command to start over")


    @commands.command("player_details")
    @oauth
    async def player_details(self, ctx,  *, content:str):
        logger.info("player_details called")
        details = self.yahoo_api.get_player_details(content)
        if details:
            await ctx.send(embed=details['embed'])
        else:
            await ctx.send("Player not found")


    @commands.command("matchups")
    @oauth
    async def matchups(self,ctx):
        embed = self.yahoo_api.get_matchups()
        if embed:
            await ctx.send(embed=embed)
        else:
            await ctx.send(self.error_message)