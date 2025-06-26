from models import Row, Board

def parse_string_to_row(text: str, columns: int) -> Board:
  """

  Parses a string into a Board object

  Args:
    text (str): the string to be parsed
    columns (int): the number of columns on the Vestaboard; should be taken from Board.columns

  Returns:
    row (Row): the Row object
  """
  rows = []
  current_line = ""

  # Parse every word in the string into a list of words
  split_words = text.split(" ")

  # Loop through every word to determine which Row it will fit on within the Board
  for word in split_words:
    if len(current_line) + len(word) + 1 <= columns:
      current_line += word + " "
    elif len(current_line) + len(word) == columns:
      current_line += word
    elif len(current_line) + len(word) + 1 > columns:
      rows.append(
        Row(
          index=0,
          length=len(current_line),
          line=current_line
        )
      )
      current_line = word + " "

  if current_line != rows[-1] and current_line != "":
    rows.append(
      Row(
        index=0,
        length=len(current_line),
        line=current_line
      )
    )
    current_line = ""

  return Board(
    rows=len(rows),
    columns=columns,
    message=rows,
    duration=None
  )