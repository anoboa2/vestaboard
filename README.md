# Vestaboard Controller

A Python application that controls messages displayed on a Vestaboard device. This application supports multiple "installables" that can display different types of content such as Spotify currently playing, current time, and MLB scores.

## Project Structure

```
vestaboard/
├── vestaboard/           # Core Vestaboard functionality
│   ├── __init__.py      # Package exports
│   ├── models.py        # Pydantic models (Row, Board, Device)
│   ├── utils.py         # Utility functions
│   └── app.py           # Base installable class
├── installables/        # Installable modules
│   ├── __init__.py      # Package exports
│   ├── base.py          # Abstract base class for installables
│   ├── spotify.py       # Spotify currently playing
│   ├── clock.py         # Current time display
│   └── mlb_scores.py    # MLB live scores
├── orchestrator.py      # Manages installables and switching
├── config.py            # Configuration settings
├── main.py              # Main entry point
└── pyproject.toml       # Project dependencies
```

## Features

- **Modular Design**: Each installable is self-contained and follows a consistent interface
- **Easy Extension**: Add new installables by inheriting from `BaseInstallable`
- **Automatic Switching**: Orchestrator manages which installable is active
- **Type Safety**: Full type hints and Pydantic models for data validation
- **Configuration**: Centralized configuration management

## Installables

### Spotify
Displays the currently playing song and artist on Spotify.

**Features:**
- Real-time song updates
- Artist name display
- Automatic refresh based on song duration

### Clock
Displays the current time in a digital format.

**Features:**
- Large digital display
- Automatic minute updates
- Clean, readable format

### MLB Scores
Displays live MLB game scores and updates.

**Features:**
- Live game feeds
- Team priority system
- Current batter/pitcher information
- Inning and score display

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd vestaboard
```

2. Install dependencies:
```bash
pip install -e .
```

3. Set up environment variables:
```bash
export VESTABOARD_API_KEY="your-vestaboard-api-key"
```

### Spotify Setup

For Spotify functionality, you need to set up Spotify API credentials:

1. **Create a Spotify App**:
   - Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
   - Click "Create App"
   - Fill in the app details
   - Add `http://localhost:8888/callback` to the Redirect URIs

2. **Set Environment Variables**:
```bash
export SPOTIFY_CLIENT_ID="your-spotify-client-id"
export SPOTIFY_CLIENT_SECRET="your-spotify-client-secret"
export SPOTIFY_REDIRECT_URI="http://localhost:8888/callback"
```

3. **Test Authentication**:
```bash
python spotify_test.py
```

**Note**: The first time you run the Spotify installable, it will open a browser window for user authorization. This is required to access user-specific data like currently playing tracks.

## Usage

### Basic Usage

Run with the default Spotify installable:
```bash
python main.py
```

### Command Line Options

List available installables:
```bash
python main.py --list
```

Run a specific installable:
```bash
python main.py --installable clock
python main.py --installable mlb
```

Set custom update interval:
```bash
python main.py --installable spotify --interval 30
```

### Programmatic Usage

```python
from vestaboard.models import Device
from orchestrator import Orchestrator

# Create device
device = Device(rows=6, columns=22, active_installable="spotify")

# Create orchestrator
orchestrator = Orchestrator(device)

# List available installables
orchestrator.list_installables()

# Run with specific installable
orchestrator.run('spotify')
```

## Creating New Installables

To create a new installable:

1. Create a new file in the `installables/` directory
2. Inherit from `BaseInstallable`
3. Implement the required methods:

```python
from .base import BaseInstallable
from vestaboard.models import Board, Device
from typing import Tuple

class MyInstallable(BaseInstallable):
    def __init__(self, device: Device):
        super().__init__(
            name="My Installable",
            description="Description of what this installable does",
            device=device,
            next_refresh_increment=0
        )

    def generate_board(self) -> Tuple[Board, int]:
        """Generate a new board for the Vestaboard."""
        # Your logic here
        board = self.device.create_board()
        return board, 60000  # Refresh time in milliseconds

    def should_update(self) -> bool:
        """Determine if the board should be updated."""
        return True
```

4. Register the installable in `installables/__init__.py`
5. Add it to the orchestrator in `orchestrator.py`

## Configuration

Configuration is centralized in `config.py`. You can modify:

- Vestaboard device settings (rows, columns)
- Installable-specific settings
- Application behavior (update intervals, retry logic)

## Architecture

### Core Components

- **Device**: Represents a Vestaboard device with dimensions and API interaction
- **Board**: Represents a message board with rows and columns
- **Row**: Represents a single row of characters on the board
- **BaseInstallable**: Abstract base class for all installables

### Data Flow

1. **Orchestrator** manages which installable is active
2. **Installable** generates a board with content
3. **Device** sends the board to the Vestaboard API
4. Process repeats based on refresh timing

### Error Handling

- API failures are handled gracefully
- Installables can return fallback content
- Configuration validation prevents invalid settings

