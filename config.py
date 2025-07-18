"""
Configuration settings for the Vestaboard application.

This module contains all the configuration settings that can be easily modified
without changing the core application code.
"""

import os
from typing import Dict, Any

# Vestaboard device configuration
VESTABOARD_CONFIG = {
    'rows': 6,
    'columns': 22,
    'api_url': 'https://rw.vestaboard.com/',
    'api_key_env': 'VESTABOARD_API_KEY'
}

# Installable configuration
INSTALLABLE_CONFIG = {
    'spotify': {
        'scope': 'user-read-currently-playing user-read-playback-state',
        'default_refresh': 15000,  # 15 seconds
        'client_id_env': 'SPOTIFY_CLIENT_ID',
        'client_secret_env': 'SPOTIFY_CLIENT_SECRET',
        'redirect_uri_env': 'SPOTIFY_REDIRECT_URI',
        'default_redirect_uri': 'http://localhost:8888/callback'
    },
    'clock': {
        'default_refresh': 60000,  # 1 minute
    },
    'mlb': {
        'default_refresh': 15000,  # 15 seconds
        'api_url': 'http://statsapi.mlb.com/api/v1',
        'team_priority': [111, 113, 147, 109, 110],  # Red Sox, Reds, Yankees, Diamondbacks, Orioles
    }
}

# Application configuration
APP_CONFIG = {
    'default_installable': 'spotify',
    'default_update_interval': 60,  # seconds
    'log_level': 'INFO',
    'max_retries': 3,
    'retry_delay': 5,  # seconds
}

# Logging configuration
LOGGING_CONFIG = {
    'default_level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'date_format': '%Y-%m-%d %H:%M:%S',
    'components': {
        'orchestrator': 'INFO',
        'spotify': 'INFO',
        'clock': 'INFO',
        'mlb': 'INFO',
        'device': 'INFO',
        'utils': 'WARNING'
    }
}

def get_vestaboard_api_key() -> str:
    """Get the Vestaboard API key from environment variables."""
    api_key = os.getenv(VESTABOARD_CONFIG['api_key_env'])
    if not api_key:
        raise ValueError(f"VESTABOARD_API_KEY environment variable not set")
    return api_key

def get_spotify_credentials() -> Dict[str, str]:
    """Get Spotify credentials from environment variables."""
    config = INSTALLABLE_CONFIG['spotify']
    client_id = os.getenv(config['client_id_env'])
    client_secret = os.getenv(config['client_secret_env'])
    redirect_uri = os.getenv(config['redirect_uri_env'], config['default_redirect_uri'])
    
    if not client_id or not client_secret:
        raise ValueError(f"Spotify credentials not found. Please set {config['client_id_env']} and {config['client_secret_env']} environment variables.")
    
    return {
        'client_id': client_id,
        'client_secret': client_secret,
        'redirect_uri': redirect_uri
    }

def get_config() -> Dict[str, Any]:
    """Get the complete configuration."""
    return {
        'vestaboard': VESTABOARD_CONFIG,
        'installables': INSTALLABLE_CONFIG,
        'app': APP_CONFIG,
        'logging': LOGGING_CONFIG
    } 