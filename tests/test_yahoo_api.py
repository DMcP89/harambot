from unittest.mock import patch
from yahoo_fantasy_api import team


def test_league(api):
    assert api.league()


def test_get_standings(api):
    get_standings_func = api.get_standings
    while hasattr(get_standings_func, "__wrapped__"):
        get_standings_func = get_standings_func.__wrapped__
    return_value = get_standings_func(api, "mock")
    assert isinstance(return_value, list)
    assert len(return_value) == 3
    assert return_value[0]["place"] == "1. Hide and Go Zeke"


def test_get_roster(api, mock_roster):
    get_roster_func = api.get_roster
    while hasattr(get_roster_func, "__wrapped__"):
        get_roster_func = get_roster_func.__wrapped__
    with patch.object(team.Team, "roster", return_value=mock_roster):
        return_value = get_roster_func(api, "Too Many Cooks", guild_id="mock")
        assert isinstance(return_value, list)
        assert return_value[0]["selected_position"] == "QB"
        assert return_value[0]["name"] == "Josh Allen"


def test_get_player_owner(api):
    return_value = api.get_player_owner("30977")
    assert isinstance(return_value, str)
    assert return_value == "Hide and Go Zeke"


def test_get_player_details(api):
    get_player_details_func = api.get_player_details
    while hasattr(get_player_details_func, "__wrapped__"):
        get_player_details_func = get_player_details_func.__wrapped__
    return_value = get_player_details_func(api, "Josh Allen", guild_id="mock")
    assert isinstance(return_value, dict)
    assert return_value["player_key"] == "399.p.30977"
    assert return_value["owner"] == "Hide and Go Zeke"


def test_get_matchups(api):
    get_matchups_func = api.get_matchups
    while hasattr(get_matchups_func, "__wrapped__"):
        get_matchups_func = get_matchups_func.__wrapped__
    week, details = get_matchups_func(api, guild_id="mock")
    assert isinstance(details, list)
    assert week == "1"


def test_get_matchups_category(category_api):
    get_matchups_func = category_api.get_matchups
    while hasattr(get_matchups_func, "__wrapped__"):
        get_matchups_func = get_matchups_func.__wrapped__
    week, details = get_matchups_func(category_api, guild_id="mock")
    assert isinstance(details, list)
    assert len(details) == 7
    assert week == "1"
