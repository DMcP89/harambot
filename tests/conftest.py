import os
import json
import pytest

from unittest.mock import MagicMock, patch
from harambot.yahoo_api import Yahoo
from yahoo_fantasy_api import game, League, Team

root_path = os.path.dirname(os.path.realpath(__file__))


def load_test_data(filename):
    with open(root_path + "/" + filename, "r") as f:
        test_data = json.load(f)
        f.close()
    return test_data


@pytest.fixture
def mock_oauth():
    oauth = MagicMock()
    oauth.token_is_valid.return_value = True
    return oauth


@pytest.fixture
def mock_standings():
    return load_test_data("test-standings.json")["standings"]


@pytest.fixture
def mock_teams():
    return load_test_data("test-teams.json")


@pytest.fixture
def mock_roster():
    return load_test_data("test-roster.json")["roster"]


@pytest.fixture
def mock_player_details():
    return load_test_data("test-player-details.json")["details"]


@pytest.fixture
def mock_player_stats():
    return [{"mock": "stats"}]


@pytest.fixture
def mock_ownership():
    return load_test_data("test-player-details.json")["ownership"]


@pytest.fixture
def mock_matchups():
    return load_test_data("test-matchups.json")


@pytest.fixture
def mock_matchups_category():
    return load_test_data("test-matchups-category.json")


@pytest.fixture
def api(
    mock_oauth,
    mock_standings,
    mock_teams,
    mock_player_details,
    mock_player_stats,
    mock_ownership,
    mock_matchups,
):
    api = Yahoo()
    api.scoring_type = "head"
    league = None
    with patch.object(game.Game, "game_id", return_value="319"):
        league = League(mock_oauth, 123456)
        league.standings = MagicMock(return_value=mock_standings)
        league.teams = MagicMock(return_value=mock_teams)
        league.current_week = MagicMock(return_value=1)
        league.player_details = MagicMock(return_value=mock_player_details)
        league.player_stats = MagicMock(return_value=mock_player_stats)
        league.ownership = MagicMock(return_value=mock_ownership)
        league.matchups = MagicMock(return_value=mock_matchups)
        league.get_team = MagicMock(
            return_value={"Too Many Cooks": Team(mock_oauth, "")}
        )
    api.league = MagicMock(return_value=league)
    return api


@pytest.fixture
def category_api(
    mock_oauth,
    mock_standings,
    mock_teams,
    mock_player_details,
    mock_player_stats,
    mock_ownership,
    mock_matchups_category,
):
    api = Yahoo()
    api.scoring_type = "headone"
    league = None
    with patch.object(game.Game, "game_id", return_value="319"):
        league = League(mock_oauth, 123456)
        league.standings = MagicMock(return_value=mock_standings)
        league.teams = MagicMock(return_value=mock_teams)
        league.current_week = MagicMock(return_value=1)
        league.player_details = MagicMock(return_value=mock_player_details)
        league.player_stats = MagicMock(return_value=mock_player_stats)
        league.ownership = MagicMock(return_value=mock_ownership)
        league.matchups = MagicMock(return_value=mock_matchups_category)
    api.league = MagicMock(return_value=league)
    return api
