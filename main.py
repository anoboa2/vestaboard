"""
Main entry point for the Vestaboard application.

This script runs the orchestrator which manages different installables
and controls which one is active on the Vestaboard device.
"""

import os
import sys
import argparse
from dotenv import load_dotenv

# Load environment variables first, before importing any modules that might need them
load_dotenv()

# Import modules after environment is loaded
from orchestrator import Orchestrator
from vestaboard.models import Device
from vestaboard.logging import get_logger, log_component_start, log_component_stop

def main():
    """Main function to run the Vestaboard application."""
    logger = get_logger("main")
    
    parser = argparse.ArgumentParser(description='Vestaboard Application')
    parser.add_argument(
        '--installable', 
        '-i',
        choices=['spotify', 'clock', 'mlb'],
        default='spotify',
        help='Which installable to run (default: spotify)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=60,
        help='Update interval in seconds (default: 60)'
    )
    parser.add_argument(
        '--list',
        action='store_true',
        help='List available installables and exit'
    )
    parser.add_argument(
        '--log-level',
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        default='INFO',
        help='Set the logging level (default: INFO)'
    )
    
    args = parser.parse_args()
    
    # Set log level from command line argument
    if args.log_level:
        import os
        os.environ['VESTABOARD_LOG_LEVEL'] = args.log_level
    
    log_component_start("main", installable=args.installable, interval=args.interval, log_level=args.log_level)
    
    try:
        # Create a device instance (6 rows, 22 columns for standard Vestaboard)
        device = Device(
            rows=6,
            columns=22,
            active_installable=args.installable
        )
        
        # Create orchestrator
        orchestrator = Orchestrator(device)
        
        if args.list:
            orchestrator.list_installables()
            return
        
        # Run the orchestrator
        orchestrator.run(args.installable, args.interval)
        
    except Exception as e:
        logger.exception("Fatal error in main application")
        sys.exit(1)
    finally:
        log_component_stop("main")


if __name__ == "__main__":
    main()