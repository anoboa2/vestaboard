import requests
import json
import os
from typing import Tuple, List, Dict, Any
from dotenv import load_dotenv

from installables._base import BaseInstallable
from vestaboard.models import Board, Device, Row
from vestaboard.utils import convert_to_character_code
from vestaboard.logging import get_logger

load_dotenv()

TEAMS = [
    {
        'statcastId': 108,
        'statcaseCode': 'ana',
        'name': 'Los Angeles Angels',
        'abbreviation': 'LAA',
        'color': 'red'
    },
    {
        'statcastId': 109,
        'statcaseCode': 'ari',
        'name': 'Arizona Diamondbacks',
        'abbreviation': 'AZ',
        'color': 'red'
    },
    {
        'statcastId': 110,
        'statcaseCode': 'bal',
        'name': 'Baltimore Orioles',
        'abbreviation': 'BAL',
        'color': 'orange'
    },
    {
        'statcastId': 111,
        'statcaseCode': 'bos',
        'name': 'Boston Red Sox',
        'abbreviation': 'BOS',
        'color': 'red'
    },
    {
        'statcastId': 112,
        'statcaseCode': 'chn',
        'name': 'Chicago Cubs',
        'abbreviation': 'CHC',
        'color': 'blue'
    },
    {
        'statcastId': 113,
        'statcaseCode': 'cin',
        'name': 'Cincinnati Reds',
        'abbreviation': 'CIN',
        'color': 'red'
    },
    {
        'statcastId': 114,
        'statcaseCode': 'cle',
        'name': 'Cleveland Guardians',
        'abbreviation': 'CLE',
        'color': 'blue'
    },
    {
        'statcastId': 115,
        'statcaseCode': 'col',
        'name': 'Colorado Rockies',
        'abbreviation': 'COL',
        'color': 'purple'
    },
    {
        'statcastId': 116,
        'statcaseCode': 'det',
        'name': 'Detroit Tigers',
        'abbreviation': 'DET',
        'color': 'orange'
    },
    {
        'statcastId': 117,
        'statcaseCode': 'hou',
        'name': 'Houston Astros',
        'abbreviation': 'HOU',
        'color': 'orange'
    },
    {
        'statcastId': 118,
        'statcaseCode': 'kca',
        'name': 'Kansas City Royals',
        'abbreviation': 'KC',
        'color': 'blue'
    },
    {
        'statcastId': 119,
        'statcaseCode': 'lan',
        'name': 'Los Angeles Dodgers',
        'abbreviation': 'LAD',
        'color': 'blue'
    },
    {
        'statcastId': 120,
        'statcaseCode': 'was',
        'name': 'Washington Nationals',
        'abbreviation': 'WSH',
        'color': 'red'
    },
    {
        'statcastId': 121,
        'statcaseCode': 'nyn',
        'name': 'New York Mets',
        'abbreviation': 'NYM',
        'color': 'blue'
    },
    {
        'statcastId': 133,
        'statcaseCode': 'oak',
        'name': 'Oakland Athletics',
        'abbreviation': 'OAK',
        'color': 'green'
    },
    {
        'statcastId': 134,
        'statcaseCode': 'pit',
        'name': 'Pittsburgh Pirates',
        'abbreviation': 'PIT',
        'color': 'yellow'
    },
    {
        'statcastId': 135,
        'statcaseCode': 'sdn',
        'name': 'San Diego Padres',
        'abbreviation': 'SD',
        'color': 'yellow'
    },
    {
        'statcastId': 136,
        'statcaseCode': 'sea',
        'name': 'Seattle Mariners',
        'abbreviation': 'SEA',
        'color': 'green'
    },
    {
        'statcastId': 137,
        'statcaseCode': 'sfn',
        'name': 'San Francisco Giants',
        'abbreviation': 'SF',
        'color': 'orange'
    },
    {
        'statcastId': 138,
        'statcaseCode': 'sln',
        'name': 'St. Louis Cardinals',
        'abbreviation': 'STL',
        'color': 'red'
    },
    {
        'statcastId': 139,
        'statcaseCode': 'tba',
        'name': 'Tampa Bay Rays',
        'abbreviation': 'TB',
        'color': 'green'
    },
    {
        'statcastId': 140,
        'statcaseCode': 'tex',
        'name': 'Texas Rangers',
        'abbreviation': 'TEX',
        'color': 'blue'
    },
    {
        'statcastId': 141,
        'statcaseCode': 'tor',
        'name': 'Toronto Blue Jays',
        'abbreviation': 'TOR',
        'color': 'blue'
    },
    {
        'statcastId': 142,
        'statcaseCode': 'min',
        'name': 'Minnesota Twins',
        'abbreviation': 'MIN',
        'color': 'blue'
    },
    {
        'statcastId': 143,
        'statcaseCode': 'phi',
        'name': 'Philadelphia Phillies',
        'abbreviation': 'PHI',
        'color': 'red'
    },
    {
        'statcastId': 144,
        'statcaseCode': 'atl',
        'name': 'Atlanta Braves',
        'abbreviation': 'ATL',
        'color': 'red'
    },
    {
        'statcastId': 145,
        'statcaseCode': 'cha',
        'name': 'Chicago White Sox',
        'abbreviation': 'CWS',
        'color': 'black'
    },
    {
        'statcastId': 146,
        'statcaseCode': 'mia',
        'name': 'Miami Marlins',
        'abbreviation': 'MIA',
        'color': 'orange'
    },
    {
        'statcastId': 147,
        'statcaseCode': 'nya',
        'name': 'New York Yankees',
        'abbreviation': 'NYY',
        'color': 'blue'
    },
    {
        'statcastId': 158,
        'statcaseCode': 'mil',
        'name': 'Milwaukee Brewers',
        'abbreviation': 'MIL',
        'color': 'yellow'
    }
]

