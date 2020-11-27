from unittest.mock import patch
from yahoo_fantasy_api import team
from discord import Embed





def test_league(api):
    assert api.league()

def test_get_standings(api):
    return_value = api.get_standings()
    assert isinstance(return_value, Embed)
    assert len(return_value.fields) == 3
    assert return_value.fields[0].name == '1. Hide and Go Zeke'
    
def test_get_team(api):
    return_value = api.get_team('Too Many Cooks')
    assert isinstance(return_value, team.Team) 
    assert return_value.team_key == '399.l.710921.t.9'

def test_get_roster(api, mock_roster):
    with patch.object(team.Team, 'roster', return_value=mock_roster):
        return_value = api.get_roster('Too Many Cooks')
        assert isinstance(return_value, Embed)
        assert return_value.fields[0].name == 'QB'
        assert return_value.fields[0].value == 'Josh Allen'

def test_get_player_owner(api):
    return_value = api.get_player_owner('30977')
    assert isinstance(return_value, str)
    assert return_value == 'Hide and Go Zeke'

def test_get_player_details(api):
    return_value = api.get_player_details('Josh Allen')
    assert isinstance(return_value, dict)
    assert isinstance(return_value['embed'], Embed)
    assert len(return_value['embed'].fields) == 5   
    assert isinstance(return_value['text'], str)

def test_get_matchups(api):
    return_value = api.get_matchups()
    assert isinstance(return_value, Embed)
    assert len(return_value.fields) == 6
