import spotipy
from math import ceil
from spotipy.oauth2 import SpotifyOAuth
from unidecode import unidecode
import transform_functions as vb
from dotenv import load_dotenv

load_dotenv()

# Some configuration for the Spotify API using the spotipy library
scope = "user-read-currently-playing"
sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def getSongFromSpotify(current_message):
  """
  Gets the current song from Spotify and returns a board with the song name and artist name(s)
  Params:
    current_message: the current message on the board
  """

  # Add some padding and embellishments to the top of the board
  header = ["GREEN", " ", " ", " ", " ", "N", "O", "w", " ", "P", "L", "A", "Y", "I", "N", "G", " ", " ", " ", " ", " ", "GREEN"]
  board = []

  header = vb.convertToCharacterCode(header)

  design = [
    [66, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 66, 66],
    header,
    [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  ]
  board += design

  # Get the current song from Spotify and handle edge cases
  try:
    current_song = sp.current_user_playing_track()
    if current_song == None:
      print("No song currently playing")
      return current_message, 15000
    if current_song['is_playing'] == False:
      print("No song currently playing")
      return current_message, 15000
  except spotipy.exceptions.SpotifyException as e:
    print(e)
    return current_message, 15000

  # Parse the artist and song name from the Spotify response
  artists = [unidecode(artist['name']) for artist in current_song['item']['artists']]
  song = unidecode(current_song['item']['name'])
  refresh = (current_song['item']['duration_ms'] - current_song['progress_ms']) + 1000

  # Construct the song and artist name lines and add them to the board
  line1 = vb.convertToCharacterCode(song)
  line1 = vb.padRow(line1)
  print(song)
  line2, line3 = spaceArtists(artists)
  line2 = vb.convertToCharacterCode(line2)
  line2 = vb.padRow(line2)
  line3 = vb.convertToCharacterCode(line3)
  line3 = vb.padRow(line3)

  board.append(line1[0:22])
  board.append(line2[0:22])
  board.append(line3[0:22])

  print("Will refresh in " + str(refresh / 1000) + " seconds")

  return board, refresh


def spaceArtists(artists_list):
  """
  Takes a list of artists and returns a string with a comma and space between each artist.
  Evaluates the length of the string and adds spaces to the end to support Vestaboard's character line limit.
  """
  artists_line1 = []
  artists_line2 = []

  for artist in artists_list:
    if sum([len(artists) for artists in artists_line1]) < 22:
      artists_line1.append(artist)
    else:
      artists_line2.append(artist)
    
  artists_line1_string = ", ".join(artists_line1)
  artists_line2_string = ", ".join(artists_line2)
  
  return artists_line1_string, artists_line2_string



