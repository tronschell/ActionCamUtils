from rich.console import Console
from rich.prompt import Prompt
from organize import organize_videos_by_date
from video_append import run_ffmpeg
from config import get_config_value, save_config
from video_import import import_videos, select_directory
from utils import check_directory_exists, change_directory
import logging

console = Console()
logger = logging.getLogger(__name__)

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
    output_directory = get_directory('output_directory', 'output')
    if not output_directory:
        return
    organize_videos_by_date(output_directory)
    console.print(f"Videos in {output_directory} have been organized by date.", style="bold green")

def handle_concatenate_videos() -> None:
    input_directory = get_directory('input_directory', 'input')
    output_directory = get_directory('output_directory', 'output')
    if not input_directory or not output_directory:
        return
    select_files_option = Prompt.ask("Do you want to select specific files to concatenate?", choices=["yes", "no"]) == "yes"
    run_ffmpeg(input_directory, output_directory, select_files_option)
    console.print(f"FFmpeg script has been run in {input_directory} and the output directory has been opened.", style="bold green")

def handle_transfer_videos() -> None:
    input_directory = get_config_value('input_directory')
    output_directory = get_config_value('output_directory')

    if not input_directory:
        input_directory = select_directory("Select Input Directory Containing Video Files")
        if input_directory:
            save_config('input_directory', input_directory)
            console.print(f"Input directory set to: {input_directory}", style="bold green")
        else:
            console.print("No directory selected.", style="bold red")
            return
    elif not check_directory_exists(input_directory, 'input'):
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
            return
    elif not check_directory_exists(output_directory, 'output'):
        return
    else:
        console.print(f"Output directory already set to: {output_directory}", style="bold green")

    import_videos(input_directory, console)

def handle_settings() -> None:
    current_input_directory = get_config_value('input_directory')
    current_output_directory = get_config_value('output_directory')

    while True:
        console.print("Settings:", style="bold green")
        console.print(f"1. Change input directory ([bold yellow]{current_input_directory}[/bold yellow])")
        console.print(f"2. Change output directory ([bold yellow]{current_output_directory}[/bold yellow])")
        console.print("3. Back to main menu")

        settings_choice = Prompt.ask("Enter your choice", choices=["1", "2", "3"])

        if settings_choice == "1":
            change_directory('input')
            current_input_directory = get_config_value('input_directory')  # Update the current directory
        elif settings_choice == "2":
            change_directory('output')
            current_output_directory = get_config_value('output_directory')  # Update the current directory
        elif settings_choice == "3":
            break