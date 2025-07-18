import time
from typing import Tuple

from .base import BaseInstallable
from vestaboard.models import Board, Device, Row
from vestaboard.utils import convert_to_character_code
from vestaboard.logging import get_logger

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

class ClockInstallable(BaseInstallable):
    def __init__(self, device: Device):
        super().__init__(
            name="Clock",
            description="Displays the current time on the Vestaboard",
            device=device,
            next_refresh_increment=0
        )

    def write_digit(self, start_row: int, start_col: int, time_value: str, board: Board) -> Board:
        """
        Writes a digit to the board
        Args:
            start_row: the row to start writing the digit
            start_col: the column to start writing the digit
            time_value: the value of the digit to write
            board: the board to write the digit to
        """
        row_loc = start_row
        for row in DIGITS[str(time_value)]:
            digit_loc = start_col
            for value in row:
                if row_loc < len(board.message) and digit_loc < board.message[row_loc].length:
                    board.message[row_loc].line[digit_loc] = value
                digit_loc += 1
            row_loc += 1

        return board

    def generate_board(self) -> Tuple[Board, int]:
        """
        Displays the current time on the Vestaboard
        
        Returns:
            Tuple[Board, int]: The board with the current time and the next refresh time
        """
        # Initialize a blank board
        board = self.device.create_board(message=[], duration=None)
        
        # Create 6 rows for the board
        for i in range(6):
            board.message.append(self.device.create_row(index=i, line=[0] * self.device.columns, align="none"))

        # Parse the current time
        hr = time.strftime("%I")
        min = time.strftime("%M")
        sec = time.strftime("%S")

        # Handle hours 10, 11, 12
        if hr[0] == "1":
            board = self.write_digit(1, 0, hr[0], board)

        # Write the time to the board
        board = self.write_digit(1, 5, hr[1], board)
        
        # Add colons
        if len(board.message) > 2 and len(board.message[2].line) > 10:
            board.message[2].line[10] = 70
        if len(board.message) > 4 and len(board.message[4].line) > 10:
            board.message[4].line[10] = 70
            
        board = self.write_digit(1, 12, min[0], board)
        board = self.write_digit(1, 17, min[1], board)

        refresh = 60000 - (int(sec) * 1000)
        
        current_time = f"{hr}:{min}:{sec}"
        self.logger.debug(f"Generated clock display for {current_time}", 
                         time=current_time, refresh_time=refresh)

        return board, refresh

    def should_update(self) -> bool:
        """
        Determine if the board should be updated.
        For clock, we always want to update to show the current time.
        
        Returns:
            bool: True if the board should be updated
        """
        return True