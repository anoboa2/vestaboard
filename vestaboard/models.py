from pydantic import BaseModel, Field, computed_field
from typing import Optional, List, Literal, Union, Annotated
import requests
import os

from .logging import get_logger

VESTABOARD_API_KEY = os.getenv("VESTABOARD_API_KEY")

class Row(BaseModel):
    index: int
    length: Annotated[int, Field(description="Length inherited from Board.columns")]
    align: Literal["left", "center", "right", "none"] = "left"
    line: List[int]

    def parse_string_to_line(self, text: Union[str, List[str]]):
        """
        Parses a string into a line object of a Row

        Args:
            text (Union[str, List[str]]): the string to be parsed

        Returns:
            remaining_words (List[str]): the words that were not able to fit on the current line
        """
        from .utils import convert_to_character_code
        if isinstance(text, str):
            list_of_chars = [char for char in text]
            self.line = convert_to_character_code(list_of_chars)
        elif isinstance(text, list):
            self.line = convert_to_character_code(text) 

    def pad_line(self):
        """
        Pads a row of character codes to the left or right to fit the Vestaboard's width
        If the alignment is "none", the line is not padded
        """
        while len(self.line) < self.length:
            if self.align == "right":
                self.line.insert(0, 0)
            elif self.align == "center":
                if len(self.line) % 2 == 1:
                    self.line.append(0)
                else:
                    self.line.insert(0, 0)
            elif self.align == "left":
                self.line.append(0)
            elif self.align == "none":
                pass
            else:
                raise ValueError("Invalid alignment specified in Row")

class Board(BaseModel):
    rows: Annotated[int, Field(description="Rows inherited from Device.rows")]
    columns: int
    message: List[Row]
    duration: Optional[int] = None

    def pad_message(self):
        """
        Pads a message the top or bottom of the board to fit the Vestaboard's height

        """
        if self.rows is None or self.columns is None:
            return self.message
            
        while len(self.message) <= self.rows:
            if len(self.message) % 2 == 1:
                blank_row = Row(index=len(self.message), length=self.columns, line=[0] * self.columns)
                self.message.append(blank_row)
            else:
                blank_row = Row(index=0, length=self.columns, line=[0] * self.columns)
                self.message.insert(0, blank_row)

        return self.message

    def write_simple_message(self, input_string: str):
        """
        Takes a simple string message and converts it to a fully centered 2D array of character codes

        Args:
            input_string (str): the string to be converted to a board
        """

        current_line = ""
        rows=[]

        # Parse every word in the string into a list of words
        split_words = input_string.split(" ")

        # Loop through every word to determine which Row it will fit on within the Board
        for word in split_words:
            if len(current_line) + len(word) + 1 <= self.columns:
                current_line += word + " "
            elif len(current_line) + len(word) == self.columns:
                current_line += word
            elif len(current_line) + len(word) + 1 > self.columns:
                rows.append(current_line)
                current_line = ""

        from .utils import convert_to_character_code
        for row in rows:
            row = Row(index=len(rows), length=self.columns, line=convert_to_character_code(row))
            self.message.append(row)

        self.pad_message()

class Device(BaseModel):
    rows: int
    columns: int
    active_board: Optional[Board] = None
    active_installable: str

    def model_post_init(self, __context) -> None:
        """Called after the model is initialized, used to populate active_board if not provided"""
        super().model_post_init(__context)
        
        # If active_board wasn't provided, populate it by calling get_board()
        if self.active_board is None:
            self.get_board()
        else:
            # Ensure the provided active_board inherits the device dimensions
            self.active_board.rows = self.rows
            self.active_board.columns = self.columns
            # Update all rows to inherit the board's column count
            for row in self.active_board.message:
                row.length = self.columns

    def create_board(self, message: Optional[List[Row]] = None, duration: Optional[int] = None) -> Board:
        """
        Creates a new Board with dimensions inherited from this Device
        
        Args:
            message: List of Row objects for the board
            duration: Optional duration for the board
            
        Returns:
            Board: A new Board with inherited dimensions
        """
        if message is None:
            message = []
        
        # Ensure all rows inherit the device's column count
        for row in message:
            row.length = self.columns
            
        return Board(
            rows=self.rows,
            columns=self.columns,
            message=message,
            duration=duration
        )

    def create_row(self, index: int, line: Optional[List[int]] = None, align: Literal["left", "center", "right", "none"] = "left") -> Row:
        """
        Creates a new Row with length inherited from this Device's columns
        
        Args:
            index: The row index
            line: The character codes for the row
            align: The alignment for the row
            
        Returns:
            Row: A new Row with inherited length
        """
        if line is None:
            line = [0] * self.columns
            
        row = Row(
            index=index,
            length=self.columns,
            line=line,
            align=align
        )
        row.pad_line()
        return row

    def update_message(self, new_board: Board):
        """
        Updates the message on the board

        Args:
            new_board (Board): the new board to be updated
        """
        logger = get_logger("device")
        
        # Ensure the new board inherits device dimensions
        new_board.rows = self.rows
        new_board.columns = self.columns
        
        # Update all rows to inherit the board's column count
        for row in new_board.message:
            row.length = self.columns

        try:
            # Convert Row objects to just the character codes for API
            message_data = [row.line for row in new_board.message]

            response = requests.post(
                url = "https://rw.vestaboard.com/",
                headers={"X-Vestaboard-Read-Write-Key": VESTABOARD_API_KEY}, # type: ignore
                json=message_data
            )

            if response.status_code == 200:
                self.active_board = new_board
                logger.debug("Board updated successfully via API")
            else:
                print("response", response.request.body)
                error_msg = f"Error updating board: {response.status_code}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            logger.exception(f"Error updating board: {e}")

    def get_board(self):
        """
        Gets the current board from the Vestaboard API
        """
        logger = get_logger("device")
        try:
            response = requests.get(
                url = "https://rw.vestaboard.com/",
                headers={"X-Vestaboard-Read-Write-Key": VESTABOARD_API_KEY}, # type: ignore
            )

            if response.status_code == 200:
                response_data = response.json()
                logger.debug(f"API Response: {response_data}")
                
                # Handle the actual API response structure
                if 'currentMessage' in response_data:
                    # API returns {currentMessage: {id: ..., layout: [...]}}
                    layout = response_data['currentMessage'].get('layout', [])
                    # Convert layout to our Board format
                    rows = []
                    for i, row_data in enumerate(layout):
                        row = Row(
                            index=i,
                            length=self.columns,
                            line=row_data,
                            align="left"
                        )
                        rows.append(row)
                    
                    self.active_board = Board(
                        rows=self.rows,
                        columns=self.columns,
                        message=rows
                    )
                else:
                    # Try to parse as direct Board format
                    self.active_board = Board.model_validate(response_data)
                    # Ensure the board inherits device dimensions
                    self.active_board.rows = self.rows
                    self.active_board.columns = self.columns
                    # Update all rows to inherit the board's column count
                    for row in self.active_board.message:
                        row.length = self.columns
            else:
                error_msg = f"Error getting board: {response.content}"
                logger.error(error_msg)
                raise Exception(error_msg)
        except Exception as e:
            logger.exception(f"Error getting board: {e}")

class Characters(BaseModel):
    code: dict[str, str] = {
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
        'FILLED': '71'
    }
    colors: dict[str, str] = {
        'RED': '1',
        'ORANGE': '2',
        'YELLOW': '3',
        'GREEN': '4',
        'BLUE': '5',
        'PURPLE': '6',
        'WHITE': '7',
        'BLACK': '8'
    }