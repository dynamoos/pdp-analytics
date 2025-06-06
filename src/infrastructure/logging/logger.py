import sys
from pathlib import Path

from loguru import logger


def setup_logging(log_level: str = "INFO"):
    """Configure Loguru logging"""

    # Remove default logger
    logger.remove()

    # Console logging with color
    logger.add(
        sys.stdout,
        format="""<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level>
         | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan>
          - <level>{message}</level>""",
        level=log_level,
        colorize=True,
    )

    # File logging
    log_path = Path("logs")
    log_path.mkdir(exist_ok=True)

    logger.add(
        log_path / "app.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line}"
        " - {message}",
        level=log_level,
        rotation="100 MB",
        retention="30 days",
        compression="zip",
    )

    # Error log file
    logger.add(
        log_path / "error.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line}"
        " - {message}",
        level="ERROR",
        rotation="50 MB",
        retention="60 days",
        compression="zip",
    )

    logger.info(f"Logging configured with level: {log_level}")
