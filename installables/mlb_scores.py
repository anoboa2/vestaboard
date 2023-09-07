import requests
import json
import os
import transform_functions as vb
from dotenv import load_dotenv

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
  111, # Red Sox
  113, # Reds
  147, # Yankees
  109, # Diamondbacks
  110, # Orioles
]

def getSchedule():
  mlb_resp = requests.get("http://statsapi.mlb.com/api/v1/schedule/games/?sportId=1")
  if mlb_resp.status_code != 200:
    print("Error getting MLB schedule")
    exit()

  data = mlb_resp.json()

  games = data['dates'][0]['games']
  vb_game_info = [{'gameId': game['gamePk'], 'homeTeamId': game['teams']['home']['team']['id'], 'awayTeamId': game['teams']['away']['team']['id'], 'datetime': game['gameDate']} for game in games]

  return vb_game_info


def gamePrioritizer(schedule):
  """
  Takes a list of games and rotates the order based on the team priority
  """
  priority_games = []
  for game in schedule:
    if game['homeTeamId'] in TEAM_PRIORITY or game['awayTeamId'] in TEAM_PRIORITY:
      priority_games.append(game)
  
  non_priority_games = []
  for game in schedule:
    if game['homeTeamId'] not in TEAM_PRIORITY and game['awayTeamId'] not in TEAM_PRIORITY:
      non_priority_games.append(game)
  
  priority_games = sorted(priority_games, key=lambda k: TEAM_PRIORITY.index(k['homeTeamId']) if k['homeTeamId'] in TEAM_PRIORITY else TEAM_PRIORITY.index(k['awayTeamId']))
  non_priority_games = sorted(non_priority_games, key=lambda k: k['datetime'])

  return priority_games + non_priority_games


def getLiveGameFeed(game_pk):
  mlb_resp = requests.get(f"http://statsapi.mlb.com/api/v1.1/game/{game_pk}/feed/live")
  if mlb_resp.status_code != 200:
    print("Error getting MLB feed")
    exit()
  
  data = mlb_resp.json()

  home_team_id = data['gameData']['teams']['home']['id']
  home_team = [team for team in TEAMS if team['statcastId'] == home_team_id][0]
  home_score = data['liveData']['linescore']['teams']['home']['runs']
  away_team_id = data['gameData']['teams']['away']['id']
  away_team = [team for team in TEAMS if team['statcastId'] == away_team_id][0]
  away_score = data['liveData']['linescore']['teams']['away']['runs']

  lookback = -1
  last_play = data['liveData']['plays']['allPlays'][lookback]

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

  print(batter, pitcher, last_play_description, inning, inning_half, outs)

  # Construct the first line, which will display the score and inning
  line_1_string = f" {away_team['abbreviation']} {away_score} @ {home_team['abbreviation']} {home_score}"
  line_1 = vb.convertToCharacterCode(line_1_string)
  line_1.insert(1, int(vb.COLORS[away_team['color']]))
  line_1.insert(int(line_1.index(38) + 2), int(vb.COLORS[home_team['color']]))
  line_1 = vb.padRow(line_1, align="left")
  if data['gameData']['status']['abstractGameState'] == "Final":
    line_1[-3] = vb.CHARACTERS["F"]
  else:
    line_1[-3] = vb.CHARACTERS[inning_half.upper()]
    if len(str(inning)) == 1:
      line_1[-2] = vb.CHARACTERS[str(inning)]
    else:
      line_1[-2] = vb.CHARACTERS[str(inning)[0]]
      line_1[-1] = vb.CHARACTERS[str(inning)[1]]

  # Construct the second line, which will display the pitcher
  line_2_string = f"P: {pitcher}"
  line_2 = vb.convertToCharacterCode(line_2_string)
  line_2 = vb.padRow(line_2, align="left")

  # Construct the third line, which will display the batter
  line_3_string = f"B: {batter}"
  line_3 = vb.convertToCharacterCode(line_3_string)
  line_3 = vb.padRow(line_3, align="left")

  # Construct the fourth line, which will display the last play
  line_4_string = f"Last...          {outs} out"
  line_4 = vb.convertToCharacterCode(line_4_string)

  # Construct the fifth and sixth lines, which will display the last play
  short_description = last_play_description.split(",")
  if len(short_description[0]) <= 22:
    line_5_string = f"{short_description[0]}"
    line_6_string = ""
  else:
    line_5_string = vb.parseToLines(short_description[0])[0]
    line_6_string = vb.parseToLines(short_description[0])[1]
  
  line_5 = vb.convertToCharacterCode(line_5_string)
  line_5 = vb.padRow(line_5, align="left")
  line_6 = vb.convertToCharacterCode(line_6_string)
  line_6 = vb.padRow(line_6, align="left")

  # if last_play['postOnFirst'] == True:
  #   line_3[-2] = vb.CHARACTERS['FILLED']
  # else:
  #   line_3[-2] = vb.CHARACTERS['.']

  # if last_play['postOnSecond'] == True:
  #   line_2[-3] = vb.CHARACTERS['FILLED']
  # else:
  #   line_2[-3] = vb.CHARACTERS['.']

  # if last_play['postOnThird'] == True:
  #   line_3[-4] = vb.CHARACTERS['FILLED']
  # else:
  #   line_3[-4] = vb.CHARACTERS['.']
  

  board = [line_1, line_2, line_3, line_4, line_5, line_6]

  return board, 15000





