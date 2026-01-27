"""
Structured logging configuration using python-json-logger.

Provides JSON-formatted logs for better parsing and monitoring.
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from pythonjsonlogger import jsonlogger


def setup_logging(log_level: str = "INFO") -> logging.Logger:
    """
    Configure application logging with JSON format and rotation.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)

    Returns:
        Configured logger instance
    """
    logger = logging.getLogger("deloculator")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()

    # JSON formatter
    json_formatter = jsonlogger.JsonFormatter(
        fmt="%(asctime)s %(name)s %(levelname)s %(message)s %(pathname)s %(lineno)d",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Console handler (JSON format for production)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(json_formatter)
    logger.addHandler(console_handler)

    # File handler with rotation (if logs directory exists)
    logs_dir = Path(__file__).parent.parent.parent.parent / "logs"
    if logs_dir.exists() or True:  # Create if doesn't exist
        logs_dir.mkdir(exist_ok=True)
        log_file = logs_dir / "deloculator.log"

        # Rotating file handler: 10MB per file, keep 5 backup files
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=10 * 1024 * 1024,  # 10MB
            backupCount=5,
            encoding="utf-8"
        )
        file_handler.setFormatter(json_formatter)
        logger.addHandler(file_handler)

    return logger


# Global logger instance
logger = setup_logging()
