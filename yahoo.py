from yahoo_oauth import OAuth2
from yahoo_fantasy_api import league, game, team
from datetime import datetime

oauth = OAuth2(None, None, from_file='oauth2.json')

gm = game.Game(oauth, 'nfl')
league_id = gm.league_ids(year=datetime.today().year)[0]
league = gm.to_league(league_id)

def refresh_access_token():
    if not oauth.token_is_valid():
        oauth.refresh_access_token()


def get_standings():
    standings_text = ''
    for idx, team in enumerate(league.standings()):
        standings_text = standings_text + str(idx+1) + '. '+team+'\n'
    return standings_text

def get_team(team_name):
    target_team = None
    for team in league.teams():
        if team['name'] == team_name:
            target_team = league.to_team(team['team_key'])
    return target_team

def get_roster(team_name):
    team = get_team(team_name)
    roster_text= ''
    for player in team.roster(league.current_week()):
        roster_text = roster_text + player['selected_position']+ ': '+player['name']
    return roster_text

#print(get_roster("Dave's Team"))
#print(get_standings())
