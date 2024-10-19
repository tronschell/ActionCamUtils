"""Module to handle configuration."""

import os
from configparser import ConfigParser
from logging_setup import setup_logger

logger = setup_logger(__name__)

# Update the path to the config.ini file to be one level up from the current directory
config_file = os.path.join(os.path.dirname(
    os.path.dirname(__file__)), 'config.ini')
config = ConfigParser()


def load_config() -> None:
    """Load the configuration file."""
    if os.path.exists(config_file):
        config.read(config_file)
    else:
        config['DEFAULT'] = {'input_directory': '', 'output_directory': ''}
        with open(config_file, 'w', encoding='utf-8') as f:
            config.write(f)
        logger.info(
            "Configuration file created at %s with default values.", config_file)
    logger.info("Configuration loaded")


def save_config(key: str, value: str) -> None:
    """Save a key-value pair to the configuration file.

    Args:
        key (str): The configuration key.
        value (str): The configuration value.
    """
    config['DEFAULT'][key] = value
    with open(config_file, 'w', encoding='utf-8') as f:
        config.write(f)
    logger.info("Configuration saved: %s = %s", key, value)
    logger.debug("Configuration file content: %s", dict(config['DEFAULT']))


def get_config_value(key: str) -> str:
    """Get a value from the configuration file.

    Args:
        key (str): The configuration key.

    Returns:
        str: The configuration value.
    """
    return config['DEFAULT'].get(key, '')
