from rich.console import Console
from rich.prompt import Prompt
from rich.panel import Panel
from organize import organize_videos_by_date
from video_append import run_ffmpeg
from config import get_config_value, save_config
from video_import import import_videos, select_directory
from utils import check_directory_exists, change_directory
from logging_setup import setup_logger
import os
from time import sleep

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
    console.print(Panel(breadcrumb_text, title="", style="bold blue", expand=False))

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
        console.print(f"No valid {directory_type} directory set. Please select option 3 to set the {directory_type} directory.", style="bold red")
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
    console.print(f"Videos in {output_directory} have been organized by date.", style="bold green")
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
        console.print("1. Select specific video files through the native file browser")
        console.print("2. Automatically append all video files")
        console.print("3. Back to main menu")

        choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if choice == "1":
            update_breadcrumb("Select Specific Files")
            select_files_option = True
            try:
                run_ffmpeg(input_directory, output_directory, select_files_option)
                console.print("FFmpeg script has been run successfully.", style="bold green")
                console.print("Press Enter to go back to the command screen or wait 5 seconds...")
                sleep(5)
                clear_screen()
            except Exception as e:
                console.print(f"Error: {e}", style="bold red")
                logger.error(f"Error running FFmpeg: {e}", exc_info=True)
            breadcrumb_path.pop()
            break
        elif choice == "2":
            update_breadcrumb("Automatically Append Files")
            while True:
                console.print("Select an option:", style="bold green")
                console.print("1. Select a directory via the native file browser")
                console.print("2. Use the output directory specified in the config.ini file")
                console.print("3. Back to previous menu")

                sub_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

                if sub_choice == "1":
                    update_breadcrumb("Select Directory via File Browser")
                    selected_directory = select_directory("Select Directory Containing Video Files")
                    if not selected_directory:
                        console.print("No directory selected.", style="bold red")
                        breadcrumb_path.pop()
                        continue
                    try:
                        run_ffmpeg(selected_directory, output_directory, False)
                        console.print("FFmpeg script has been run successfully.", style="bold green")
                        console.print("Press Enter to go back to the command screen or wait 5 seconds...")
                        sleep(5)
                        clear_screen()
                    except Exception as e:
                        console.print(f"Error: {e}", style="bold red")
                        logger.error(f"Error running FFmpeg: {e}", exc_info=True)
                    breadcrumb_path.pop()
                    break
                elif sub_choice == "2":
                    update_breadcrumb("Use Config Output Directory")
                    try:
                        run_ffmpeg(output_directory, output_directory, False)
                        console.print("FFmpeg script has been run successfully.", style="bold green")
                        console.print("Press Enter to go back to the command screen or wait 5 seconds...")
                        sleep(5)
                        clear_screen()
                    except Exception as e:
                        console.print(f"Error: {e}", style="bold red")
                        logger.error(f"Error running FFmpeg: {e}", exc_info=True)
                    breadcrumb_path.pop()
                    break
                elif sub_choice == "3":
                    breadcrumb_path.pop()
                    break
            if sub_choice == "3":
                continue
            break
        elif choice == "3":
            breadcrumb_path.pop()
            break

    console.print(f"FFmpeg script has been run and the output directory has been opened.", style="bold green")
    breadcrumb_path.pop()

def handle_transfer_videos() -> None:
    """Handle the transfer of video files from the input directory to the output directory."""
    clear_screen()
    update_breadcrumb("Transfer Videos")
    input_directory = get_config_value('input_directory')
    output_directory = get_config_value('output_directory')

    if not input_directory:
        input_directory = select_directory("Select Input Directory Containing Video Files")
        if input_directory:
            save_config('input_directory', input_directory)
            console.print(f"Input directory set to: {input_directory}", style="bold green")
        else:
            console.print("No directory selected.", style="bold red")
            breadcrumb_path.pop()
            return
    elif not check_directory_exists(input_directory, 'input'):
        breadcrumb_path.pop()
        return
    else:
        console.print(f"Input directory already set to: {input_directory}", style="bold green")

    if not output_directory:
        output_directory = select_directory("Select Output Directory for Imported Videos")
        if output_directory:
            save_config('output_directory', output_directory)
            console.print(f"Output directory set to: {output_directory}", style="bold green")
        else:
            console.print("No output directory selected.", style="bold red")
            breadcrumb_path.pop()
            return
    elif not check_directory_exists(output_directory, 'output'):
        breadcrumb_path.pop()
        return
    else:
        console.print(f"Output directory already set to: {output_directory}", style="bold green")

    import_videos(input_directory, console)
    breadcrumb_path.pop()

def handle_settings() -> None:
    """Handle the settings menu to change input and output directories."""
    clear_screen()
    update_breadcrumb("Settings")
    current_input_directory = get_config_value('input_directory')
    current_output_directory = get_config_value('output_directory')

    while True:
        console.print("Settings:", style="bold green")
        console.print(f"1. Change input directory ([bold yellow]{current_input_directory}[/bold yellow])")
        console.print(f"2. Change output directory ([bold yellow]{current_output_directory}[/bold yellow])")
        console.print("3. Back to main menu")

        settings_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if settings_choice == "1":
            update_breadcrumb("Change Input Directory")
            change_directory('input')
            current_input_directory = get_config_value('input_directory')  # Update the current directory
            breadcrumb_path.pop()
        elif settings_choice == "2":
            update_breadcrumb("Change Output Directory")
            change_directory('output')
            current_output_directory = get_config_value('output_directory')  # Update the current directory
            breadcrumb_path.pop()
        elif settings_choice == "3":
            breadcrumb_path.pop()
            break