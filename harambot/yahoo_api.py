import logging
import os
import objectpath


from yahoo_fantasy_api import game
from cachetools import cached, TTLCache
from datetime import datetime, timedelta

logger = logging.getLogger("discord.harambot.yahoo_api")


dir_path = os.path.dirname(os.path.realpath(__file__))
cache = TTLCache(maxsize=1024, ttl=600)


class Yahoo:

    oauth = None
    scoring_type = None

    def __init__(self, oauth, league_id, league_type):
        self.oauth = oauth
        self.league_id = league_id
        self.league_type = league_type

    def league(self):

        try:
            if not self.oauth.token_is_valid():
                self.oauth.refresh_access_token()
        except Exception:
            logger.exception(
                "Error while refreshing access token for league: {}".format(
                    self.league_id
                )
            )
            return None

        try:
            gm = game.Game(self.oauth, self.league_type)
            league = gm.to_league(
                "{}.l.{}".format(gm.game_id(), self.league_id)
            )
            self.scoring_type = league.settings()["scoring_type"]
            return league
        except Exception:
            logger.exception(
                "Error while fetching league details for league {}".format(
                    self.league_id
                )
            )
            return None

    def get_teams(self):
        try:
            return self.league().teams()
        except Exception:
            logger.exception(
                "Error while fetching teams for league {}".format(
                    self.league_id
                )
            )
            return None

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

    @cached(cache)
    def get_roster(self, team_name):
        try:
            team_details = self.league().get_team(team_name)
            if team_details:
                return team_details[team_name].roster(
                    self.league().current_week()
                )
            else:
                return None
        except Exception:
            logger.exception(
                "Error while fetching roster for team: {} in league {}".format(
                    team_name, self.league_id
                )
            )
            return None

    @cached(cache)
    def get_player_details(self, player_name):
        try:
            player = self.league().player_details(player_name)[0]
            player["owner"] = self.get_player_owner(player["player_id"])
            return player
        except Exception:
            logger.exception(
                "Error while fetching player details for player: \
                    {} in league {}".format(
                    player_name, self.league_id
                )
            )
            return None

    @cached(cache)
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
                    "waivers": "On Waivers",
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

    def get_matchups(self, week=None):
        try:
            if not week:
                week = self.league().current_week()
            matchups = objectpath.Tree(
                self.league().matchups(week=week)
            ).execute("$..scoreboard..matchups..matchup..teams")

            details = []
            divider = "--------------------------------------"
            for matchup in matchups:
                team1_details = self.get_matchup_details(matchup["0"]["team"])
                team2_details = self.get_matchup_details(matchup["1"]["team"])
                details.append(
                    {
                        "name": "{} vs {}".format(
                            team1_details["name"], team2_details["name"]
                        ),
                        "value": team1_details["text"]
                        + team2_details["text"]
                        + divider,
                    }
                )
            return str(week), details
        except Exception as e:
            logger.exception(
                "Error while fetching matchups for league: {}".format(
                    self.league_id
                ),
                e,
            )

    def get_matchup_details(self, team):
        team_name = team[0][2]["name"]
        team_details = "***{}*** \n".format(team_name)

        actual_points = team[1]["team_points"]["total"]
        team_details += "Score: {} \n".format(actual_points)

        if "team_projected_points" in team[1]:
            projected_points = team[1]["team_projected_points"]["total"]
            team_details += "Projected Score: {} \n".format(projected_points)

        if "win_probability" in team[1]:
            win_probability = "{:.0%}".format(team[1]["win_probability"])
            team_details += "Win Probability: {} \n".format(win_probability)

        if "team_remaining_games" in team[1]:
            remaining_games = team[1]["team_remaining_games"]["total"][
                "remaining_games"
            ]
            live_games = team[1]["team_remaining_games"]["total"]["live_games"]
            completed_games = team[1]["team_remaining_games"]["total"][
                "completed_games"
            ]
            team_details += "Remaining Games: {} \n".format(remaining_games)
            team_details += "Live Games: {} \n".format(live_games)
            team_details += "Completed Games: {} \n".format(completed_games)

        return {"name": team_name, "text": team_details}

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
            logger.exception(
                "Error fetching latest trades for league: {}".format(
                    self.league_id
                )
            )

    def get_latest_waiver_transactions(self):
        ts = datetime.now() - timedelta(days=1)
        try:
            transactions = self.league().transactions("add,drop", "")
            filtered_transactions = [
                t for t in transactions if int(t["timestamp"]) > ts.timestamp()
            ]
            return filtered_transactions
        except Exception:
            logger.exception(
                "Error fetching latest waivers for league: {}".format(
                    self.league_id
                )
            )
            return None
