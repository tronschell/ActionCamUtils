"""Main module for the application."""

import os
import logging
from rich.console import Console
from rich.prompt import Prompt
from config import load_config
from commands import (
    handle_concatenate_videos,
    handle_transfer_videos,
    handle_settings,
)
from logging_setup import setup_logger

logger = setup_logger(__name__)
console = Console()

# Constants for menu choices
CONCATENATE_VIDEOS = "1"
TRANSFER_VIDEOS = "2"
SETTINGS = "3"
EXIT = "4"
LOGGING_LEVEL = logging.WARNING  # Constant for logging level


def clear_screen() -> None:
    """Clear the console screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def display_menu() -> None:
    """Display the available commands to the user."""
    clear_screen()
    console.print("Available commands:", style="bold green")
    console.print(f"{CONCATENATE_VIDEOS}. Concatenate videos")
    console.print(f"{TRANSFER_VIDEOS}. Transfer videos to output directory")
    console.print(f"{SETTINGS}. Settings")
    console.print(f"{EXIT}. Exit")


def execute_command(choice: str) -> None:
    """Execute the command based on user choice."""
    commands = {
        CONCATENATE_VIDEOS: handle_concatenate_videos,
        TRANSFER_VIDEOS: handle_transfer_videos,
        SETTINGS: handle_settings,
        EXIT: lambda: console.print("Exiting...", style="bold red"),
    }

    command = commands.get(choice)
    if command:
        try:
            logger.info("Executing command: %s", choice)
            command()
        except Exception as e:
            logger.error("Error executing command %s: %s",
                         choice, e, exc_info=True)
            console.print(f"An error occurred: {e}", style="bold red")
    else:
        console.print("Invalid choice. Please try again.", style="bold red")


def main() -> None:
    """Main function to run the application."""
    load_config()

    while True:
        display_menu()
        choice = Prompt.ask("Enter your choice", choices=[
                            CONCATENATE_VIDEOS, TRANSFER_VIDEOS, SETTINGS, EXIT])

        if choice == EXIT:
            logger.setLevel(LOGGING_LEVEL)  # Set logger to WARNING level
            logger.info("Exiting the application")  # This will not be printed
            break

        execute_command(choice)


if __name__ == "__main__":
    main()
