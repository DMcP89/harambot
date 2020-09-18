import logging
import os
import discord
import objectpath

from yahoo_fantasy_api import league, game, team, yhandler
from datetime import datetime
from cachetools import cached, TTLCache


logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)



dir_path = os.path.dirname(os.path.realpath(__file__))

class Yahoo:

    oauth = None

    def __init__(self, oauth, league_id):
        self.oauth = oauth
        self.league_id = league_id

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def league(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, 'nfl')
        return gm.to_league('{}.l.{}'.format(gm.game_id(), self.league_id))
        # for id in gm.league_ids(year=datetime.today().year):
        #     if self.league_id in id:
        #         return gm.to_league(id)
        # return gm.to_league(gm.league_ids(year=datetime.today().year)[0])
        
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        embed = discord.Embed(title="Standings", description='Team Name\n W-L-T', color=0xeee657)
        for idx, team in enumerate(self.league().standings()):
            outcomes = team['outcome_totals']
            record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
            embed.add_field(name=str(idx+1) + '. '+team['name'],value=record, inline=False)
        return embed

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, team_name):
        for id,team in self.league().teams().items():
            if team['name'] == team_name:
                return self.league().to_team(id)
        
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        team = self.get_team(team_name)
        roster_text= ''
        for player in team.roster(self.league().current_week()):
            roster_text = roster_text + player['selected_position']+ ': '+player['name'] + '\n'
        if not roster_text:
             return "{} roster unavailable".format(team_name)
        return roster_text

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
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

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_matchups(self):
        embed = discord.Embed(title="Matchups for Week {}".format(str(self.league().current_week())), description='', color=0xeee657)
        matchups_json = objectpath.Tree(self.league().matchups())
        matchups = matchups_json.execute('$..scoreboard..matchups..matchup..teams')
        for matchup in matchups:
            team1 = matchup["0"]["team"]
            team1_name = team1[0][2]["name"]
            team1_actual_points = team1[1]['team_points']['total']
            team1_projected_points = team1[1]['team_projected_points']['total']
            team1_win_probability = "{:.0%}".format(team1[1]['win_probability'])
            team1_details = '***{}*** \n Projected Score: {} \n  Actual Score: {} \n Win Probability: {} \n'.format(team1_name, team1_projected_points, team1_actual_points, team1_win_probability)
            team2 = matchup["1"]["team"]
            team2_name = team2[0][2]["name"]
            team2_actual_points = team2[1]['team_points']['total']
            team2_projected_points = team2[1]['team_projected_points']['total']
            team2_win_probability = "{:.0%}".format(team2[1]['win_probability'])
            team2_details = '\n***{}*** \n Projected Score: {} \n  Actual Score: {} \n Win Probability: {}\n'.format(team2_name, team2_projected_points, team2_actual_points, team2_win_probability)
            divider = '--------------------------------------'
            embed.add_field(name="{} vs {}".format(team1_name, team2_name), value=team1_details + team2_details+divider, inline=False)
        return embed