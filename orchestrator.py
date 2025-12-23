"""
Vestaboard Orchestrator

This module manages the different installables and controls which one is active
at any given time. It handles switching between installables and managing their
lifecycles.
"""

import time
import os
import threading
from typing import Dict, Optional, Type
from dotenv import load_dotenv

from vestaboard.models import Device
from installables import BaseInstallable, SpotifyInstallable, ClockInstallable, MLBScoresInstallable
from vestaboard.logging import get_logger, log_component_start, log_component_stop, log_installable_switch

load_dotenv()

class Orchestrator:
    """
    Manages multiple Vestaboard installables and controls which one is active.
    """
    
    def __init__(self, device: Device):
        self.device = device
        self.installables: Dict[str, BaseInstallable] = {}
        self.active_installable: Optional[str] = None
        self.last_update_time = 0
        self.logger = get_logger("orchestrator")
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self._lock = threading.Lock()
        
        # Register available installables
        self._register_installables()
    
    def _register_installables(self):
        """Register all available installables."""
        self.installables = {
            'spotify': SpotifyInstallable(self.device),
            'clock': ClockInstallable(self.device),
            'mlb': MLBScoresInstallable(self.device),
        }
    
    def set_active_installable(self, installable_name: str) -> bool:
        """
        Set the active installable.
        
        Args:
            installable_name: Name of the installable to activate
            
        Returns:
            bool: True if successful, False if installable not found
        """
        with self._lock:
            if installable_name not in self.installables:
                self.logger.error(f"Installable '{installable_name}' not found. Available: {list(self.installables.keys())}")
                return False
            
            previous_installable = self.active_installable
            self.active_installable = installable_name
            
            if previous_installable:
                log_installable_switch("orchestrator", previous_installable, installable_name)
            else:
                self.logger.info(f"Activated {installable_name} installable")
            
            return True
    
    def deactivate_installable(self) -> bool:
        """
        Deactivate the current installable.
        Stops the installable but leaves the board unchanged.
        
        Returns:
            bool: True if successful, False if no installable was active
        """
        with self._lock:
            if self.active_installable is None:
                self.logger.warning("No active installable to deactivate")
                return False
            
            previous_installable = self.active_installable
            self.active_installable = None
            self.logger.info(f"Deactivated {previous_installable} installable")
            return True
    
    def get_active_installable(self) -> Optional[BaseInstallable]:
        """
        Get the currently active installable.
        
        Returns:
            BaseInstallable: The active installable or None if none is set
        """
        with self._lock:
            if self.active_installable is None:
                return None
            return self.installables[self.active_installable]
    
    def get_active_installable_name(self) -> Optional[str]:
        """
        Get the name of the currently active installable.
        
        Returns:
            str: The active installable name or None if none is set
        """
        with self._lock:
            return self.active_installable
    
    def update_board(self) -> bool:
        """
        Update the board with the active installable.
        
        Returns:
            bool: True if update was successful, False otherwise
        """
        with self._lock:
            if self.active_installable is None:
                return False
            
            installable_name = self.active_installable
        
        installable = self.installables[installable_name]
        
        if installable.should_update():
            success = installable.update_board()
            if success:
                with self._lock:
                    self.last_update_time = time.time()
                self.logger.debug(f"Board updated successfully with {installable_name}")
            return success
        
        return True  # No update needed
    
    def run(self, installable_name: str = 'spotify', update_interval: int = 60):
        """
        Run the orchestrator with the specified installable.
        
        Args:
            installable_name: Name of the installable to run
            update_interval: How often to check for updates (in seconds)
        """
        if not self.set_active_installable(installable_name):
            return
        
        log_component_start("orchestrator", installable=installable_name, update_interval=update_interval)
        
        try:
            while True:
                self.update_board()
                
                # Get the refresh time from the active installable
                installable = self.get_active_installable()
                if installable:
                    refresh_time = installable.get_refresh_time() / 1000  # Convert to seconds
                    time.sleep(refresh_time)
                else:
                    time.sleep(update_interval)
                    
        except KeyboardInterrupt:
            self.logger.info("Received keyboard interrupt, stopping orchestrator")
        except Exception as e:
            self.logger.exception("Error in orchestrator")
        finally:
            log_component_stop("orchestrator")
    
    def start_background_task(self, update_interval: int = 60):
        """
        Start the orchestrator background task in a separate thread.
        
        Args:
            update_interval: How often to check for updates (in seconds)
        """
        if self._running:
            self.logger.warning("Orchestrator background task is already running")
            return
        
        self._running = True
        
        def _background_loop():
            log_component_start("orchestrator", update_interval=update_interval)
            
            try:
                while self._running:
                    with self._lock:
                        active_name = self.active_installable
                    
                    if active_name is None:
                        time.sleep(update_interval)
                        continue
                    
                    self.update_board()
                    
                    # Get the refresh time from the active installable
                    installable = self.get_active_installable()
                    if installable:
                        refresh_time = installable.get_refresh_time() / 1000  # Convert to seconds
                        # Sleep in smaller increments to check _running flag
                        slept = 0
                        while slept < refresh_time and self._running:
                            time.sleep(min(1.0, refresh_time - slept))
                            slept += 1.0
                    else:
                        time.sleep(update_interval)
                        
            except Exception as e:
                self.logger.exception("Error in orchestrator background task")
            finally:
                self._running = False
                log_component_stop("orchestrator")
        
        self._thread = threading.Thread(target=_background_loop, daemon=True)
        self._thread.start()
        self.logger.info("Orchestrator background task started")
    
    def stop_background_task(self):
        """
        Stop the orchestrator background task.
        """
        if not self._running:
            return
        
        self.logger.info("Stopping orchestrator background task")
        self._running = False
        
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=5.0)
        
        self.logger.info("Orchestrator background task stopped")
    
    def list_installables(self):
        """List all available installables."""
        self.logger.info("Available installables:")
        for name, installable in self.installables.items():
            self.logger.info(f"  - {name}: {installable.description}")
    
    def get_installable_status(self) -> Dict[str, str]:
        """
        Get the status of all installables.
        
        Returns:
            Dict[str, str]: Dictionary mapping installable names to their status
        """
        with self._lock:
            status = {}
            for name, installable in self.installables.items():
                is_active = name == self.active_installable
                status[name] = "active" if is_active else "inactive"
            return status
    
    def get_installables_info(self) -> Dict[str, Dict[str, str]]:
        """
        Get detailed information about all installables.
        
        Returns:
            Dict[str, Dict[str, str]]: Dictionary mapping installable names to their info
        """
        with self._lock:
            info = {}
            for name, installable in self.installables.items():
                is_active = name == self.active_installable
                info[name] = {
                    "name": installable.name,
                    "description": installable.description,
                    "status": "active" if is_active else "inactive"
                }
            return info


def main():
    """Main function to run the orchestrator."""
    # Create a device instance (6 rows, 22 columns for standard Vestaboard)
    device = Device(
        rows=6,
        columns=22,
        active_installable="spotify"
    )
    
    # Create orchestrator
    orchestrator = Orchestrator(device)
    
    # List available installables
    orchestrator.list_installables()
    
    # Run with Spotify installable (default)
    orchestrator.run('spotify')


if __name__ == "__main__":
    main() 