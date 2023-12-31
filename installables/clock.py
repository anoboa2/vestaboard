import time

DIGITS = {
  "0": [
    [70, 70, 70, 70],
    [70, 0, 0, 70],
    [70, 0, 0, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70]
  ],
  "1": [
    [0, 0, 70, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70]
  ],
  "2": [
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [70, 70, 70, 70],
    [70, 0, 0, 0],
    [70, 70, 70, 70]
  ],
  "3": [
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [70, 70, 70, 70]
  ],
  "4": [
    [70, 0, 0, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70]
  ],
  "5": [
    [70, 70, 70, 70],
    [70, 0, 0, 0],
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [70, 70, 70, 70]
  ],
  "6": [
    [70, 70, 70, 70],
    [70, 0, 0, 0],
    [70, 70, 70, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70]
  ],
  "7": [
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70],
    [0, 0, 0, 70]
  ],
  "8": [
    [70, 70, 70, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70]
  ],
  "9": [
    [70, 70, 70, 70],
    [70, 0, 0, 70],
    [70, 70, 70, 70],
    [0, 0, 0, 70],
    [70, 70, 70, 70]
  ]
}

def writeDigit(start_row, start_digit, time_value, board):
  """
  Writes a digit to the board
  Params:
    start_row: the row to start writing the digit
    start_digit: the column to start writing the digit
    time_value: the value of the digit to write
    board: the board to write the digit to
  """
  row_loc = start_row
  for row in DIGITS[str(time_value)]:
    digit_loc = start_digit
    for value in row:
      board[row_loc][digit_loc] = value
      digit_loc += 1
    row_loc += 1

  return board

def displayTime():
  """
  Displays the current time on the Vestaboard
  """
  # Initialize a blank board
  board = [[0] * 22 for _ in range(6)]

  # Parse the current time
  hr = time.strftime("%I")
  min = time.strftime("%M")
  sec = time.strftime("%S")

  # Handle hours 10, 11, 12
  if hr[0] == "1":
    board = writeDigit(1, 0, hr[0], board)

  # Write the time to the board
  board = writeDigit(1, 5, hr[1], board)
  board[2][101] = 70
  board[4][10] = 70
  board = writeDigit(1, 12, min[0], board)
  board = writeDigit(1, 17, min[1], board)

  refresh = 60000 - (int(sec) * 1000)

  return board, refresh