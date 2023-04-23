import discord
import logging
import urllib3

from discord.ext import commands
from discord import app_commands
from yahoo_oauth import OAuth2
from playhouse.shortcuts import model_to_dict

from harambot.yahoo_api import Yahoo
from harambot.database.models import Guild


logger = logging.getLogger(__file__)
logger.setLevel(logging.INFO)


class YahooCog(commands.Cog):

    error_message = (
        "I'm having trouble getting that right now please try again later"
    )

    def __init__(self, bot, KEY, SECRET):
        self.bot = bot
        self.http = urllib3.PoolManager()
        self.KEY = KEY
        self.SECRET = SECRET
        self.yahoo_api = None

    async def cog_before_invoke(self, ctx):
        guild = Guild.get(Guild.guild_id == str(ctx.guild.id))
        self.yahoo_api = Yahoo(
            OAuth2(
                self.KEY, self.SECRET, store_file=False, **model_to_dict(guild)
            ),
            guild.league_id,
            guild.league_type,
        )
        return

    async def set_yahoo_from_interaction(
        self, interaction: discord.Interaction
    ):
        guild = Guild.get(Guild.guild_id == str(interaction.guild_id))
        self.yahoo_api = Yahoo(
            OAuth2(
                self.KEY, self.SECRET, store_file=False, **model_to_dict(guild)
            ),
            guild.league_id,
            guild.league_type,
        )
        return

    @app_commands.command(
        name="standings",
        description="Returns the current standings of your league",
    )
    async def standings(self, interaction: discord.Interaction):
        logger.info("standings called")
        embed = discord.Embed(
            title="Standings",
            description="Team Name\n W-L-T",
            color=0xEEE657,
        )
        await self.set_yahoo_from_interaction(interaction)
        for team in self.yahoo_api.get_standings():
            embed.add_field(
                name=team["place"],
                value=team["record"],
                inline=False,
            )
        if embed:
            await interaction.response.send_message(embed=embed)
        else:
            await interaction.response.send_message(self.error_message)

    @app_commands.command(
        name="roster", description="Returns the roster of the given team"
    )
    async def roster(self, interaction: discord.Interaction, team_name: str):
        logger.info("roster called")
        await self.set_yahoo_from_interaction(interaction)
        embed = discord.Embed(
            title="{}'s Roster".format(team_name),
            description="",
            color=0xEEE657,
        )
        roster = self.yahoo_api.get_roster(team_name)
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
        logger.info("trade called")
        await self.set_yahoo_from_interaction(interaction)
        latest_trade = self.yahoo_api.get_latest_trade()

        if latest_trade is None:
            await interaction.response.send_message(
                "No trades up for approval at this time"
            )
            return

        teams = self.yahoo_api.league().teams()

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
            api_details = (
                self.get_player_text(
                    self.yahoo_api.get_player_details(player["name"])
                )
                + "\n"
            )
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

    @app_commands.command(
        name="stats", description="Returns the details of the given player"
    )
    async def stats(self, interaction: discord.Interaction, player_name: str):
        logger.info("player_details called")
        await self.set_yahoo_from_interaction(interaction)
        player = self.yahoo_api.get_player_details(player_name)
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
        embed.set_image(url=player["image_url"])
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
        player_details_text = (
            player_details_text
            + "Owner: "
            + self.yahoo_api.get_player_owner(player["player_id"])
        )
        return player_details_text

    @app_commands.command(
        name="matchups", description="Returns the current weeks matchups"
    )
    async def matchups(self, interaction: discord.Interaction):
        await self.set_yahoo_from_interaction(interaction)
        week, details = self.yahoo_api.get_matchups()
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
        name="waviers",
        description="Returns the wavier transactions from the last 24 hours",
    )
    async def waviers(self, interaction: discord.Interaction):
        await self.set_yahoo_from_interaction(interaction)
        await interaction.response.defer(thinking=True)
        embed_functions_dict = {
            "add/drop": self.create_add_drop_embed,
            "add": self.create_add_embed,
            "drop": self.create_drop_embed,
        }
        for transaction in self.yahoo_api.get_latest_waiver_transactions():
            await interaction.followup.send(
                embed=embed_functions_dict[transaction["type"]](transaction)
            )

    def create_add_embed(self, transaction):
        embed = discord.Embed(title="Player Added")
        self.add_player_fields_to_embed(
            embed, transaction["players"]["0"]["player"][0]
        )
        embed.add_field(
            name="Owner",
            value=transaction["players"]["0"]["player"][1]["transaction_data"][
                0
            ]["destination_team_name"],
        )
        return embed

    def create_drop_embed(self, transaction):
        embed = discord.Embed(title="Player Dropped")
        self.add_player_fields_to_embed(
            embed, transaction["players"]["0"]["player"][0]
        )
        embed.add_field(
            name="Owner",
            value=transaction["players"]["0"]["player"][1]["transaction_data"][
                "source_team_name"
            ],
        )
        return embed

    def create_add_drop_embed(self, transaction):
        embed = discord.Embed(title="Player Added/ Player Dropped")
        embed.add_field(
            name="Player Added", value="=====================", inline=True
        )
        self.add_player_fields_to_embed(
            embed, transaction["players"]["0"]["player"][0]
        )
        embed.add_field(
            name="Player Dropped", value="=====================", inline=True
        )
        self.add_player_fields_to_embed(
            embed, transaction["players"]["1"]["player"][0]
        )
        return embed

    def add_player_fields_to_embed(self, embed, player):
        embed.add_field(
            name="Player", value=player[2]["name"]["full"], inline=True
        )
        embed.add_field(
            name="Team", value=player[3]["editorial_team_abbr"], inline=True
        )
        embed.add_field(
            name="Position", value=player[4]["display_position"], inline=True
        )
