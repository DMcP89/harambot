from unittest.mock import patch
from yahoo_fantasy_api import team


def test_league(api):
    assert api.league()


def test_get_standings(api):
    return_value = api.get_standings()
    assert isinstance(return_value, list)
    assert len(return_value) == 3
    assert return_value[0]["place"] == "1. Hide and Go Zeke"


def test_get_roster(api, mock_roster):
    with patch.object(team.Team, "roster", return_value=mock_roster):
        return_value = api.get_roster("Too Many Cooks")
        assert isinstance(return_value, list)
        assert return_value[0]["selected_position"] == "QB"
        assert return_value[0]["name"] == "Josh Allen"


def test_get_player_owner(api):
    return_value = api.get_player_owner("30977")
    assert isinstance(return_value, str)
    assert return_value == "Hide and Go Zeke"


def test_get_player_details(api):
    return_value = api.get_player_details("Josh Allen")
    assert isinstance(return_value, dict)
    assert return_value["player_key"] == "399.p.30977"
    assert return_value["owner"] == "Hide and Go Zeke"


def test_get_matchups(api):
    week, details = api.get_matchups()
    assert isinstance(details, list)
    assert week == "1"


def test_get_matchups_category(category_api):
    week, details = category_api.get_matchups()
    assert isinstance(details, list)
    assert len(details) == 7
    assert week == "1"
