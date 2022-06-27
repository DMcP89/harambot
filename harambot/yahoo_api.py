import logging
import os
import discord
import objectpath

from yahoo_fantasy_api import league, game, team, yhandler
from cachetools import cached, TTLCache

logger = logging.getLogger()
logger.setLevel(logging.INFO)
logging.disable(logging.DEBUG)

# standings <year>
# champion <year>
# champions
# loser <year>
# losers
# keeper (draft results)
# last_place
# rules
# Update player details with %owned and status

dir_path = os.path.dirname(os.path.realpath(__file__))

class Yahoo:

    oauth = None

    def __init__(self, oauth, league_id, league_type):
        self.oauth = oauth
        self.league_id = league_id
        self.league_type = league_type

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def league(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        return gm.to_league('{}.l.{}'.format(gm.game_id(), self.league_id))
        

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_test(self):
        if not self.oauth.token_is_valid():
            self.oauth.refresh_access_token()
        gm = game.Game(self.oauth, self.league_type)
        names = ''
        leagues = gm.league_ids(2020)[0]
        #for league in leagues:
        #    l = gm.to_league(league)
        #    names += '\n' + l.settings()['name'] + ' - ' + l.settings()['season'] + ' ' + l.settings()['league_key']
        l = gm.to_league(leagues)
        player = l.draft_results()[0]
        results = self.get_player_details(player['player_id'])
        return results

    # Mobile embeds cannot do inline, so let's try ljust
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_standings(self):
        try:
            # standings_dict = {}
            description = ''
            for idx, team in enumerate(self.league().standings()):
                outcomes = team['outcome_totals']
                record = '({}-{}-{})'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
                # embed.add_field(name='{}. {} {}'.format(str(idx+1), team['name'].ljust(24, '.'), record), value='\u200b', inline=False)
                description += '**{}. {}** _{}_\n'.format(str(idx+1), team['name'], record)
            embed = discord.Embed(title="Standings", description=description, color=0xeee657)
            return embed
            
            # If Discord ever allows inline embeds on mobile, this format is much better
            
            #for idx, team in enumerate(self.league().standings()):
            #    outcomes = team['outcome_totals']
            #    record = '{}-{}-{}'.format(outcomes['wins'], outcomes['losses'], outcomes['ties'])
            #    standings_dict[str(idx+1) + '. ' + team['name']] = record
            #teams_string = ''
            #records_string = ''
            #for k,v in standings_dict.items():
            #    teams_string += k + '\n'
            #    records_string += v + '\n'
            #embed.add_field(name="Team", value=teams_string)
            #embed.add_field(name="Record", value=records_string)
            #return embed
        except Exception:
            logger.exception("Error while fetching standings for league {}".format(self.league_id))
            return None

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_team(self, team_name):
        try:
            for id,team in self.league().teams().items():
                if team['name'] == team_name:
                    return self.league().to_team(id)
        except Exception:
            logger.exception("Error while fetching team: {} from league: {}".format(team_name, self.league_id))
            return None
        
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_roster(self, team_name):
        team = self.get_team(team_name)
        if team:
            embed = discord.Embed(title="{}'s Roster".format(team_name), description='', color=0xeee657)
            roster = {}
            for player in team.roster(self.league().current_week()):
                roster[player['selected_position']] = player['name']
            positions = ''
            players = ''
            if roster:
                for k,v in roster.items():
                    positions += k + '\n'
                    players += v + '\n'
            else:
                positions = 'Empty'
                players = 'Empty'
            embed.add_field(name="Position", value=positions)
            embed.add_field(name="Player", value=players)
            return embed
        else:
            return None


    # player_keeper
    # player_id
    # name['full']
    # editorial_team_full_name
    # editorial_team_abbr
    # bye_weeks
    # is_keeper
    # bye_weeks
    # uniform_number
    # display_position / primary_position
    # headshot[url]
    # image_url
    # player_points[total]
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_details(self, player_name):
        try:
            player = self.league().player_details(player_name)[0]
            logger.info(player)
            print(player)
            embed = discord.Embed(title=player['name']['full'], description='#{} - {}'.format(player['uniform_number'], player['editorial_team_full_name']), color=0xeee657)
            embed.add_field(name="Postion", value=player['primary_position'])
            #embed.add_field(name="Team", value=player['editorial_team_abbr'])
            if 'bye_weeks' in player:
                embed.add_field(name="Bye", value=player['bye_weeks']['week'])
            embed.add_field(name="Total Points", value=player['player_points']['total'])
#            embed.add_field(name="% Owned", value=player['percent_owned'])
#            if 'status' in player:
#                embed.add_field(name="Status", value=player['status'])
            embed.add_field(name="Owner", value=self.get_player_owner(player['player_id']))
            # embed.set_image
            embed.set_thumbnail(url=player['image_url'])
            
            # TODO: i think we can get rid of text??
            player_details_text = player['name']['full'] + ' #' + player['uniform_number'] + '\n'
            player_details_text = player_details_text + "Position: "+player['primary_position']+'\n'
            player_details_text = player_details_text + "Team: "+player['editorial_team_abbr']+'\n'
            if 'bye_weeks' in player:
                player_details_text = player_details_text + "Bye: "+player['bye_weeks']['week']+'\n'
            player_details_text = player_details_text + "Total Points: "+player['player_points']['total']+'\n'
            player_details_text = player_details_text + "Owner: " + self.get_player_owner(player['player_id'])
            
            player_details = {}
            player_details['embed'] = embed
            player_details['text'] = player_details_text
            return player_details
        except Exception as e:
            logger.exception("Error while fetching player details for player: {} in league {}".format(player_name, self.league_id))
            return None
    
    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_player_owner(self, player_id):
        try:
            player_ownership = self.league().ownership([player_id])[str(player_id)]
            if 'owner_team_name' in player_ownership:
                return player_ownership['owner_team_name']
            else:
                ownership_map = {
                    "freeagents": "Free Agent",
                    "waivers":    "On Waviers"      
                }
                return ownership_map.get(player_ownership['ownership_type'], "")
        except Exception:
            logger.exception("Error while fetching ownership for player id: {} in league {}".format(player_id, self.league_id))
            return None

        


    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_matchups(self):
        try:
            embed = discord.Embed(title="Matchups for Week {}".format(str(self.league().current_week())), description='', color=0xeee657)
            matchups_json = objectpath.Tree(self.league().matchups())
            matchups = matchups_json.execute('$..scoreboard..matchups..matchup..teams')
            for matchup in matchups:
                team1 = matchup["0"]["team"]
                team1_name = team1[0][2]["name"]
                team1_actual_points = team1[1]['team_points']['total']
                team1_projected_points = team1[1]['team_projected_points']['total']
                if 'win_probability' in team1[1]:
                    team1_win_probability = "{:.0%}".format(team1[1]['win_probability'])
                    team1_details = 'Score: {}\nWin Probability: {}\n'.format(team1_actual_points, team1_win_probability)
                else:
                    team1_details = 'Score: {}\n'.format(team1_actual_points)
                team2 = matchup["1"]["team"]
                team2_name = team2[0][2]["name"]
                team2_actual_points = team2[1]['team_points']['total']
                team2_projected_points = team2[1]['team_projected_points']['total']
                if 'win_probability' in team2[1]:
                    team2_win_probability = "{:.0%}".format(team2[1]['win_probability'])
                    team2_details = 'Score: {}\nWin Probability: {}\n'.format(team2_actual_points, team2_win_probability)
                else:
                    team2_details = 'Score: {}\n'.format(team2_actual_points)
                divider = r'\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_\_'
                embed.add_field(name='{} (Proj. {})'.format(team1_name, team1_projected_points), value=team1_details, inline=False)
                embed.add_field(name='{} (Proj. {})'.format(team2_name, team1_projected_points), value=team2_details+divider, inline=False)
            return embed
        except Exception:
            logger.exception("Error while fetching matchups for league: {}".format(self.league_id))

    @cached(cache=TTLCache(maxsize=1024, ttl=600))
    def get_latest_trade(self):
        try:
            for key, values in self.league().teams().items():
                if 'is_owned_by_current_login' in values:
                    team = self.league().to_team(key)
                    accepted_trades = list(filter(lambda d: d['status'] == 'accepted', team.proposed_trades()))
                    if accepted_trades:
                        return accepted_trades[0]
            return
        except Exception:
            logger.exception("Error while fetching latest trade")
