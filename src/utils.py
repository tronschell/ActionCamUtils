"""Module containing utility functions."""

import os
from datetime import datetime
from typing import List
from rich.console import Console
from rich.prompt import Prompt
from video_import import select_directory
from config import save_config, get_config_value
from logging_setup import setup_logger

logger = setup_logger(__name__)
console = Console()


def get_unique_filename(directory: str, base_name: str, extension: str) -> str:
    """Generate a unique filename in the specified directory.

    Args:
        directory (str): The directory to check for existing filenames.
        base_name (str): The base name for the filename.
        extension (str): The file extension.

    Returns:
        str: A unique filename.
    """
    today = datetime.now().strftime("%m-%d-%Y")
    filename = f"{base_name}_{today}.{extension}"
    count = 1

    while os.path.exists(os.path.join(directory, filename)):
        filename = f"{base_name}_{today}_{count}.{extension}"
        count += 1
        logger.debug("Checking for existing filename: %s", filename)

    logger.info("Generated unique filename: %s", filename)
    return filename


def get_video_files(directory: str) -> List[str]:
    """Get a list of video files in the specified directory.

    Args:
        directory (str): The directory to search for video files.

    Returns:
        List[str]: A list of video filenames.
    """
    video_extensions = ['.mp4', '.mov', '.avi', '.mkv']
    video_files = [f for f in os.listdir(directory) if os.path.splitext(f)[
        1].lower() in video_extensions]
    logger.info("Found video files in directory '%s': %s",
                directory, video_files)
    return video_files


def create_vidlist_file(output_directory: str, video_files: List[str]) -> str:
    """Create a vidlist.txt file with the list of video files.

    Args:
        output_directory (str): The directory to create the vidlist.txt file in.
        video_files (List[str]): The list of video files to include in the vidlist.txt file.

    Returns:
        str: The path to the created vidlist.txt file.
    """
    vidlist_path = os.path.join(output_directory, "vidlist.txt")
    with open(vidlist_path, 'w', encoding='utf-8') as vidlist_file:
        for video_file in video_files:
            vidlist_file.write(f"file '{video_file}'\n")

    logger.info("Created vidlist.txt at %s with %d video files",
                vidlist_path, len(video_files))

    # Log the contents of the vidlist.txt file
    with open(vidlist_path, 'r', encoding='utf-8') as vidlist_file:
        logger.info("Contents of %s:", vidlist_path)
        logger.info(vidlist_file.read())

    return vidlist_path


def check_directory_exists(directory: str, directory_type: str) -> bool:
    """Check if a directory exists and prompt the user to change it if it doesn't.

    Args:
        directory (str): The directory path to check.
        directory_type (str): The type of directory ('input' or 'output').

    Returns:
        bool: True if the directory exists or is changed successfully, False otherwise.
    """
    if not os.path.exists(directory):
        console.print(
            f"The {directory_type} directory '{directory}' does not exist.", style="bold red")
        logger.warning("The %s directory '%s' does not exist.",
                       directory_type, directory)
        change_choice = Prompt.ask(
            f"Do you want to change the {directory_type} directory?", choices=["yes", "no"])
        if change_choice.lower() == "yes":
            new_directory = select_directory(
                f"Select New {directory_type.capitalize()} Directory")
            if new_directory:
                save_config(f"{directory_type}_directory", new_directory)
                console.print(
                    f"{directory_type.capitalize()} directory set to: {new_directory}", style="bold green")
                logger.info("Changed %s directory to: %s",
                            directory_type, new_directory)
                return True
            else:
                console.print(
                    f"No {directory_type} directory selected.", style="bold red")
                logger.warning("No new %s directory selected.", directory_type)
                return False
        else:
            logger.info(
                "User chose not to change the %s directory.", directory_type)
            return False
    logger.info("The %s directory '%s' exists.", directory_type, directory)
    return True


def change_directory(directory_type: str) -> None:
    """Change the input or output directory in the configuration file.

    Args:
        directory_type (str): The type of directory ('input' or 'output').
    """
    current_directory = get_config_value(f"{directory_type}_directory")
    console.print(
        f"Current {directory_type} directory: {current_directory}", style="bold yellow")
    logger.info("Current %s directory: %s", directory_type, current_directory)
    new_directory = select_directory(
        f"Select New {directory_type.capitalize()} Directory")
    if new_directory:
        save_config(f"{directory_type}_directory", new_directory)
        console.print(
            f"{directory_type.capitalize()} directory set to: {new_directory}", style="bold green")
        logger.info("Changed %s directory to: %s",
                    directory_type, new_directory)
    else:
        console.print(
            f"No {directory_type} directory selected.", style="bold red")
        logger.warning("No new %s directory selected.", directory_type)
