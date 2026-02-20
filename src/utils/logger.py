"""Logging configuration using loguru."""

import sys
from pathlib import Path

from loguru import logger

from src.utils.config import PROJECT_ROOT, settings

# Create logs directory
LOG_DIR = PROJECT_ROOT / "logs"
try:
    LOG_DIR.mkdir(exist_ok=True)
except (PermissionError, OSError):
    # Fallback for environments with restricted permissions like Hugging Face Spaces
    LOG_DIR = Path("/tmp/logs")
    LOG_DIR.mkdir(exist_ok=True, parents=True)
    print(f"⚠️ Permission denied for local logs. Using fallback: {LOG_DIR}")

# Remove default handler
logger.remove()

# Add console handler
logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level=settings.log_level,
    colorize=True,
)

# Add file handler
logger.add(
    LOG_DIR / "app_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="10 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level=settings.log_level,
)

# Add error file handler
logger.add(
    LOG_DIR / "error_{time:YYYY-MM-DD}.log",
    rotation="500 MB",
    retention="30 days",
    compression="zip",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
)


def get_logger(name: str):
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name (usually __name__)
        
    Returns:
        Logger instance
    """
    return logger.bind(name=name)
