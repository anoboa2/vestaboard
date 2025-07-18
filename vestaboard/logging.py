"""
Centralized logging configuration for the Vestaboard application.

This module provides a consistent logging interface across all components
with configurable log levels, structured output, and proper error handling.
"""

import logging
import sys
import os
from typing import Optional
from datetime import datetime

# Default logging configuration
DEFAULT_LOG_LEVEL = "INFO"
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

class VestaboardLogger:
    """
    Centralized logger for the Vestaboard application.
    
    Provides consistent logging across all components with configurable
    log levels and structured output.
    """
    
    def __init__(self, name: str, log_level: Optional[str] = None):
        """
        Initialize a logger for a specific component.
        
        Args:
            name: The name of the component (e.g., 'spotify', 'orchestrator')
            log_level: Optional log level override (defaults to environment or INFO)
        """
        self.logger = logging.getLogger(f"vestaboard.{name}")
        
        # Set log level from parameter, environment, or default
        level = log_level or os.getenv("VESTABOARD_LOG_LEVEL", DEFAULT_LOG_LEVEL)
        self.logger.setLevel(getattr(logging, level.upper(), logging.INFO))
        
        # Only add handler if none exists (prevents duplicate handlers)
        if not self.logger.handlers:
            handler = logging.StreamHandler(sys.stdout)
            formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)
            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
    
    def debug(self, message: str, **kwargs):
        """Log a debug message."""
        self.logger.debug(message, extra=kwargs)
    
    def info(self, message: str, **kwargs):
        """Log an info message."""
        self.logger.info(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log a warning message."""
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """Log an error message."""
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log a critical message."""
        self.logger.critical(message, extra=kwargs)
    
    def exception(self, message: str, **kwargs):
        """Log an exception with traceback."""
        self.logger.exception(message, extra=kwargs)

def get_logger(name: str, log_level: Optional[str] = None) -> VestaboardLogger:
    """
    Get a logger instance for a specific component.
    
    Args:
        name: The name of the component
        log_level: Optional log level override
        
    Returns:
        VestaboardLogger: A configured logger instance
    """
    return VestaboardLogger(name, log_level)

# Convenience functions for common logging patterns
def log_component_start(component_name: str, **kwargs):
    """Log when a component starts."""
    logger = get_logger(component_name)
    logger.info(f"Starting {component_name} component", **kwargs)

def log_component_stop(component_name: str, **kwargs):
    """Log when a component stops."""
    logger = get_logger(component_name)
    logger.info(f"Stopping {component_name} component", **kwargs)

def log_api_request(component_name: str, endpoint: str, status_code: int, **kwargs):
    """Log API request details."""
    logger = get_logger(component_name)
    level = "error" if status_code >= 400 else "info"
    getattr(logger, level)(f"API request to {endpoint} returned {status_code}", 
                          endpoint=endpoint, status_code=status_code, **kwargs)

def log_board_update(component_name: str, success: bool, refresh_time: int, **kwargs):
    """Log board update attempts."""
    logger = get_logger(component_name)
    if success:
        logger.info(f"Board updated successfully, next refresh in {refresh_time}ms", 
                   refresh_time=refresh_time, **kwargs)
    else:
        logger.error("Board update failed", refresh_time=refresh_time, **kwargs)

def log_installable_switch(component_name: str, from_installable: str, to_installable: str, **kwargs):
    """Log when switching between installables."""
    logger = get_logger(component_name)
    logger.info(f"Switching from {from_installable} to {to_installable}", 
               from_installable=from_installable, to_installable=to_installable, **kwargs) 