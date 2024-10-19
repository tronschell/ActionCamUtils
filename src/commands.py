"""Module containing command handling functions."""

import os
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from config import get_config_value, save_config
from logging_setup import setup_logger
from organize import organize_videos_by_date
from utils import change_directory, check_directory_exists
from video_append import run_ffmpeg
from video_import import import_videos, select_directory

console = Console()
logger = setup_logger(__name__)

breadcrumb_path = ["Main Menu"]


def update_breadcrumb(action: str) -> None:
    """Update the breadcrumb path with the current action.

    Args:
        action (str): The current action to add to the breadcrumb path.
    """
    breadcrumb_path.append(action)
    breadcrumb_text = ' > '.join(breadcrumb_path)
    console.print(Panel(breadcrumb_text, title="",
                  style="bold blue", expand=False))


def clear_screen() -> None:
    """Clear the terminal screen."""
    os.system('cls' if os.name == 'nt' else 'clear')


def get_directory(config_key: str, directory_type: str) -> str:
    """Get and validate a directory from the configuration.

    Args:
        config_key (str): The configuration key for the directory.
        directory_type (str): The type of directory ('input' or 'output').

    Returns:
        str: The validated directory path or an empty string if invalid.
    """
    directory = get_config_value(config_key)
    if not directory or not check_directory_exists(directory, directory_type):
        console.print(
            f"No valid {directory_type} directory set. Please select option 3 to set the {directory_type} directory.", style="bold red")
        return ""
    return directory


def handle_organize_videos() -> None:
    """Handle the organization of videos by date in the output directory."""
    clear_screen()
    update_breadcrumb("Organize Videos")
    output_directory = get_directory('output_directory', 'output')
    if not output_directory:
        breadcrumb_path.pop()
        return
    organize_videos_by_date(output_directory)
    console.print(
        f"Videos in {output_directory} have been organized by date.", style="bold green")
    breadcrumb_path.pop()


def handle_concatenate_videos() -> None:
    """Handle the concatenation of video files from the input directory to the output directory."""
    clear_screen()
    update_breadcrumb("Concatenate Videos")
    input_directory = get_directory('input_directory', 'input')
    output_directory = get_directory('output_directory', 'output')
    if not input_directory or not output_directory:
        breadcrumb_path.pop()
        return

    while True:
        console.print("Select an option:", style="bold green")
        console.print(
            "1. Select specific video files through the native file browser")
        console.print("2. Automatically append all video files")
        console.print("3. Back to main menu")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if choice == "1":
            update_breadcrumb("Select Specific Files")
            run_ffmpeg_with_error_handling(
                input_directory, output_directory, True)
            breadcrumb_path.pop()
            break
        elif choice == "2":
            handle_automatic_append(output_directory)
            break
        elif choice == "3":
            breadcrumb_path.pop()
            break

    console.print(
        "FFmpeg script has been run and the output directory has been opened.", style="bold green")
    breadcrumb_path.pop()
    clear_screen()  # Clear the screen before returning to the main menu


def handle_automatic_append(output_directory: str) -> None:
    """Handle the automatic appending of video files."""
    while True:
        console.print("Select an option:", style="bold green")
        console.print("1. Select a directory via the native file browser")
        console.print(
            "2. Use the output directory specified in the config.ini file")
        console.print("3. Back to previous menu")

        sub_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if sub_choice == "1":
            update_breadcrumb("Select Directory via File Browser")
            selected_directory = select_directory(
                "Select Directory Containing Video Files")
            if selected_directory:
                run_ffmpeg_with_error_handling(
                    selected_directory, output_directory, False)
            else:
                console.print("No directory selected.", style="bold red")
            breadcrumb_path.pop()
            break
        elif sub_choice == "2":
            update_breadcrumb("Use Config Output Directory")
            run_ffmpeg_with_error_handling(
                output_directory, output_directory, False)
            breadcrumb_path.pop()
            break
        elif sub_choice == "3":
            breadcrumb_path.pop()
            break


