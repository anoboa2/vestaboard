import os
import json
import time
import requests
from installables import plant_reminder as pr
from installables import spotify as sp
from installables import mlb_scores as mlb
from installables import clock as cl
from dotenv import load_dotenv

load_dotenv()

VESTABOARD_API_KEY = os.getenv("VESTABOARD_API_KEY")
PLANTREMINDER_INSTALLABLE_KEY = os.getenv("PLANTREMINDER_INSTALLABLE_KEY")
PLANTREMINDER_INSTALLABLE_SECRET = os.getenv("PLANTREMINDER_INSTALLABLE_SECRET")

active_message = []
mlb_cache = 0

def createBoard(app: str, active_message, mlb_cache = mlb_cache):
  if app == "plants":
    plants = ["Banana Plant", "Lipstick Plant", "Large Pothos", "Palm", "Birds of Paradise"]
    board = pr.plantReminder(plants)
    return board, 60000 * 15
  elif app == "weather":
    print("Weather app not yet implemented")
    exit()
  elif app == "clock":
    board, refresh = cl.displayTime()
    return board, refresh
  elif app == "spotify":
    board, refresh = sp.getSongFromSpotify(active_message)
    return board, refresh
  elif app == "mlb":
    schedule = mlb.getSchedule()
    board, refresh = mlb.getLiveGameFeed(schedule[mlb_cache]['gameId'])
    if board != active_message:
      mlb_cache = (mlb_cache + 1) % len(schedule)
      return board, 60000
    else:
      mlb_cache = (mlb_cache + 1) % len(schedule)
      return active_message, 15000
    

    # board, refresh = mlb.getLiveGameFeed('717794')
    # return board, refresh
  else:
    print("No app found")
    exit()


def updateBoard(board):
  print("Sending the following board to Vestaboard:")
  print(board)
  r = requests.post(
    url = "https://rw.vestaboard.com/",
    headers={"X-Vestaboard-Read-Write-Key": VESTABOARD_API_KEY}, # type: ignore
    json=board
  )

  print(r, r.text)


if __name__ == "__main__":
  while True:
    board, refresh = createBoard("spotify", active_message)
    if board == active_message:
      print("No update to board")
    else:
      updateBoard(board)
      active_message = board
    time.sleep(refresh / 1000)
 