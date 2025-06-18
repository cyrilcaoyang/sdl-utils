import os
import sys
import socket
import getpass
from datetime import datetime
from loguru import logger

# --- Configuration ---
# Store configured loggers to avoid adding duplicate handlers
_configured_loggers = set()

def get_logger(logger_name: str):
    """
    Creates and configures a Loguru logger instance that writes to a specific file
    and maintains backward compatibility with the legacy logger's format and file naming.

    The log file is placed in the ~/Logs directory with the format:
        <hostname>_<username>_<logger_name>_<timestamp>.log

    Args:
        logger_name: The name of the logger, used in the filename.

    Returns:
        The configured Loguru logger instance.
    """
    # Only configure this specific file sink once
    if logger_name not in _configured_loggers:
        # Get machine and user details for the filename
        hostname = socket.gethostname()
        username = getpass.getuser()

        # Create the ~/Logs directory if it doesn't exist
        logs_dir = os.path.join(os.path.expanduser("~"), "Logs")
        os.makedirs(logs_dir, exist_ok=True)

        # Generate the timestamp and construct the log file path
        timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_filename = f"{hostname}_{username}_{logger_name}_{timestamp}.log"
        log_path = os.path.join(logs_dir, log_filename)
        
        # Define the legacy format
        log_format = "{time:YYYY-MM-DD HH:mm:ss} - [{level}] - {message}"

        # Add the file sink with the specified format and path
        logger.add(
            log_path,
            level="DEBUG",
            format=log_format,
            # Use a filter to ensure logs from this specific call go to the right file if needed,
            # though by default loguru sends all logs to all sinks.
            # filter=lambda record: record["extra"].get("name") == logger_name
        )
        
        # Mark this logger name as configured
        _configured_loggers.add(logger_name)

    # Return the logger instance bound with a specific name if you need to filter
    # For now, we return the global logger as per the new design.
    return logger

# --- Default Console Logger ---
# Remove the default handler and add our own simple one for console output
logger.remove()
logger.add(
    sys.stderr, 
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>"
)

# --- Optional Slack Integration ---
try:
    from .slack_loguru_sink import get_slack_sink
    slack_sink = get_slack_sink()
    if slack_sink:
        logger.add(slack_sink, level="ERROR", format="{message}")
        logger.info("Slack logging for ERROR level is configured.")
except ImportError:
    pass # This is expected if 'full' dependencies are not installed.
except Exception as e:
    logger.warning(f"Failed to configure Slack logging sink: {e}")

__all__ = ["get_logger", "logger"]
