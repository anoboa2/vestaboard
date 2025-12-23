"""
Vestaboard Installables Package

This package contains all the installable modules that can display content on a Vestaboard device.
Each installable inherits from BaseInstallable and implements the required methods.
"""

from ._base import BaseInstallable
from .spotify.app import SpotifyInstallable
from .clock.app import ClockInstallable
from .sports.mlb.app import MLBScoresInstallable

__all__ = [
    'BaseInstallable',
    'SpotifyInstallable', 
    'ClockInstallable',
    'MLBScoresInstallable'
] 