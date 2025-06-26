from models import Row as RowModel, Board as BoardModel
from typing import List

class Board(BoardModel):
  def __init__(self, rows: int, columns: int):
    super().__init__(rows=rows, columns=columns, message=[])

  def add_row(self, row: RowModel):
    self.message.append(row)

  def pad_row(self, input_line: List[int], align: str = "center") -> List[int]:
    """
    Pads a row of character codes to the left or right to fit the Vestaboard's width

    Args:
        row_line (List[int]): the row of character codes to be padded
        max_columns (int): the maximum number of columns on the Vestaboard
        align (str): the alignment of the text on the board

    Returns:
        line (List[int]): the padded row of character codes
    """
    while len(input_line) < self.columns:
        if align == "right":
            input_line.insert(0, 0)
        elif align == "center":
            if len(input_line) % 2 == 1:
                input_line.append(0)
            else:
                input_line.insert(0, 0)
        elif align == "left":
            input_line.append(0)
        else:
            "no alignment specified"
    
    return input_line

  def pad_message(self, message: MessageModel) -> MessageModel:
    """
    Interprets how many blank rows are needed from a 2D array of character codes
    and adds enough padding to center the text on the board
    Params:
        board: the board to be padded
    """
    while len(message.message) <= self.rows:
        if len(message.message) % 2 == 1:
            message.message.append([0] * self.columns)
        else:
            board.insert(0, [0] * self.columns)

    return board


class Device():
  def __init__(self, rows: int, columns: int):
    self.rows = rows
    self.columns = columns
    self.board = BoardModel(rows=rows, columns=columns, message=[])

  def update_message(self, message: BoardModel):
    self.board = message

  def write_simple_message(self, message: str) -> BoardModel:
    """
    Takes a simple string message and converts it to a fully centered 2D array of character codes

    Args:
        message (str): the string to be converted to a board

    Returns:
        board (BoardModel): the board with the message
    """
    board = Board(self.rows, self.columns)
    
    lines = parse_string_to_line(message, self.columns)
    
    for line in lines:
      row = convert_to_character_code(line)
      
      board.add_row(padded_row)

    board = self.pad_message(board)

    return board



