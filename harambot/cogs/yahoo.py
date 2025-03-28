import discord
import logging
import json

from discord.ext import commands
from discord import app_commands
from typing import List, Optional
from datetime import datetime, timedelta

from harambot.yahoo_api import Yahoo
from harambot import utils

logging.setLoggerClass(logging.Logger)
logging.getLogger("yahoo_oauth").setLevel("INFO")

logger = logging.getLogger("discord.harambot.cogs.yahoo")


class YahooCog(commands.Cog):

    error_message = (
        "I'm having trouble getting that right now please try again later"
    )

    def __init__(self, bot, KEY, SECRET):
        self.bot = bot
        self.KEY = KEY
        self.SECRET = SECRET
        self.yahoo_api = Yahoo()

    @app_commands.command(
        name="standings",
        description="Returns the current standings of your league",
    )
    async def standings(self, interaction: discord.Interaction):
        logger.info("Command:Standings called in %i", interaction.guild_id)
        await interaction.response.defer()
        scoring_type = self.yahoo_api.get_settings(guild_id=interaction.guild_id)["scoring_type"]
        embed = discord.Embed(
            title="Standings",
            description="W-L-T" if scoring_type == "head" else "Team \nPoints For - Points Change",
            color=0xEEE657,
        )
        standings = self.yahoo_api.get_standings(guild_id=interaction.guild_id)
        if standings:
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
        teams = self.yahoo_api.get_teams(guild_id=interaction.guild_id)
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

    @app_commands.command(
        name="roster", description="Returns the roster of the given team"
    )
    @app_commands.autocomplete(team_name=roster_autocomplete)
    async def roster(self, interaction: discord.Interaction, team_name: str):
        logger.info(
            "Command:Roster called in %i with team_name:%s",
            interaction.guild_id,
            team_name,
        )
        await interaction.response.defer()
        embed = discord.Embed(
            title="{}'s Roster".format(team_name),
            description="",
            color=0xEEE657,
        )
        settings = self.yahoo_api.get_settings(guild_id=interaction.guild_id)
        if "draft_status" in settings and settings["draft_status"] == "predraft":
            await interaction.followup.send("Rosters not available yet")
            return
        roster = self.yahoo_api.get_roster(
            guild_id=interaction.guild_id, team_name=team_name
        )
        if roster:
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
    

    @app_commands.command(
        name="trade",
        description="Create poll for latest trade for league approval",
    )
    async def trade(self, interaction: discord.Interaction):
        logger.info("Command:Trade called in %i", interaction.guild_id)
        await interaction.response.defer()
        if (
            self.yahoo_api.get_settings(guild_id=interaction.guild_id)[
                "trade_ratify_type"
            ]
            == "none"
        ):
            await interaction.followup.send(
                "Trade command only available for leagues with vote or commissioner ratification"
            )
            return
        latest_trade = self.yahoo_api.get_latest_trade(
            guild_id=interaction.guild_id
        )
        if latest_trade is None:
            await interaction.followup.send(
                "No trades up for approval at this time"
            )
            return

        trader = self.yahoo_api.league().to_team(latest_trade["trader_team_key"]).details()["name"]
        tradee = self.yahoo_api.league().to_team(latest_trade["tradee_team_key"]).details()["name"]

        trader_player_names = []
        for player in latest_trade["trader_players"]:
            if player:
                trader_player_names.append(player["name"])

        tradee_player_names = []
        for player in latest_trade["tradee_players"]:
            tradee_player_names.append(player["name"])

        confirm_trade_message = "\n{} sends {} to {} for {}".format(
            trader,
            ", ".join(trader_player_names),
            tradee,
            ", ".join(tradee_player_names),
        )
        trade_poll = discord.Poll(
                question="The following trade is up for approval:{}".format(confirm_trade_message),
                duration=timedelta(hours=24),
                )
        trade_poll.add_answer(text="Yes")
        trade_poll.add_answer(text="No")

        await interaction.followup.send(poll=trade_poll)
        
    async def stats_autocomplete(
        self,
        interaction: discord.Interaction,
        current: str,
    ) -> List[app_commands.Choice[str]]:
        players = self.yahoo_api.get_players(
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
        player = self.yahoo_api.get_player_details(
            player_name, guild_id=interaction.guild_id, week=week
        )
        if player:
            embed = self.get_player_embed(player)
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("Player not found")

    def get_player_embed(self, player):
        embed = discord.Embed(
            title=player["name"]["full"],
            description="#" + player["uniform_number"],
            color=0xEEE657,
        )
        embed.add_field(name="Postion", value=player["primary_position"])
        embed.add_field(name="Team", value=player["editorial_team_abbr"])
        if "bye_weeks" in player:
            embed.add_field(name="Bye", value=player["bye_weeks"]["week"])
        embed.add_field(name="Owner", value=player["owner"])
        embed.set_thumbnail(url=player["image_url"])
        if "total_points" in player["stats"]:
            embed.add_field(
                name="Total Points",
                value=player["stats"]["total_points"],
                inline=False,
            )
        if len(player["stats"].items()) < 20:
            for key, value in player["stats"].items():
                if key == "total_points":
                    continue
                embed.add_field(name=key, value=value)
        return embed

    def get_player_text(self, player):
        player_details_text = (
            player["name"]["full"] + " #" + player["uniform_number"] + "\n"
        )
        player_details_text = (
            player_details_text
            + "Position: "
            + player["primary_position"]
            + "\n"
        )
        player_details_text = (
            player_details_text
            + "Team: "
            + player["editorial_team_abbr"]
            + "\n"
        )
        if "bye_weeks" in player:
            player_details_text = (
                player_details_text
                + "Bye: "
                + player["bye_weeks"]["week"]
                + "\n"
            )
        if "player_points" in player:
            player_details_text = (
                player_details_text
                + "Total Points: "
                + player["player_points"]["total"]
                + "\n"
            )
        player_owner = self.yahoo_api.get_player_owner(player["player_id"])
        if player_owner:
            player_details_text = (
                player_details_text + "Owner: " + player_owner
            )
        return player_details_text

    @app_commands.command(
        name="matchups", description="Returns the current weeks matchups"
    )
    async def matchups(
        self, interaction: discord.Interaction, week: Optional[int] = None
    ):
        logger.info(
            "Command:Matchups called in {} with week: {}".format(
                interaction.guild_id, week
            )
        )
        await interaction.response.defer()
        if self.yahoo_api.get_settings(guild_id=interaction.guild_id)["draft_status"] == "predraft":
            await interaction.followup.send("Matchups not available yet")
            return
        week, details = self.yahoo_api.get_matchups(
            guild_id=interaction.guild_id, week=week
        )
            
        if details:
            embed = discord.Embed(
                title="Matchups for Week {}".format(week),
                description="",
                color=0xEEE657,
            )
            for detail in details:
                embed.add_field(
                    name=detail["name"], value=detail["value"], inline=False
                )
            await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send(self.error_message)

    @app_commands.command(
        name="waivers",
        description="Returns the waiver transactions from the last 24 hours",
    )
    async def waivers(self, interaction: discord.Interaction, days: int = 1):
        logger.info("Command:Waivers called in %i", interaction.guild_id)

        await interaction.response.defer()
        embed_functions_dict = {
            "add/drop": utils.create_add_drop_embed,
            "add": utils.create_add_embed,
            "drop": utils.create_drop_embed,
        }
        ts = datetime.now() - timedelta(days=days)
        transactions = self.yahoo_api.get_transactions(
            guild_id=interaction.guild_id, timestamp=ts.timestamp()
        )
        if transactions:
            for transaction in transactions:
                await interaction.followup.send(
                    embed=embed_functions_dict[transaction["type"]](
                        transaction
                    )
                )
        else:
            await interaction.followup.send("No transactions found")
