"""Module handling the setup of the logger"""

import os
from datetime import datetime
import logging
from logging.handlers import TimedRotatingFileHandler


def setup_logger(name: str) -> logging.Logger:
    """Set up a logger that outputs logs to a file with the specified date format.

    Args:
        name (str): The name of the logger.

    Returns:
        logging.Logger: Configured logger instance.
    """
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up logging
    date_str = datetime.now().strftime("%m-%d-%Y")
    log_filename = f'logs/{date_str}-log.log'
    log_handler = TimedRotatingFileHandler(
        log_filename, when='midnight', interval=1)
    log_handler.suffix = "%Y-%m-%d"
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s - %(pathname)s:%(lineno)d')
    log_handler.setFormatter(formatter)

    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # Remove any existing handlers
    logger.handlers = []

    # Add the file handler only
    logger.addHandler(log_handler)

    return logger
