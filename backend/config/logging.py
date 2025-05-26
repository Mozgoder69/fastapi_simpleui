# backend/config/logging.py

"""Configuration for application logging."""

import logging
import logging.config

from config.settings import settings
from rich.logging import RichHandler

# Configuration dictionary for logging
log_cfg = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": settings.logging.logfmt_default,
        },
        "details": {
            "format": settings.logging.logfmt_details,
            "datefmt": settings.logging.log_datefmt,
        },
    },
    "handlers": {
        "dev_terminal": {
            "class": settings.logging.dev_terminal_class,
            "level": settings.logging.dev_terminal_level,
            "formatter": "default",
            "rich_tracebacks": settings.logging.dev_terminal_rich_tracebacks,
            "markup": settings.logging.dev_terminal_markup,
            "log_time_format": settings.logging.log_datefmt,
        },
        "logs_history": {
            "class": settings.logging.logs_history_class,
            "level": settings.logging.logs_history_level,
            "formatter": "details",
            "filename": settings.logging.logs_history_filename,
        },
        "prod_console": {
            "class": settings.logging.prod_console_class,
            "level": settings.logging.prod_console_level,
            "formatter": "default",
            "stream": settings.logging.prod_console_stream,
        },
    },
    "loggers": {
        "uvicorn": {
            "handlers": ["dev_terminal", "prod_console"],
            "level": "INFO",
            "propagate": False,
        },
        "root": {  # Root logger
            "handlers": ["dev_terminal", "logs_history", "prod_console"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# Apply the logging configuration
logging.config.dictConfig(log_cfg)
logging.getLogger("uvicorn.access").handlers = []
logger = logging.getLogger(__name__)
"""Logger instance for the logging module."""
