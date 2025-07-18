import spotipy
from spotipy.oauth2 import SpotifyOAuth
from unidecode import unidecode
from typing import Tuple, Optional
import os

from .base import BaseInstallable
from vestaboard.models import Board, Device
from vestaboard.utils import convert_to_character_code
from vestaboard.logging import get_logger
from config import INSTALLABLE_CONFIG

# Some configuration for the Spotify API using the spotipy library
scope = INSTALLABLE_CONFIG['spotify']['scope']

class SpotifyInstallable(BaseInstallable):
    def __init__(self, device: Device):
        super().__init__(
            name="Spotify",
            description="Displays the currently playing song from Spotify",
            device=device,
            next_refresh_increment=0
        )
        self._spotify_client: Optional[spotipy.Spotify] = None

    def _get_spotify_client(self) -> Optional[spotipy.Spotify]:
        """Get or create Spotify client with lazy initialization."""
        if self._spotify_client is None:
            try:
                # Use SpotifyOAuth for user authentication
                auth_manager = SpotifyOAuth(
                    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
                    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
                    redirect_uri=os.getenv("SPOTIFY_REDIRECT_URI"),
                    scope=scope,
                    open_browser=True  # This will open a browser for user authorization
                )
                
                self._spotify_client = spotipy.Spotify(auth_manager=auth_manager)
                self.logger.debug("Spotify client initialized successfully")
            except Exception as e:
                self.logger.error(f"Failed to initialize Spotify client: {e}")
                return None
        return self._spotify_client

    def generate_board(self) -> Tuple[Board, int]:
        """
        Gets the current song from Spotify and returns a board with the song name and artist name(s)

        Returns:
            Tuple[Board, int]: The board with the song name and artist name(s), and the next refresh time
        """
        board = self.device.create_board(message=[], duration=None)

        # Add some padding and embellishments to the top of the board
        header_line_text = ["GREEN", " ", " ", " ", " ", "N", "O", "w", " ", "P", "L", "A", "Y", "I", "N", "G", " ", " ", " ", " ", " ", "GREEN"]
        header_row = self.device.create_row(index=1, line=convert_to_character_code(header_line_text), align="none")

        design = [
            self.device.create_row(index=0, line=[66, 66, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 66, 66], align="none"),
            header_row,
            self.device.create_row(index=2, line=[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], align="none")
        ]
        board.message = design

        # Get the current song from Spotify and handle edge cases
        sp = self._get_spotify_client()
        if sp is None:
            self.logger.warning("Spotify client not available - check your credentials")
            return board, 15000
            
        try:
            current_song = sp.current_user_playing_track()
            if current_song == None:
                self.logger.info("No song currently playing")
                self.next_refresh_increment = 15000
                return board, 15000
            if current_song['is_playing'] == False:
                self.logger.info("No song is actively playing")
                self.next_refresh_increment = 15000
                return board, 15000
        except spotipy.exceptions.SpotifyException as e:
            self.logger.error(f"Spotify API error: {e}")
            self.next_refresh_increment = 15000
            return board, 15000

        # Parse the artist and song name from the Spotify response
        artists = [unidecode(artist['name']) for artist in current_song['item']['artists']]
        song = unidecode(current_song['item']['name'])
        refresh = (current_song['item']['duration_ms'] - current_song['progress_ms']) + 1000

        self.logger.info(f"Now playing: {song} by {', '.join(artists)}", 
                        song=song, artists=artists, refresh_time=refresh)

        # Construct the song and artist name lines and add them to the board
        line4 = self.device.create_row(index=3, line=convert_to_character_code([char for char in song]), align="center")
        line5 = self.device.create_row(index=4, line=convert_to_character_code([char for char in ", ".join(artists)]), align="center")
        line6 = self.device.create_row(index=5, line=[0] * self.device.columns, align="none")
        
        board.message.extend([line4, line5, line6])

        return board, refresh

    def should_update(self) -> bool:
        """
        Determine if the board should be updated.
        For Spotify, we always want to update to get the latest song information.
        
        Returns:
            bool: True if the board should be updated
        """
        return True




