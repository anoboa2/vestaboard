from abc import ABC, abstractmethod
from typing import Optional, Tuple, List
from pydantic import BaseModel

from vestaboard.models import Device, Board, Row
from vestaboard.logging import get_logger


class BaseInstallable(BaseModel, ABC):
    """
    Abstract base class for all Vestaboard installables.
    
    All installables must inherit from this class and implement the required methods.
    """
    name: str
    description: str
    device: Device
    next_refresh_increment: int = 0
    
    def model_post_init(self, __context) -> None:
        """Called after the model is initialized, used to set up logging."""
        super().model_post_init(__context)
        # Initialize logger after the model is fully initialized
        self._logger = get_logger(self.name.lower())
    
    @property
    def logger(self):
        """Get the logger for this installable."""
        return self._logger

    @abstractmethod
    def generate_board(self) -> Tuple[Board, int]:
        """
        Generate a new board for the Vestaboard.
        
        Returns:
            Tuple[Board, int]: A tuple containing the board and the next refresh time in milliseconds
        """
        pass

    @abstractmethod
    def should_update(self) -> bool:
        """
        Determine if the board should be updated.
        
        Returns:
            bool: True if the board should be updated, False otherwise
        """
        pass

    def update_board(self) -> bool:
        """
        Update the Vestaboard with a new board.
        
        Returns:
            bool: True if the update was successful, False otherwise
        """
        logger = get_logger(self.name.lower())
        try:
            board, refresh_time = self.generate_board()
            self.device.update_message(board)
            self.next_refresh_increment = refresh_time
            logger.info(f"Board updated successfully, next refresh in {refresh_time}ms", 
                       refresh_time=refresh_time)
            return True
        except Exception as e:
            logger.exception(f"Error updating board for {self.name}")
            return False

    def get_refresh_time(self) -> int:
        """
        Get the next refresh time in milliseconds.
        
        Returns:
            int: The next refresh time in milliseconds
        """
        return self.next_refresh_increment
