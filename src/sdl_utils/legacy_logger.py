"""
A light-weight logger for SDL
Author: Yang Cao, Acceleration Consortium
Version: 0.1

A list of functions:
 - get_logger(logger_name)
"""

import os
import sys
import socket
import getpass
import logging
from datetime import datetime


def get_logger(
        logger_name: str
) -> logging.Logger:

    """
    Creates and configures a logger with the following filename format:
        <hostname>_<username>_<logger_name>_<timestamp>.log
    The log file is placed in the ~/Logs directory.

    :param logger_name: The name of the logger to create.
    :return: A configured logger instance.
    """

    # Get the local machine name (computer name)
    hostname = socket.gethostname()
    # Get the local user who is running this script
    username = getpass.getuser()

    # Create a "Logs" folder in the user's home directory if it doesn't exist
    # These logs and then be backed up using another utility
    logs_dir = os.path.join(os.path.expanduser("~"), "Logs")
    os.makedirs(logs_dir, exist_ok=True)

    # Generate a timestamp for the log filename
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")

    # Build the log filename and path
    log_filename = f"{hostname}_{username}_{logger_name}_{timestamp}.log"
    log_path = os.path.join(logs_dir, log_filename)

    # Create and configure the logger
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Create a file handler to write logs to our log file
    file_handler = logging.FileHandler(log_path)
    file_handler.setLevel(logging.DEBUG)

    # Set a log message format
    formatter = logging.Formatter(
        fmt="%(asctime)s - [%(levelname)s] - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    file_handler.setFormatter(formatter)

    # Avoid adding multiple handlers if logger is already used
    if not logger.handlers:
        logger.addHandler(file_handler)

    # Also output the stout by streaming the output
    logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger


if __name__ == "__main__":
    """
    Example usage of the sdl_logger module.
    """
    # Create a logger named "example_logger"
    test_logger = get_logger("example_logger")

    # Log a few sample messages
    test_logger.debug("Debug message.")
    test_logger.info("Info message.")
    test_logger.warning("Warning message.")
    test_logger.error("Error message.")
    test_logger.critical("Critical message.")

