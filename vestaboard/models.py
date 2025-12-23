from pydantic import BaseModel, Field
from typing import Optional, List, Literal, Union, Annotated
import requests
import os
from dotenv import load_dotenv

from .logging import get_logger

# Load environment variables before accessing them
load_dotenv()

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
            # Ensure API key is available
            api_key = os.getenv("VESTABOARD_API_KEY")
            if not api_key:
                raise Exception("VESTABOARD_API_KEY environment variable not set")
            
            # Convert Row objects to just the character codes for API
            # Vestaboard API expects exactly 6 rows x 22 columns
            # Truncate or pad to match these dimensions
            VESTABOARD_ROWS = 6
            VESTABOARD_COLS = 22
            
            message_data = []
            rows_to_send = new_board.message[:VESTABOARD_ROWS]  # Only send first 6 rows
            for row in rows_to_send:
                row_data = row.line[:VESTABOARD_COLS]  # Truncate if longer
                if len(row_data) < VESTABOARD_COLS:
                    # Pad if shorter (shouldn't happen if pad_line was called, but be safe)
                    row_data.extend([0] * (VESTABOARD_COLS - len(row_data)))
                message_data.append(row_data)
            
            # Ensure we have exactly 6 rows (pad with empty rows if needed)
            while len(message_data) < VESTABOARD_ROWS:
                message_data.append([0] * VESTABOARD_COLS)

            response = requests.post(
                url = "https://rw.vestaboard.com/",
                headers={"X-Vestaboard-Read-Write-Key": api_key},
                json=message_data
            )

            if response.status_code == 200:
                self.active_board = new_board
                logger.debug("Board updated successfully via API")
            else:
                # Log request and response for debugging
                logger.error(f"Request body: {response.request.body}")
                error_message = f"Error updating board: {response.status_code}"
                try:
                    response_text = response.text
                    logger.error(f"Response body: {response_text}")
                    # Try to parse JSON error message from Vestaboard API
                    try:
                        error_json = response.json()
                        error_message = error_json.get("message", error_message)
                    except (ValueError, AttributeError, TypeError):
                        # If JSON parsing fails, use the response text if available
                        if response_text:
                            error_message = response_text
                except Exception:
                    logger.error(f"Response content: {response.content}")
                logger.error(error_message)
                raise Exception(error_message)
        except Exception as e:
            logger.exception(f"Error updating board: {e}")
            raise  # Re-raise the exception so the API endpoint can handle it

    def get_board(self):
        """
        Gets the current board from the Vestaboard API
        """
        logger = get_logger("device")
        try:
            # Ensure API key is available
            api_key = os.getenv("VESTABOARD_API_KEY")
            if not api_key:
                raise Exception("VESTABOARD_API_KEY environment variable not set")
            
            response = requests.get(
                url = "https://rw.vestaboard.com/",
                headers={"X-Vestaboard-Read-Write-Key": api_key},
            )

            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"API Response keys: {list(response_data.keys())}")
                logger.debug(f"Full API Response: {response_data}")
                
                # Handle the actual API response structure
                if 'currentMessage' in response_data:
                    current_message = response_data['currentMessage']
                    logger.info(f"currentMessage type: {type(current_message)}, value: {current_message}")
                    
                    if current_message is None:
                        logger.info("currentMessage is None - no active board")
                        # Create empty board
                        rows = []
                        for i in range(self.rows):
                            rows.append(Row(
                                index=i,
                                length=self.columns,
                                line=[0] * self.columns,
                                align="left"
                            ))
                        self.active_board = Board(
                            rows=self.rows,
                            columns=self.columns,
                            message=rows
                        )
                    elif isinstance(current_message, dict):
                        # API returns {currentMessage: {id: ..., layout: [...]}}
                        layout = current_message.get('layout', [])
                        logger.info(f"Layout type: {type(layout)}, length: {len(layout) if isinstance(layout, (list, str)) else 'N/A'}")
                        
                        # Handle case where layout might be a string (JSON string) or list
                        if isinstance(layout, str):
                            import json
                            try:
                                layout = json.loads(layout)
                                logger.info(f"Parsed layout from JSON string, now has {len(layout)} rows")
                            except json.JSONDecodeError:
                                logger.warning(f"Could not parse layout as JSON: {layout[:100]}...")
                                layout = []
                        
                        
                        # Ensure layout is a list
                        if not isinstance(layout, list):
                            logger.error(f"Layout is not a list, type: {type(layout)}, value: {layout}")
                            layout = []
                        
                        logger.info(f"Processing layout with {len(layout)} rows")
                        
                        # Convert layout to our Board format
                    rows = []
                    for i, row_data in enumerate(layout):
                        try:
                            # Ensure row_data is a list of integers
                            if isinstance(row_data, str):
                                import json
                                try:
                                    row_data = json.loads(row_data)
                                except json.JSONDecodeError:
                                    logger.warning(f"Could not parse row_data as JSON at index {i}: {row_data[:50]}...")
                                    row_data = []
                            
                            if not isinstance(row_data, list):
                                logger.warning(f"Row data at index {i} is not a list: {type(row_data)} - {str(row_data)[:50]}")
                                row_data = []
                            
                            # Ensure all elements are integers (convert to int, default to 0 if not valid)
                            processed_row = []
                            for x in row_data:
                                try:
                                    processed_row.append(int(x))
                                except (ValueError, TypeError):
                                    processed_row.append(0)
                            
                            # Ensure row has correct length (pad or truncate)
                            if len(processed_row) < self.columns:
                                processed_row.extend([0] * (self.columns - len(processed_row)))
                            elif len(processed_row) > self.columns:
                                processed_row = processed_row[:self.columns]
                            
                            row = Row(
                                index=i,
                                length=self.columns,
                                line=processed_row,
                                align="left"
                            )
                            rows.append(row)
                        except Exception as e:
                            logger.error(f"Error processing row {i}: {e}, row_data type: {type(row_data)}, value: {str(row_data)[:100]}")
                            # Create empty row as fallback
                            rows.append(Row(
                                index=i,
                                length=self.columns,
                                line=[0] * self.columns,
                                align="left"
                            ))
                    
                    self.active_board = Board(
                        rows=self.rows,
                        columns=self.columns,
                        message=rows
                    )
                elif 'currentMessage' in response_data and response_data['currentMessage'] is None:
                    # No current message on the board - create empty board
                    logger.info("No current message on Vestaboard - returning empty board")
                    rows = []
                    for i in range(self.rows):
                        rows.append(Row(
                            index=i,
                            length=self.columns,
                            line=[0] * self.columns,
                            align="left"
                        ))
                    self.active_board = Board(
                        rows=self.rows,
                        columns=self.columns,
                        message=rows
                    )
                else:
                    # Try to parse as direct Board format
                    try:
                        self.active_board = Board.model_validate(response_data)
                        # Ensure the board inherits device dimensions
                        self.active_board.rows = self.rows
                        self.active_board.columns = self.columns
                        # Update all rows to inherit the board's column count
                        for row in self.active_board.message:
                            row.length = self.columns
                    except Exception:
                        # If parsing fails, create empty board
                        logger.warning("Could not parse board response - returning empty board")
                        rows = []
                        for i in range(self.rows):
                            rows.append(Row(
                                index=i,
                                length=self.columns,
                                line=[0] * self.columns,
                                align="left"
                            ))
                        self.active_board = Board(
                            rows=self.rows,
                            columns=self.columns,
                            message=rows
                        )
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