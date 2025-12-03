"""Application-wide logging configuration utilities."""

from __future__ import annotations

import logging

LOG_FORMAT = "%(asctime)s [%(levelname)s] %(name)s - %(message)s"


def configure_logging(level: int = logging.INFO, log_file: str | None = None) -> None:
    """Configure logging for the application.

    Args:
        level: Logging level to set globally.
        log_file: Optional path to a log file. If provided, file handler is added.
    """
    logging.basicConfig(level=level, format=LOG_FORMAT)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        formatter = logging.Formatter(LOG_FORMAT)
        file_handler.setFormatter(formatter)
        root_logger = logging.getLogger()
        root_logger.addHandler(file_handler)


def get_logger(name: str) -> logging.Logger:
    """Create a logger with consistent formatting.

    Args:
        name: Module or component name.

    Returns:
        Configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    return logger
