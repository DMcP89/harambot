import logging
import json
import os

from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league, game, team
from datetime import datetime



#logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)

dir_path = os.path.dirname(os.path.realpath(__file__))

oauth = OAuth2(None, None, from_file=dir_path+'/oauth2.json')

gm = game.Game(oauth, 'nfl')
league_id = gm.league_ids(year=datetime.today().year)[0]
league = gm.to_league(league_id)

def refresh_access_token():
    print("Refreshing token")
    if not oauth.token_is_valid():
        oauth.refresh_access_token()
        gm = game.Game(oauth, 'nfl')


def get_standings():
    refresh_access_token()
    standings_text = ''
    for idx, team in enumerate(league.standings()):
        standings_text = standings_text + str(idx+1) + '. '+team+'\n'
    return standings_text

def get_team(team_name):
    refresh_access_token()
    target_team = None
    for team in league.teams():
        if team['name'] == team_name:
            target_team = league.to_team(team['team_key'])
    return target_team

def get_roster(team_name):
    team = get_team(team_name)
    roster_text= ''
    for player in team.roster(league.current_week()):
        roster_text = roster_text + player['selected_position']+ ': '+player['name'] + '\n'
    return roster_text

def get_player_details(player_name):
    player = league.player_details(player_name)
    player_details = {}
    player_details_text = player['name']['full'] + ' #' + player['uniform_number'] + '\n'
    player_details_text = player_details_text + "Position: "+player['primary_position']+'\n'
    player_details_text = player_details_text + "Team: "+player['editorial_team_abbr']+'\n'
    player_details_text = player_details_text + "Bye: "+player['bye_weeks']['week']+'\n'
    player_details_text = player_details_text + "Total Points: "+player['player_points']['total']+'\n'
    player_details['text'] = player_details_text
    player_details['url'] = player['image_url']
    return player_details


#print(get_player_details("Drew Brees"))
#print(get_roster("Matural Ice"))
#print(get_standings())
