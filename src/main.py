# src/main.py
import os
from rich.console import Console
from rich.prompt import Prompt
from config import load_config
from commands import handle_organize_videos, handle_concatenate_videos, handle_transfer_videos, handle_settings
from logging_setup import setup_logger

logger = setup_logger(__name__)

console = Console()

# Constants for menu choices
ORGANIZE_VIDEOS = "1"
CONCATENATE_VIDEOS = "2"
TRANSFER_VIDEOS = "3"
SETTINGS = "4"
EXIT = "5"

def display_menu() -> None:
    """Display the available commands to the user."""
    console.print("Available commands:", style="bold green")
    console.print(f"{ORGANIZE_VIDEOS}. Organize videos by date")
    console.print(f"{CONCATENATE_VIDEOS}. Concatenate videos")
    console.print(f"{TRANSFER_VIDEOS}. Transfer videos to output directory")
    console.print(f"{SETTINGS}. Settings")
    console.print(f"{EXIT}. Exit")

def main() -> None:
    """Main function to run the application."""
    load_config()

    commands = {
        ORGANIZE_VIDEOS: handle_organize_videos,
        CONCATENATE_VIDEOS: handle_concatenate_videos,
        TRANSFER_VIDEOS: handle_transfer_videos,
        SETTINGS: handle_settings,
        EXIT: lambda: console.print("Exiting...", style="bold red")
    }

    while True:
        display_menu()
        choice = Prompt.ask("Enter your choice", choices=[ORGANIZE_VIDEOS, CONCATENATE_VIDEOS, TRANSFER_VIDEOS, SETTINGS, EXIT])

        if choice == EXIT:
            logger.info("Exiting the application")
            break

        command = commands.get(choice)
        if command:
            try:
                logger.info(f"Executing command: {choice}")
                command()
            except Exception as e:
                logger.error(f"Error executing command {choice}: {e}")
                console.print(f"An error occurred: {e}", style="bold red")
        else:
            console.print("Invalid choice. Please try again.", style="bold red")

if __name__ == "__main__":
    main()