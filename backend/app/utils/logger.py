"""
Logging Utility
===============
Centralized logging configuration for InfraPilot.

Good logging is critical for DevOps - it's how you debug production issues.
Structured logs (JSON format) are easier to parse with log aggregation tools
like Datadog, Elasticsearch, or CloudWatch.
"""

import logging
import sys
from app.config import settings


def setup_logging():
    """Configure the root logger for the application."""
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    # Format: timestamp | level | module | message
    log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    logging.basicConfig(
        level=log_level,
        format=log_format,
        datefmt=date_format,
        handlers=[
            logging.StreamHandler(sys.stdout),  # Print to console
        ]
    )

    # Reduce noise from third-party libraries
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("aiohttp").setLevel(logging.WARNING)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)

    logger = logging.getLogger("infrapilot")
    logger.info(f"Logging initialized at level: {settings.LOG_LEVEL}")


def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger. Use this in every module:

    from app.utils.logger import get_logger
    logger = get_logger(__name__)
    """
    return logging.getLogger(name)


# Initialize logging when this module is first imported
setup_logging()
