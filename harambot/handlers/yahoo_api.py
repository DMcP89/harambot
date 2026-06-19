import logging
import os
import objectpath
import functools

from yahoo_fantasy_api import game
from cachetools import cached, keys
from playhouse.shortcuts import model_to_dict
from yahoo_oauth import OAuth2

from harambot.database.models import Guild
from harambot.config import settings, cache
from harambot.utils import get_cache_key
from harambot.handlers.api_handler import APIHandler

logging.setLoggerClass(logging.Logger)
logging.getLogger("yahoo_oauth").setLevel("INFO")

logger = logging.getLogger("discord.harambot.yahoo_api")

YAHOO_API_TOKEN_URL = "https://api.login.yahoo.com/oauth2/get_token"

class Yahoo (APIHandler):
    cache = cache
    league_id = None
    league_type = None
    current_league = None

    def handle_authentication(self, guild_id: int, token: str):
        encoded_creds = base64.b64encode(
            ("{0}:{1}".format(settings.yahoo_key, settings.yahoo_secret)).encode(
                "utf-8"
            )
        )
        response = requests.post(
            url="{}get_token".format(YAHOO_API_URL),
            data={
                "code": token,
                "redirect_uri": "oob",
                "grant_type": "authorization_code",
            },
            headers={
                "User-Agent": "HaramBot",
                "Authorization": "Basic {0}".format(encoded_creds.decode("utf-8")),
                "Content-Type": "application/x-www-form-urlencoded",
            },
        )
        if response.status_code != 200:
            logger.error(
                "Failed to authenticate with Yahoo API: {}".format(response.json)
            )
            return {}
        details = response.json()

        details["token_time"] = time.time()
        return details

    def handle_oauth(f):
        @functools.wraps(f)
        def wrapper(self, *args, **kwargs):
            guild_id = kwargs.get("guild_id")
            if guild_id is None:
                logger.error("Guild id not provided to Yahoo API")
                return None
            guild = Guild.get_or_none(Guild.guild_id == str(guild_id))
            if guild is None:
                logger.error(
                    "Guild with id %s does not exist in the database",
                    guild_id,
                )

                return None
            self.oauth = OAuth2(
                settings.yahoo_key,
                settings.yahoo_secret,
                store_file=False,
                **model_to_dict(guild),
            )
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
            self.league_id = guild.league_id
            self.league_type = guild.league_type
            if not self.current_league or self.current_league.league_id.split(".l.")[-1] != self.league_id:
                gm = game.Game(self.oauth, self.league_type)
                leagues = gm.league_ids(game_codes=[self.league_type])
                for league_id in leagues:
                    if league_id.split(".l.")[-1] == self.league_id:
                        self.current_league = gm.to_league(league_id)
            return f(self, *args, **kwargs)

        return wrapper

    @cached(cache, key=functools.partial(get_cache_key, "get_leagues"))
    @handle_oauth
    def get_leagues(self, guild_id):
        logger.info("Fetching leagues for guild: %s", guild_id)
        try:
            gm = game.Game(self.oauth, self.league_type)
            leagues = gm.league_ids(is_available=True)
            return leagues
        except Exception:
            logger.exception(
                "Error while fetching leagues for guild {}".format(guild_id)
                )
            return None


    @cached(cache, key=functools.partial(get_cache_key, "get_settings_for_league"))
    @handle_oauth
    def get_settings_for_league(self, league_id, guild_id):
        try:
            gm = game.Game(self.oauth, self.league_type)
            league = gm.to_league(league_id)
            return league.settings()
        except Exception:
            logger.exception(
                "Error while fetching settings for league {} in guild {}".format(
                    league_id,
                    guild_id,
                )
            )
            return None


    @cached(cache, key=functools.partial(get_cache_key, "get_settings"))
    @handle_oauth
    def get_settings(self, guild_id):
        try:
            return self.current_league.settings()
        except Exception:
            logger.exception(
                "Error while fetching settings for league {} in guild {}".format(
                    self.league_id,
                    guild_id,
                )
            )
            return None


    @cached(cache, key=functools.partial(get_cache_key, "get_teams"))
    @handle_oauth
    def get_teams(self, guild_id):
        try:
            return self.current_league.teams()
        except Exception:
            logger.exception(
                "Error while fetching teams for league {} in guild {}".format(
                    self.league_id,
                    guild_id,
                )
            )
            return None

    @cached(cache, key=functools.partial(get_cache_key, "get_players"))
    @handle_oauth
    def get_players(self, player, guild_id):
        try:
            return self.current_league.player_details(player)
        except Exception:
            logger.exception(
                "Error while fetching players for league {} in guild: {}".format(
                    self.league_id,
                    guild_id,
                )
            )
            return None

    @cached(cache, key=functools.partial(get_cache_key, "get_standings"))
    @handle_oauth
    def get_standings(self, guild_id):
        scoring_type = self.get_settings(guild_id=guild_id)["scoring_type"]
        description = "W-L-T" if scoring_type == "head" else "Team \nPoints For - Points Change"
        try:
            standings = []
            for idx, team in enumerate(self.current_league.standings()):
                if "outcome_totals" in team:
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
                elif "points_for" in team:
                    standings.append(
                        {
                            "place": str(idx + 1) + ". " + team["name"],
                            "record": "{} - {}".format(team["points_for"],team["points_change"])
                        }
                    )
            return description, standings
        except Exception:
            logger.exception(
                "Error while fetching standings for league {} in guild {}".format(
                    self.league_id,
                    guild_id,
                )
            )
            return None, None

    @cached(cache, key=functools.partial(get_cache_key, "roster_check"))
    @handle_oauth
    def roster_check(self, guild_id):
        settings = self.get_settings(guild_id=guild_id)
        return settings and settings.get("draft_status") != "predraft"

    @cached(cache, key=functools.partial(get_cache_key, "get_roster"))
    @handle_oauth
    def get_roster(self, team_name, guild_id):
        try:
            team_details = self.current_league.get_team(team_name)
            if team_details:
                return team_details[team_name].roster()
            else:
                return None
        except Exception:
            logger.exception(
                "Error while fetching roster for team: {} in league {} for guild: {}".format(
                    team_name, self.league_id, guild_id
                )
            )
            return None

    # @cached(cache)
    @handle_oauth
    def get_player_details(self, player_name, guild_id, week=None):
        try:
            player = self.current_league.player_details(player_name)[0]
            player["owner"] = self.get_player_owner(player["player_id"])
            if week:
                stats = self.current_league.player_stats(
                    [player["player_id"]],
                    req_type="week",
                    week=week,
                )[0]
            else:
                stats = self.current_league.player_stats(
                    [player["player_id"]],
                    req_type="season",
                )[0]
            del stats["player_id"]
            del stats["name"]
            del stats["position_type"]
            if len(stats) > 20:
                stats = {k: v for k, v in stats.items() if v != 0.0}
            player["stats"] = stats
            return player
        except Exception:
            logger.exception(
                "Error while fetching player details for player: \
                    {} in league {} in guild {}".format(
                    player_name, self.league_id, guild_id
                )
            )
            return None

    def get_player_owner(self, player_id):
        try:
            player_ownership = self.current_league.ownership([player_id])[
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

    @cached(cache, key=functools.partial(get_cache_key, "matchups_check"))
    @handle_oauth
    def matchups_check(self, guild_id):
        settings = self.get_settings(guild_id=guild_id)
        return settings and settings.get("draft_status") != "predraft"

    @cached(cache, key=functools.partial(get_cache_key, "get_matchups"))
    @handle_oauth
    def get_matchups(self, guild_id, week=None):
        try:
            if not week:
                week = self.current_league.current_week()
            matchups = objectpath.Tree(
                self.current_league.matchups(week=week)
            ).execute("$..scoreboard..matchups..matchup..teams")
            return matchups 
        except Exception:
            logger.exception(
                "Error while fetching matchups for league: {} for guild: {}".format(
                    self.league_id,
                    guild_id,
                )
            )

    @cached(cache, key=functools.partial(get_cache_key, "trade_check"))
    @handle_oauth
    def trade_check(self, guild_id):
        return self.get_settings(guild_id=guild_id)["trade_ratify_type"] == "none"

    @cached(cache, key=functools.partial(get_cache_key, "get_latest_trade"))
    @handle_oauth
    def get_latest_trade(self, guild_id):
        try:
            for key, values in self.current_league.teams().items():
                if "is_owned_by_current_login" in values:
                    team = self.current_league.to_team(key)
                    accepted_trades = list(
                        filter(
                            lambda d: d["status"] == "accepted",
                            team.proposed_trades(),
                        )
                    )
                    if accepted_trades:
                        # return the last accepted trade
                        latest_trade = accepted_trades[-1]
                        trader = self.current_league.to_team(latest_trade["trader_team_key"]).details()["name"]
                        tradee = self.current_league.to_team(latest_trade["tradee_team_key"]).details()["name"]
                        trader_player_names = []
                        tradee_player_names = []
                        for player in latest_trade["players"]["player"]:
                            if player["transaction_data"]["source_team_key"] == latest_trade["trader_team_key"]:
                                trader_player_names.append(player["name"]["full"])
                            else:
                                tradee_player_names.append(player["name"]["full"])

                        confirm_trade_message = "\n{} sends {} to {} for {}".format(
                            trader,
                            ", ".join(trader_player_names),
                            tradee,
                            ", ".join(tradee_player_names),
                        )
                        return confirm_trade_message
                        
            return None
        except Exception:
            logger.exception(
                "Error fetching latest trades for league: {} in guild {}".format(
                    self.league_id, guild_id
                )
            )
            return None
    

    @cached(cache, key=functools.partial(get_cache_key, "get_transactions"))
    @handle_oauth
    def get_transactions(self, guild_id, timestamp=0.0):
        try:
            transactions = self.current_league.transactions("add,drop", "")
            filtered_transactions = [
                t for t in transactions if float(t["timestamp"]) > timestamp
            ]
            return filtered_transactions
        except Exception:
            logger.exception(
                "Error fetching latest waivers for league: {} in guild {}".format(
                    self.league_id,
                    guild_id,
                )
            )
            return []
