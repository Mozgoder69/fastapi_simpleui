# myrich.py
import logging
import logging.config
import sys
import traceback

from rich.console import Console
from rich.traceback import install

# Configure rich library to display enhanced tracebacks with local variable details.
install(
    show_locals=True,
    locals_max_length=1,
    locals_max_string=18,
    width=72,
    extra_lines=0,
    indent_guides=False,
    max_frames=1,
)

console = Console()

# Configuration dictionary for logging
log_cfg = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(message)s [%(filename)s:%(lineno)d] ",
            "datefmt": "[%X]",
        },
    },
    "handlers": {
        "console": {
            "class": "rich.logging.RichHandler",
            "level": "DEBUG",
            "formatter": "default",
            "rich_tracebacks": True,
            "markup": True,
            "show_time": True,
            "show_level": True,
        },
        "file": {
            "class": "logging.FileHandler",
            "filename": "app.log",
            "level": "DEBUG",
            "formatter": "default",
        },
    },
    "root": {"handlers": ["console", "file"], "level": "DEBUG"},
}

# Apply the logging configuration
logging.config.dictConfig(log_cfg)

# Get a logger object for use throughout the application
logger = logging.getLogger("RichLogger")

# Preserve the original exception hook
original_excepthook = sys.excepthook


def rich_excepthook(exc_type, exc_value, exc_traceback):
    """Custom exception hook using Rich for detailed tracebacks in console."""
    if exc_traceback:
        tb = traceback.extract_tb(exc_traceback)
        last_call = tb[-1]
        error_msg = f"Err {exc_type}.{exc_value} in Fun {last_call.name}; Line {last_call.lineno} in File {last_call.path}"
        try:
            console.print(error_msg, style="bold red")
        except Exception as e:
            logger.error("Error in rich_excepthook: %s", e)
    else:
        original_excepthook(exc_type, exc_value, traceback.format_exc())


# Replace the system default exception hook with our custom hook
sys.excepthook = rich_excepthook
