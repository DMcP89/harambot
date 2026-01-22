import base64
import requests
import time
import logging

from cachetools import keys

from harambot.config import settings
from harambot import yahoo_api
from discord import Embed

YAHOO_API_URL = "https://api.login.yahoo.com/oauth2/"
YAHOO_AUTH_URI = "request_auth?redirect_uri=oob&response_type=code&client_id="

logger = logging.getLogger("discord.harambot.utils")


def yahoo_auth(code):
    encoded_creds = base64.b64encode(
        ("{0}:{1}".format(settings.yahoo_key, settings.yahoo_secret)).encode(
            "utf-8"
        )
    )
    response = requests.post(
        url="{}get_token".format(YAHOO_API_URL),
        data={
            "code": code,
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


def create_add_embed(transaction):
    embed = Embed(title="Player Added")
    add_player_fields_to_embed(embed, transaction["players"]["0"]["player"][0])
    embed.add_field(
        name="Owner",
        value=transaction["players"]["0"]["player"][1]["transaction_data"][0][
            "destination_team_name"
        ],
    )
    if "faab_bid" in transaction:
        embed.add_field(
            name="Bid", value=transaction["faab_bid"], inline=False
        )
    return embed


def create_drop_embed(transaction):
    embed = Embed(title="Player Dropped")
    add_player_fields_to_embed(embed, transaction["players"]["0"]["player"][0])
    embed.add_field(
        name="Owner",
        value=transaction["players"]["0"]["player"][1]["transaction_data"][
            "source_team_name"
        ],
    )
    return embed


def create_add_drop_embed(transaction):
    embed = Embed(title="Player Added / Player Dropped")
    embed.add_field(
        name="Owner",
        value=transaction["players"]["0"]["player"][1]["transaction_data"][0][
            "destination_team_name"
        ],
    )
    if "faab_bid" in transaction:
        embed.add_field(
            name="Bid", value=transaction["faab_bid"], inline=False
        )
    embed.add_field(
        name="Player Added", value="=====================", inline=False
    )
    add_player_fields_to_embed(embed, transaction["players"]["0"]["player"][0])
    embed.add_field(
        name="Player Dropped", value="=====================", inline=False
    )
    add_player_fields_to_embed(embed, transaction["players"]["1"]["player"][0])
    return embed


def add_player_fields_to_embed(embed, player):
    embed.add_field(
        name="Player", value=player[2]["name"]["full"], inline=True
    )
    embed.add_field(
        name="Team", value=player[3]["editorial_team_abbr"], inline=True
    )
    embed.add_field(
        name="Position", value=player[4]["display_position"], inline=True
    )


def get_avatar_bytes():
    # return the image from the settings.webhook_avatar_url variable as bytes
    return requests.get(settings.webhook_avatar_url).content


def get_cache_key(*args, **kwargs):
    function_name = args[0]
    guild_id = str(kwargs.get("guild_id"))
    return keys.hashkey(function_name, guild_id)

def clear_guild_cache(guild_id):
    guild_cache_keys = [
        get_cache_key("get_settings", guild_id=guild_id),
        get_cache_key("get_teams", guild_id=guild_id),
        get_cache_key("get_players", guild_id=guild_id),
        get_cache_key("get_standings", guild_id=guild_id),
        get_cache_key("get_roster", guild_id=guild_id),
        get_cache_key("get_matchups", guild_id=guild_id),
        get_cache_key("get_latest_trade", guild_id=guild_id),
        get_cache_key("get_transactions", guild_id=guild_id)
    ]
    for key in guild_cache_keys:
        yahoo_api.cache.pop(key, None)

def get_player_embed(player):
    embed = Embed(
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

def get_matchup_details(team):
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

def get_matchups_embed(week, matchups):
    details = []
    divider = "--------------------------------------"
    for matchup in matchups:
        team1_details = get_matchup_details(matchup["0"]["team"])
        team2_details = get_matchup_details(matchup["1"]["team"])
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
    if details:
        embed = Embed(
            title="Matchups for Week {}".format(week),
            description="",
            color=0xEEE657,
        )
        for detail in details:
            embed.add_field(
                name=detail["name"], value=detail["value"], inline=False
            )
    return embed