TEAM_PRIORITY = [
    111,  # Red Sox
    113,  # Reds
    147,  # Yankees
    109,  # Diamondbacks
    110,  # Orioles
]

# Color mapping for team colors
COLOR_MAP = {
    'red': 63,
    'orange': 64,
    'yellow': 65,
    'green': 66,
    'blue': 67,
    'purple': 68,
    'white': 69,
    'black': 70,
    'filled': 71
}

class MLBScoresInstallable(BaseInstallable):
    def __init__(self, device: Device):
        super().__init__(
            name="MLB Scores",
            description="Displays live MLB game scores and updates",
            device=device,
            next_refresh_increment=0
        )
        # Initialize instance variables after calling super().__init__
        self._current_game_index = 0
        self._schedule = []

    def get_schedule(self) -> List[Dict[str, Any]]:
        """
        Gets the MLB schedule for the current day
        """
        mlb_resp = requests.get("http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1")
        if mlb_resp.status_code != 200:
            self.logger.error(f"Error getting MLB schedule: HTTP {mlb_resp.status_code}")
            return []

        data = mlb_resp.json()
        games = data['dates'][0]['games']
        vb_game_info = [{
            'gameId': game['gamePk'], 
            'homeTeamId': game['teams']['home']['team']['id'], 
            'awayTeamId': game['teams']['away']['team']['id'], 
            'datetime': game['gameDate']
        } for game in games]

        self.logger.info(f"Retrieved {len(vb_game_info)} games from MLB schedule")
        return vb_game_info

    def game_prioritizer(self, schedule: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Takes a list of games and rotates the order based on the team priority.
        Args:
            schedule: list of games
        """
        # Split the games into priority and non-priority based on the hardcoded global priority list
        priority_games = []
        for game in schedule:
            if game['homeTeamId'] in TEAM_PRIORITY or game['awayTeamId'] in TEAM_PRIORITY:
                priority_games.append(game)
        
        non_priority_games = []
        for game in schedule:
            if game['homeTeamId'] not in TEAM_PRIORITY and game['awayTeamId'] not in TEAM_PRIORITY:
                non_priority_games.append(game)
        
        # Sort the priority games by the priority list and the non-priority games by the datetime
        priority_games = sorted(priority_games, key=lambda k: TEAM_PRIORITY.index(k['homeTeamId']) if k['homeTeamId'] in TEAM_PRIORITY else TEAM_PRIORITY.index(k['awayTeamId']))
        non_priority_games = sorted(non_priority_games, key=lambda k: k['datetime'])

        return priority_games + non_priority_games

    def get_live_game_feed(self, game_pk: int) -> Tuple[Board, int]:
        """
        Gets the live feed for a game
        Args:
            game_pk: the game id
        """
        mlb_resp = requests.get(f"http://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live")
        if mlb_resp.status_code != 200:
            self.logger.error(f"Error getting MLB feed for game {game_pk}: HTTP {mlb_resp.status_code}")
            return self.device.create_board(), 15000
        
        data = mlb_resp.json()

        # Parse data for the home and away teams
        home_team_id = data['gameData']['teams']['home']['id']
        home_team = [team for team in TEAMS if team['statcastId'] == home_team_id][0]
        home_score = data['liveData']['linescore']['teams']['home']['runs']
        away_team_id = data['gameData']['teams']['away']['id']
        away_team = [team for team in TEAMS if team['statcastId'] == away_team_id][0]
        away_score = data['liveData']['linescore']['teams']['away']['runs']

        # Parse data for the last play
        lookback = -1
        last_play = data['liveData']['plays']['allPlays'][lookback]

        # Parse data for the last play
        batter = last_play['matchup']['batter']['fullName']
        batter = batter.split(" ")[-1]
        pitcher = last_play['matchup']['pitcher']['fullName']
        pitcher = pitcher.split(" ")[-1]
        inning = last_play['about']['inning']
        inning_half = last_play['about']['halfInning'][0]
        game_over = data['gameData']['status']['abstractGameState'] == "Final"
        outs = last_play['count']['outs']

        try:
            last_play_description = last_play['result']['description']
        except KeyError:
            last_play_description = ""

        self.logger.debug(f"Game {game_pk}: {batter} vs {pitcher}, {inning}{inning_half}, {outs} outs", 
                         game_pk=game_pk, batter=batter, pitcher=pitcher, inning=inning, 
                         inning_half=inning_half, outs=outs, last_play=last_play_description)

        # Create board
        board = self.device.create_board(message=[], duration=None)

        # Construct the first line, which will display the score and inning
        line_1_string = f" {away_team['abbreviation']} {away_score} @ {home_team['abbreviation']} {home_score}"
        line_1_chars = convert_to_character_code([char for char in line_1_string])
        
        # Add team colors
        line_1_chars.insert(1, COLOR_MAP[away_team['color']])
        at_index = line_1_string.find('@')
        if at_index != -1:
            line_1_chars.insert(at_index + 2, COLOR_MAP[home_team['color']])
        
        line_1 = self.device.create_row(index=0, line=line_1_chars, align="left")
        line_1.pad_line()

        # Add inning indicator
        if data['gameData']['status']['abstractGameState'] == "Final":
            line_1.line[-3] = 37  # "F" character
        else:
            line_1.line[-3] = ord(inning_half.upper()) - ord('A') + 1  # Convert A->1, B->2, etc.
            if len(str(inning)) == 1:
                line_1.line[-2] = int(str(inning)) + 26  # Numbers start at 27
            else:
                line_1.line[-2] = int(str(inning)[0]) + 26
                line_1.line[-1] = int(str(inning)[1]) + 26

        # Construct the second line, which will display the pitcher
        line_2_string = f"P: {pitcher}"
        line_2_chars = convert_to_character_code([char for char in line_2_string])
        line_2 = self.device.create_row(index=1, line=line_2_chars, align="left")
        line_2.pad_line()

        # Construct the third line, which will display the batter
        line_3_string = f"B: {batter}"
        line_3_chars = convert_to_character_code([char for char in line_3_string])
        line_3 = self.device.create_row(index=2, line=line_3_chars, align="left")
        line_3.pad_line()

        # Construct the fourth line, which will display the last play
        line_4_string = f"Last...          {outs} out"
        line_4_chars = convert_to_character_code([char for char in line_4_string])
        line_4 = self.device.create_row(index=3, line=line_4_chars, align="left")
        line_4.pad_line()

        # Construct the fifth and sixth lines, which will display the last play
        short_description = last_play_description.split(",")
        if len(short_description[0]) <= 22:
            line_5_string = f"{short_description[0]}"
            line_6_string = ""
        else:
            # Simple line splitting for long descriptions
            words = short_description[0].split()
            line_5_string = ""
            line_6_string = ""
            for word in words:
                if len(line_5_string) + len(word) + 1 <= 22:
                    line_5_string += word + " "
                else:
                    line_6_string += word + " "
        
        line_5_chars = convert_to_character_code([char for char in line_5_string])
        line_5 = self.device.create_row(index=4, line=line_5_chars, align="left")
        line_5.pad_line()
        
        line_6_chars = convert_to_character_code([char for char in line_6_string])
        line_6 = self.device.create_row(index=5, line=line_6_chars, align="left")
        line_6.pad_line()

        # Add all rows to the board
        board.message = [line_1, line_2, line_3, line_4, line_5, line_6]

        self.logger.info(f"Generated board for {away_team['abbreviation']} @ {home_team['abbreviation']}: {away_score}-{home_score}", 
                        away_team=away_team['abbreviation'], home_team=home_team['abbreviation'], 
                        away_score=away_score, home_score=home_score, game_pk=game_pk)

        return board, 15000

    def generate_board(self) -> Tuple[Board, int]:
        """
        Generate a new board for the Vestaboard.
        
        Returns:
            Tuple[Board, int]: A tuple containing the board and the next refresh time in milliseconds
        """
        # Get schedule if we don't have one
        if not self._schedule:
            self._schedule = self.get_schedule()
            if not self._schedule:
                self.logger.warning("No games found in schedule, waiting 1 minute")
                return self.device.create_board(), 60000  # Wait 1 minute if no games
        
        # Prioritize games
        prioritized_schedule = self.game_prioritizer(self._schedule)
        
        if not prioritized_schedule:
            self.logger.warning("No prioritized games found, waiting 1 minute")
            return self.device.create_board(), 60000
        
        # Get current game
        current_game = prioritized_schedule[self._current_game_index % len(prioritized_schedule)]
        
        self.logger.debug(f"Processing game {self._current_game_index + 1}/{len(prioritized_schedule)}: {current_game['gameId']}", 
                         game_index=self._current_game_index, total_games=len(prioritized_schedule), game_id=current_game['gameId'])
        
        # Get live feed for current game
        board, refresh = self.get_live_game_feed(current_game['gameId'])
        
        # Move to next game
        self._current_game_index = (self._current_game_index + 1) % len(prioritized_schedule)
        
        return board, refresh

    def should_update(self) -> bool:
        """
        Determine if the board should be updated.
        For MLB scores, we always want to update to get the latest game information.
        
        Returns:
            bool: True if the board should be updated
        """
        return True