def run_ffmpeg_with_error_handling(input_directory: str, output_directory: str, select_files_option: bool) -> None:
    """Run FFmpeg with error handling.

    Args:
        input_directory (str): The input directory for video files.
        output_directory (str): The output directory for concatenated videos.
        select_files_option (bool): Whether to select specific files.
    """
    try:
        run_ffmpeg(input_directory, output_directory, select_files_option)
        console.print("FFmpeg script has been run successfully.",
                      style="bold green")
        console.print("Press Enter to go back to the main menu...")
        input()  # Wait for user input
        clear_screen()
    except Exception as e:
        console.print(f"Error: {e}", style="bold red")
        logger.error("Error running FFmpeg: %s", e, exc_info=True)


def handle_transfer_videos() -> None:
    """Handle the transfer of video files from the input directory to the output directory."""
    clear_screen()
    update_breadcrumb("Transfer Videos")
    input_directory = get_config_value('input_directory')
    output_directory = get_config_value('output_directory')

    input_directory = handle_directory_selection(
        'input_directory', input_directory, 'input')
    if not input_directory:
        breadcrumb_path.pop()
        return

    output_directory = handle_directory_selection(
        'output_directory', output_directory, 'output')
    if not output_directory:
        breadcrumb_path.pop()
        return

    # Ask about organizing by date
    organize_by_date = Prompt.ask(
        "Do you want to organize videos by date? ([bold magenta]y/n[/bold magenta])").strip().lower() == 'y'
    import_videos(input_directory, console, organize_by_date)
    breadcrumb_path.pop()


def handle_directory_selection(config_key: str, current_directory: str, directory_type: str) -> str:
    """Handle the selection of a directory, either from config or user input.

    Args:
        config_key (str): The configuration key for the directory.
        current_directory (str): The current directory path.
        directory_type (str): The type of directory ('input' or 'output').

    Returns:
        str: The selected or current directory path.
    """
    if not current_directory or not check_directory_exists(current_directory, directory_type):
        new_directory = select_directory(
            f"Select {directory_type.capitalize()} Directory")
        if new_directory:
            save_config(config_key, new_directory)
            console.print(
                f"{directory_type.capitalize()} directory set to: {new_directory}", style="bold green")
            return new_directory
        else:
            console.print(
                f"No {directory_type} directory selected.", style="bold red")
            return ""
    else:
        change_directory_prompt = Prompt.ask(
            f"Current {directory_type} directory is '[bold cyan]{current_directory}[/bold cyan]'. "
            "Press [bold magenta]Enter[/bold magenta] to skip changing it or type '[bold magenta]y[/bold magenta]' to change"
        )
        if change_directory_prompt.strip().lower() == 'y':
            new_directory = select_directory(
                f"Select New {directory_type.capitalize()} Directory")
            if new_directory:
                save_config(config_key, new_directory)
                console.print(
                    f"{directory_type.capitalize()} directory set to: {new_directory}", style="bold green")
                return new_directory
            else:
                console.print(
                    f"No new {directory_type} directory selected. Using the current one.", style="bold yellow")
    return current_directory


def handle_settings() -> None:
    """Handle the settings menu to change input and output directories."""
    clear_screen()
    update_breadcrumb("Settings")
    current_input_directory = get_config_value('input_directory')
    current_output_directory = get_config_value('output_directory')

    while True:
        console.print("Settings:", style="bold green")
        console.print(
            f"1. Change input directory ([bold yellow]{current_input_directory}[/bold yellow])")
        console.print(
            f"2. Change output directory ([bold yellow]{current_output_directory}[/bold yellow])")
        console.print("3. Back to main menu")

        settings_choice = Prompt.ask(
            "Enter your choice", choices=["1", "2", "3"])

        if settings_choice == "1":
            update_breadcrumb("Change Input Directory")
            change_directory('input')
            current_input_directory = get_config_value(
                'input_directory')  # Update the current directory
            breadcrumb_path.pop()
        elif settings_choice == "2":
            update_breadcrumb("Change Output Directory")
            change_directory('output')
            current_output_directory = get_config_value(
                'output_directory')  # Update the current directory
            breadcrumb_path.pop()
        elif settings_choice == "3":
            breadcrumb_path.pop()
            break
