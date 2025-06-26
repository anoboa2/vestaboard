

def pad_row(row: list, maxColumns: int, align = "center"):
  """
  Interprets how many blank spaces are needed from an array of characters codes
  and adds enough padding to center the text on the board
  Params:
    row: the row to be padded
    maxColumns: the maximum number of columns on the Vestaboard
    align: the alignment of the text on the board
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
  Interprets how many blank rows are needed from a 2D array of character codes
  and adds enough padding to center the text on the board
  Params:
    board: the board to be padded
  """
  while len(board) <= ROWS:
    if len(board) % 2 == 1:
      board.append([0] * COLUMNS)
    else:
      board.insert(0, [0] * COLUMNS)

  return board