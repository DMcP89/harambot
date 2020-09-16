import logging
import json
import os
import discord

from yahoo_fantasy_api import league, game, team, yhandler
from datetime import datetime


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)



dir_path = os.path.dirname(os.path.realpath(__file__))

class Yahoo:

    oauth = None

    def __init__(self, oauth, league_id):
        self.oauth = oauth
        self.league_id = league_id

    def league(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, 'nfl')
        for id in gm.league_ids(year=datetime.today().year):
            if self.league_id in id:
                return gm.to_league(id)
        return gm.to_league(gm.league_ids(year=datetime.today().year)[0])
        
    def get_standings(self):
        embed = discord.Embed(title="Standings", description='Team Name\n W-L-T', color=0xeee657)
        for idx, team in enumerate(self.league().standings()):
            outcomes = team['outcome_totals']
            record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
            embed.add_field(name=str(idx+1) + '. '+team['name'],value=record, inline=False)
        return embed

    def get_team(self, team_name):
        for id,team in self.league().teams().items():
            if team['name'] == team_name:
                return self.league().to_team(id)
        
    def get_roster(self, team_name):
        team = self.get_team(team_name)
        roster_text= ''
        for player in team.roster(self.league().current_week()):
            roster_text = roster_text + player['selected_position']+ ': '+player['name'] + '\n'
        if not roster_text:
             return "{} roster unavailable".format(team_name)
        return roster_text

    def get_player_details(self, player_name):
        try:
            player = self.league().player_details(player_name)[0]
            player_details = {}
            player_details_text = player['name']['full'] + ' #' + player['uniform_number'] + '\n'
            player_details_text = player_details_text + "Position: "+player['primary_position']+'\n'
            player_details_text = player_details_text + "Team: "+player['editorial_team_abbr']+'\n'
            player_details_text = player_details_text + "Bye: "+player['bye_weeks']['week']+'\n'
            player_details_text = player_details_text + "Total Points: "+player['player_points']['total']+'\n'
            player_details['text'] = player_details_text
            player_details['url'] = player['image_url']
            return player_details
        except IndexError as e:
            return {}
