"""
Logging configuration module for the TMDB Movie Recommendation application.
"""

import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

import colorlog


def setup_logger(
    name: str = "tmdb_app",
    log_level: str = "INFO",
    log_file: Optional[str] = None,
    max_bytes: int = 10485760,  # 10MB
    backup_count: int = 5,
    console_enabled: bool = True,
    file_enabled: bool = True,
) -> logging.Logger:
    """
    Configure and return a logger instance with file and console handlers.

    Args:
        name: Logger name
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Path to log file (if None, defaults to logs/app.log)
        max_bytes: Maximum size of log file before rotation
        backup_count: Number of backup files to keep
        console_enabled: Enable console logging
        file_enabled: Enable file logging

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # Define log format
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    # Console handler with color
    if console_enabled:
        console_handler = colorlog.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))

        # Colored formatter for console
        color_formatter = colorlog.ColoredFormatter(
            "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt=date_format,
            log_colors={
                "DEBUG": "cyan",
                "INFO": "green",
                "WARNING": "yellow",
                "ERROR": "red",
                "CRITICAL": "red,bg_white",
            },
        )
        console_handler.setFormatter(color_formatter)
        logger.addHandler(console_handler)

    # File handler with rotation
    if file_enabled:
        if log_file is None:
            log_file = "logs/app.log"

        # Ensure log directory exists
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(getattr(logging, log_level.upper()))

        # Standard formatter for file
        file_formatter = logging.Formatter(log_format, datefmt=date_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)

    # Prevent propagation to root logger
    logger.propagate = False

    return logger


def get_logger(name: str = "tmdb_app") -> logging.Logger:
    """
    Get an existing logger or create a new one with default settings.

    Args:
        name: Logger name

    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)

    # If logger has no handlers, set it up with defaults
    if not logger.handlers:
        log_level = os.getenv("LOG_LEVEL", "INFO")
        setup_logger(
            name=name,
            log_level=log_level,
            console_enabled=True,
            file_enabled=True,
        )

    return logger
