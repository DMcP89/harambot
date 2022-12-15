import logging
import os
import discord
import objectpath

from yahoo_fantasy_api import game
from cachetools import cached, TTLCache

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)


dir_path = os.path.dirname(os.path.realpath(__file__))


class Yahoo:

    oauth = None
    scoring_type = None

    def __init__(self, oauth, league_id, league_type):
        self.oauth = oauth
        self.league_id = league_id
        self.league_type = league_type

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def league(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        league = gm.to_league("{}.l.{}".format(gm.game_id(), self.league_id))
        self.scoring_type = league.settings()["scoring_type"]
        return league

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        try:
            standings = []
            for idx, team in enumerate(self.league().standings()):
                outcomes = team["outcome_totals"]
                record = "{}-{}-{}".format(
                    outcomes["wins"], outcomes["losses"], outcomes["ties"]
                )
                standings.append(
                    {
                        "place": str(idx + 1) + ". " + team["name"],
                        "record": record,
                    }
                )
            return standings
        except Exception:
            logger.exception(
                "Error while fetching standings for league {}".format(
                    self.league_id
                )
            )
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, team_name):
        try:
            for id, team in self.league().teams().items():
                if team["name"] == team_name:
                    return self.league().to_team(id)
        except Exception:
            logger.exception(
                "Error while fetching team: {} from league: {}".format(
                    team_name, self.league_id
                )
            )
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        team = self.get_team(team_name)
        if team:
            embed = discord.Embed(
                title="{}'s Roster".format(team_name),
                description="",
                color=0xEEE657,
            )
            for player in team.roster(self.league().current_week()):
                embed.add_field(
                    name=player["selected_position"],
                    value=player["name"],
                    inline=False,
                )
            return embed
        else:
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_details(self, player_name):
        try:
            player = self.league().player_details(player_name)[0]

            embed = discord.Embed(
                title=player["name"]["full"],
                description="#" + player["uniform_number"],
                color=0xEEE657,
            )
            embed.add_field(name="Postion", value=player["primary_position"])
            embed.add_field(name="Team", value=player["editorial_team_abbr"])
            if "bye_weeks" in player:
                embed.add_field(name="Bye", value=player["bye_weeks"]["week"])
            if self.scoring_type == "head":
                embed.add_field(
                    name="Total Points", value=player["player_points"]["total"]
                )
            embed.add_field(
                name="Owner", value=self.get_player_owner(player["player_id"])
            )
            embed.set_image(url=player["image_url"])

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
            if self.scoring_type == "head":
                player_details_text = (
                    player_details_text
                    + "Total Points: "
                    + player["player_points"]["total"]
                    + "\n"
                )
            player_details_text = (
                player_details_text
                + "Owner: "
                + self.get_player_owner(player["player_id"])
            )

            player_details = {}
            player_details["embed"] = embed
            player_details["text"] = player_details_text
            return player_details
        except Exception:
            logger.exception(
                "Error while fetching player details for player: \
                    {} in league {}".format(
                    player_name, self.league_id
                )
            )
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_owner(self, player_id):
        try:
            player_ownership = self.league().ownership([player_id])[
                str(player_id)
            ]
            if "owner_team_name" in player_ownership:
                return player_ownership["owner_team_name"]
            else:
                ownership_map = {
                    "freeagents": "Free Agent",
                    "waivers": "On Waviers",
                }
                return ownership_map.get(
                    player_ownership["ownership_type"], ""
                )
        except Exception:
            logger.exception(
                "Error while fetching ownership for player id: \
                    {} in league {}".format(
                    player_id, self.league_id
                )
            )
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_matchups(self):
        try:
            embed = discord.Embed(
                title="Matchups for Week {}".format(
                    str(self.league().current_week())
                ),
                description="",
                color=0xEEE657,
            )
            matchups = objectpath.Tree(self.league().matchups()).execute(
                "$..scoreboard..matchups..matchup..teams"
            )

            # loop through each matchup element
            for matchup in matchups:
                # handle team 1
                team1_details = self.get_matchup_details(matchup["0"]["team"])

                # handle team 2
                team2_details = self.get_matchup_details(matchup["1"]["team"])
                divider = "--------------------------------------"

                # Add details to embed
                embed.add_field(
                    name="{} vs {}".format(
                        team1_details["name"], team2_details["name"]
                    ),
                    value=team1_details["text"]
                    + team2_details["text"]
                    + divider,
                    inline=False,
                )
            return embed
        except Exception:
            logger.exception(
                "Error while fetching matchups for league: {}".format(
                    self.league_id
                )
            )

    def get_matchup_details(self, team):
        team_name = team[0][2]["name"]
        team_details = ""
        if self.scoring_type == "head":
            # handle data for head to head scoring
            team1_actual_points = team[1]["team_points"]["total"]
            team1_projected_points = team[1]["team_projected_points"]["total"]
            if "win_probability" in team[1]:
                team1_win_probability = "{:.0%}".format(
                    team[1]["win_probability"]
                )
                team_details = "***{}*** \n Projected Score: {} \n  \
                            Actual Score: {} \n Win Probability: {} \n".format(
                    team_name,
                    team1_projected_points,
                    team1_actual_points,
                    team1_win_probability,
                )
            else:
                team_details = "***{}*** \n Projected Score: {} \n  \
                            Actual Score: {} \n".format(
                    team_name,
                    team1_projected_points,
                    team1_actual_points,
                )
        else:
            team_details = "***{}*** \n Score: {} \n  \
                            Remaining Games: {} \n \
                                Live Games: {} \n \
                                    Completed Games: {} \n".format(
                team_name,
                team[1]["team_points"]["total"],
                team[1]["team_remaining_games"]["total"]["remaining_games"],
                team[1]["team_remaining_games"]["total"]["live_games"],
                team[1]["team_remaining_games"]["total"]["completed_games"],
            )
        return {"name": team_name, "text": team_details}

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_latest_trade(self):
        try:
            for key, values in self.league().teams().items():
                if "is_owned_by_current_login" in values:
                    team = self.league().to_team(key)
                    accepted_trades = list(
                        filter(
                            lambda d: d["status"] == "accepted",
                            team.proposed_trades(),
                        )
                    )
                    if accepted_trades:
                        return accepted_trades[0]
            return
        except Exception:
            logger.exception("Error while fetching latest trade")
