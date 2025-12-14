"""
Logging configuration for the Banking Docs-as-Code platform
"""

import logging
import sys
from pathlib import Path
from pythonjsonlogger import jsonlogger
from src.config import settings


def setup_logging():
    """
    Configure application logging with JSON formatting
    """
    # Create logs directory
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper()))

    # Remove existing handlers
    root_logger.handlers = []

    # Console handler with JSON formatting
    console_handler = logging.StreamHandler(sys.stdout)
    console_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(message)s",
        timestamp=True
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)

    # File handler for persistent logs
    file_handler = logging.FileHandler(log_dir / "app.log")
    file_formatter = jsonlogger.JsonFormatter(
        "%(asctime)s %(name)s %(levelname)s %(pathname)s %(funcName)s %(lineno)d %(message)s",
        timestamp=True
    )
    file_handler.setFormatter(file_formatter)
    root_logger.addHandler(file_handler)

    # Set third-party loggers to WARNING
    logging.getLogger("uvicorn").setLevel(logging.WARNING)
    logging.getLogger("fastapi").setLevel(logging.WARNING)
    logging.getLogger("neo4j").setLevel(logging.WARNING)

    return root_logger
