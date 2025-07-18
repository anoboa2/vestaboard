"""
Vestaboard Installables Package

This package contains all the installable modules that can display content on a Vestaboard device.
Each installable inherits from BaseInstallable and implements the required methods.
"""

from .base import BaseInstallable
from .spotify import SpotifyInstallable
from .clock import ClockInstallable
from .mlb_scores import MLBScoresInstallable

__all__ = [
    'BaseInstallable',
    'SpotifyInstallable', 
    'ClockInstallable',
    'MLBScoresInstallable'
] 