COLUMNS = 22
ROWS = 6
CHARACTERS = {
  ' ': '0',
  'A': '1',
  'B': '2',
  'C': '3',
  'D': '4',
  'E': '5',
  'F': '6',
  'G': '7',
  'H': '8',
  'I': '9',
  'J': '10',
  'K': '11',
  'L': '12',
  'M': '13',
  'N': '14',
  'O': '15',
  'P': '16',
  'Q': '17',
  'R': '18',
  'S': '19',
  'T': '20',
  'U': '21',
  'V': '22',
  'W': '23',
  'X': '24',
  'Y': '25',
  'Z': '26',
  '1': '27',
  '2': '28',
  '3': '29',
  '4': '30',
  '5': '31',
  '6': '32',
  '7': '33',
  '8': '34',
  '9': '35',
  '0': '36',
  '!': '37',
  '@': '38',
  '#': '39',
  '$': '40',
  '(': '41',
  ')': '42',
  '-': '44',
  '+': '46',
  '&': '47',
  '=': '48',
  ';': '49',
  ':': '50',
  "'": '52',
  '"': '53',
  '%': '54',
  ',': '55',
  '.': '56',
  '/': '59',
  '?': '60',
  '•': '62',
  'RED': '63',
  'ORANGE': '64',
  'YELLOW': '65',
  'GREEN': '66',
  'BLUE': '67',
  'PURPLE': '68',
  'WHITE': '69',
  'BLACK': '70',
  'FILLED': '71',
}
COLORS = {
  'red': '63',
  'orange': '64',
  'yellow': '65',
  'green': '66',
  'blue': '67',
  'purple': '68',
  'white': '69',
  'black': '70',
  'filled': '71',
}
BLANK_LINE = [0] * COLUMNS

def parseToLines(text: str):
  """
  Takes a string and splits it into a list of strings that are no longer than the max number of columns on the Vestaboard
  """
  split_message = text.split(" ")
  line_groups = []
  current_line = ""

  for message in split_message:
    if len(current_line) + len(message) + 1 <= COLUMNS:
      current_line += message + " "
    elif len(current_line) + len(message) == COLUMNS:
      current_line += message
    elif len(current_line) + len(message) + 1 > COLUMNS:
      line_groups.append(current_line)
      current_line = message + " "

  if current_line != line_groups[-1] and current_line != "":
    line_groups.append(current_line)
    current_line = ""

  return line_groups


def convertToCharacterCode(input):
  """
  Converts a string, a list of unicode characters, or list of Vestaboard compliant colors to a list of Vestaboard character codes
  """
  row = []
  for v in input:
    try:
      row.append(int(CHARACTERS[v.upper()]))
    except KeyError:
      print(f"Character {v} not found in character dictionary")
      continue

  return row


def padRow(row: list, maxColumns = COLUMNS, align = "center"):
  """
  Interprets how many blank spaces are needed from an array of characters codes and adds enough padding to center the text on the board
  """
  while len(row) < maxColumns:
    if align == "right":
      row.insert(0, 0)
    elif align == "center":
      if len(row) % 2 == 1:
        row.append(0)
      else:
        row.insert(0, 0)
    elif align == "left":
      row.append(0)
    else:
      "no alignment specified"
  
  return row


def padBoard(board: list):
  """
  Interprets how many blank rows are needed from a 2D array of character codes and adds enough padding to center the text on the board
  """
  while len(board) <= ROWS:
    if len(board) % 2 == 1:
      board.append([0] * COLUMNS)
    else:
      board.insert(0, [0] * COLUMNS)

  return board


def writeSimpleMessage(message):
  """
  Takes a simple string and converts it to a fully centered 2D array of character codes
  """

  board = []

  lines = parseToLines(message)
  
  # convert to character codes, add padding to rows, and write to board
  for line in lines:
    row = convertToCharacterCode(line)
    padded_row = padRow(row)
    board.append(padded_row)

  # add padding to vertically center the board
  board = padBoard(board)

  return board

def writeTwoColumns(messages: list, maxRows: int, rightWider = False, outerAlign = False):
  """
  Takes a list of messages and displays them in two columns of rows on the board
  """

  board = []
  
  if rightWider:
    right_column_max = 11
    left_column_max = 10
  else:
    right_column_max = 10
    left_column_max = 11

  if len(messages) > (maxRows * 2):
    print(f"Too many messages have been provided to fit on the board. Messages will be truncated to {maxRows * 2} values.")

  # write messages to columns
  i = 0
  for i in range(maxRows):
    row = []

    # write left column
    # will pad row if the message is shorter than the max length, or truncate if it is longer
    try:
      line = convertToCharacterCode(messages[i])
      if len(line) < left_column_max:
        line += '0' * (left_column_max - len(line))
      if len(line) > left_column_max:
        line = line[:left_column_max]
      row += line
    
    # add a blank row if there are no more messages in the list
    except IndexError:
      row += '0' * left_column_max

    # write right column, starting a blank value to separate the columns
    # will pad row if the message is shorter than the max length, or truncate if it is longer
    row += '0'
    try:
      line = convertToCharacterCode(messages[i + maxRows])
      if len(line) < right_column_max:
        # if the outerAlign flag is set, the right column will be aligned to the right of the board
        if outerAlign:
          line = (['0'] * (right_column_max - len(line))) + line 
        else:
          line += '0' * (right_column_max - len(line))
      if len(line) > right_column_max:
        line = line[:right_column_max]
      row += line
    except IndexError:
      row += '0' * right_column_max

    board.append(row)

  return board
  
