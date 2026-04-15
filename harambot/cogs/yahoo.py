import discord
import logging
import json
import functools

from discord.ext import commands
from discord import app_commands
from typing import List, Optional
from datetime import datetime, timedelta

from harambot.yahoo_api import Yahoo
from harambot.database.models import Guild
from harambot import utils

logger = logging.getLogger("discord.harambot.cogs.yahoo")

yahoo_api = Yahoo()

handlers = {
        "yahoo": Yahoo(),
}


class YahooCog(commands.Cog):

    error_message = (
        "I'm having trouble getting that right now please try again later"
    )
    
    api_handler = None

    def __init__(self, bot):
        self.bot = bot

            
    def api_handler_check(f):
        @functools.wraps(f)
        async def wrapper(self, interaction: discord.Interaction, *args, **kwargs):
            logger.info("Setting api handler")
            guild = Guild.get_or_none(Guild.guild_id == str(interaction.guild_id))
            if guild is None:
                logger.error("Guild %i not found in database", interaction.guild_id)
                await interaction.response.send_message(
                    "Guild not found in database"
                )
                return
            handler = handlers.get(guild.league_provider)
            if handler:
                self.api_handler = handler
                logger.info("Set api handler to %s for guild %i", guild.league_provider, interaction.guild_id)
                logger.info ("API Handler: %s", self.api_handler)
                await f(self, interaction, *args, **kwargs)
            else:
                logger.error("No handler found for league provider %s in guild %i", guild.league_provider, interaction.guild_id)
                await interaction.response.send_message(
                    "League provider not supported"
                )
        return wrapper


    @app_commands.command(
        name="standings",
        description="Returns the current standings of your league",
    )
    @api_handler_check
    async def standings(self, interaction: discord.Interaction):
        logger.info("Command:Standings called in %i", interaction.guild_id)
        await interaction.response.defer()
        description, standings = self.api_handler.get_standings(guild_id=interaction.guild_id)
        if standings:
            embed = discord.Embed(
                    title="Standings",
                    description=description,
                    color=0xEEE657,
                    )
            for team in standings:
                embed.add_field(
                    name=team["place"],
                    value=team["record"],
                    inline=False,
                )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(self.error_message)

    async def roster_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        teams = yahoo_api.get_teams(guild_id=interaction.guild_id)
        if teams:
            options = list(
                map(
                    lambda x: app_commands.Choice(
                        name=teams[x]["name"], value=teams[x]["name"]
                    ),
                    teams,
                )
            )
            return options
        return []

    async def check_roster_available(interaction: discord.Interaction):
        return yahoo_api.roster_check(guild_id=interaction.guild_id)

    @app_commands.command(
        name="roster", description="Returns the roster of the given team"
    )
    @app_commands.check(check_roster_available)
    @app_commands.autocomplete(team_name=roster_autocomplete)
    async def roster(self, interaction: discord.Interaction, team_name: str):
        logger.info(
            "Command:Roster called in %i with team_name:%s",
            interaction.guild_id,
            team_name,
        )
        await interaction.response.defer()
        roster = yahoo_api.get_roster(
            guild_id=interaction.guild_id, team_name=team_name
        )
        if roster:
            embed = discord.Embed(
                    title="{}'s Roster".format(team_name),
                    description="",
                    color=0xEEE657,
                    )
            for player in roster:
                if len(roster) > 25 and player["selected_position"] in ["IR", "IL"]:
                    continue
                embed.add_field(
                    name=player["selected_position"],
                    value=player["name"],
                    inline=False,
                )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(self.error_message)
    
    @roster.error
    async def roster_check_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Rosters not available yet"
            )
    
    def check_trade_ratification(interaction: discord.Interaction):
        return yahoo_api.trade_check(guild_id=interaction.guild_id)

    @app_commands.command(
        name="trade",
        description="Create poll for latest trade for league approval",
    )
    @app_commands.check(check_trade_ratification)
    async def trade(self, interaction: discord.Interaction):
        logger.info("Command:Trade called in %i", interaction.guild_id)
        await interaction.response.defer()
        latest_trade = yahoo_api.get_latest_trade(
            guild_id=interaction.guild_id
        )
        if latest_trade is None:
            await interaction.followup.send(
                "No trades up for approval at this time"
            )
            return
        trade_poll = discord.Poll(
                question="The following trade is up for approval:{}".format(latest_trade),
                duration=timedelta(hours=24),
                )
        trade_poll.add_answer(text="Yes")
        trade_poll.add_answer(text="No")

        await interaction.followup.send(poll=trade_poll)

    @trade.error
    async def trade_check_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Trade command only available for leagues with vote or commissioner ratification"
            )

    async def stats_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        players = yahoo_api.get_players(
            current, guild_id=interaction.guild_id
        )
        if players:
            options = list(
                map(
                    lambda x: app_commands.Choice(
                        name=x["name"]["full"],
                        value=x["name"]["full"],
                    ),
                    players,
                )
            )
        else:
            options = []
        return options

    @app_commands.command(
        name="stats", description="Returns the details of the given player"
    )
    @app_commands.autocomplete(player_name=stats_autocomplete)
    async def stats(
        self,
        interaction: discord.Interaction,
        player_name: str,
        week: Optional[int] = None,
    ):
        logger.info(
            "Command:Stats called in %i with player_name:%s",
            interaction.guild_id,
            player_name,
        )
        await interaction.response.defer()
        player = yahoo_api.get_player_details(
            player_name, guild_id=interaction.guild_id, week=week
        )
        if player:
            embed = utils.get_player_embed(player)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Player not found")

    async def check_matchups_available(interaction: discord.Interaction):
        return yahoo_api.matchups_check(guild_id=interaction.guild_id)

    @app_commands.command(
        name="matchups", description="Returns the current weeks matchups"
    )
    @app_commands.check(check_matchups_available)
    async def matchups(
        self, interaction: discord.Interaction, week: Optional[int] = None
    ):
        logger.info(
            "Command:Matchups called in {} with week: {}".format(
                interaction.guild_id, week
            )
        )
        await interaction.response.defer()
        matchups = yahoo_api.get_matchups(
            guild_id=interaction.guild_id, week=week
        )
        if matchups: 
            embed = utils.get_matchups_embed(week, matchups)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(self.error_message)

    @matchups.error
    async def matchups_check_error(self, interaction: discord.Interaction, error):
        if isinstance(error, app_commands.CheckFailure):
            await interaction.response.send_message(
                "Matchups not available yet"
            )


    @app_commands.command(
        name="waivers",
        description="Returns the waiver transactions from the last 24 hours",
    )
    async def waivers(self, interaction: discord.Interaction, days: int = 1):
        logger.info("Command:Waivers called in %i", interaction.guild_id)
        await interaction.response.defer()
        ts = datetime.now() - timedelta(days=days)
        transactions = yahoo_api.get_transactions(
            guild_id=interaction.guild_id, timestamp=ts.timestamp()
        )
        if transactions:
            embed_functions_dict = {
                "add/drop": utils.create_add_drop_embed,
                "add": utils.create_add_embed,
                "drop": utils.create_drop_embed,
            }
            for transaction in transactions:
                await interaction.followup.send(
                    embed=embed_functions_dict[transaction["type"]](
                        transaction
                    )
                )
        else:
            await interaction.followup.send("No transactions found")
