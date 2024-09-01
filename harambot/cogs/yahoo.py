import discord
import logging


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
        embed = discord.Embed(
            title="Standings",
            description="Team Name\n W-L-T",
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
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(self.error_message)

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
        embed = discord.Embed(
            title="{}'s Roster".format(team_name),
            description="",
            color=0xEEE657,
        )
        roster = self.yahoo_api.get_roster(
            guild_id=interaction.guild_id, team_name=team_name
        )
        if roster:
            for player in roster:
                embed.add_field(
                    name=player["selected_position"],
                    value=player["name"],
                    inline=False,
                )
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(self.error_message)

    @app_commands.command(
        name="trade",
        description="Create poll for latest trade for league approval",
    )
    async def trade(self, interaction: discord.Interaction):
        logger.info("Command:Trade called in %i", interaction.guild_id)
        latest_trade = self.yahoo_api.get_latest_trade(
            guild_id=interaction.guild_id
        )
        if latest_trade is None:
            await interaction.response.send_message(
                "No trades up for approval at this time"
            )
            return

        teams = self.yahoo_api.get_teams()
        if teams is None:
            await interaction.response.send_message(self.error_message)
            return
        trader = teams[latest_trade["trader_team_key"]]
        tradee = teams[latest_trade["tradee_team_key"]]
        managers = [trader["name"], tradee["name"]]

        player_set0 = []
        player_set0_details = ""
        for player in latest_trade["trader_players"]:
            if player:
                player_set0.append(player["name"])
                api_details = (
                    self.get_player_text(
                        self.yahoo_api.get_player_details(player["name"])
                    )
                    + "\n"
                )
                if api_details:
                    player_set0_details = player_set0_details + api_details
                else:
                    await interaction.send(self.error_message)
                    return

        player_set1 = []
        player_set1_details = ""
        for player in latest_trade["tradee_players"]:
            player_set1.append(player["name"])
            player_details = self.yahoo_api.get_player_details(player["name"])
            if player_details is None:
                await interaction.send(self.error_message)
                return
            api_details = self.get_player_text(player_details) + "\n"
            if api_details:
                player_set1_details = player_set1_details + api_details
            else:
                await interaction.response.send_message(self.error_message)
                return

            confirm_trade_message = "{} sends {} to {} for {}".format(
                managers[0],
                ", ".join(player_set0),
                managers[1],
                ", ".join(player_set1),
            )
            announcement = "There's collusion afoot!\n"
            embed = discord.Embed(
                title="The following trade is up for approval:",
                description=confirm_trade_message,
                color=0xEEE657,
            )
            embed.add_field(
                name="{} sends:".format(managers[0]),
                value=player_set0_details,
                inline=False,
            )
            embed.add_field(
                name="to {} for:".format(managers[1]),
                value=player_set1_details,
                inline=False,
            )
            embed.add_field(
                name="Voting",
                value=" Click :white_check_mark: for yes,\
                     :no_entry_sign: for no",
            )
            await interaction.response.send_message(
                content=announcement, embed=embed
            )
            response_message = await interaction.original_response()
            yes_emoji = "\U00002705"
            no_emoji = "\U0001F6AB"
            await response_message.add_reaction(yes_emoji)
            await response_message.add_reaction(no_emoji)

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
    async def stats(self, interaction: discord.Interaction, player_name: str):
        logger.info(
            "Command:Stats called in %i with player_name:%s",
            interaction.guild_id,
            player_name,
        )
        player = self.yahoo_api.get_player_details(
            player_name, guild_id=interaction.guild_id
        )
        if player:
            embed = self.get_player_embed(player)
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message("Player not found")

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
        if "player_points" in player:
            embed.add_field(
                name="Total Points", value=player["player_points"]["total"]
            )
        embed.add_field(name="Owner", value=player["owner"])
        embed.set_thumbnail(url=player["image_url"])
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
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(self.error_message)

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
