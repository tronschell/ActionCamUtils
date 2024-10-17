# src/commands.py
import os
from rich.console import Console
from rich.prompt import Prompt
from organize import organize_videos_by_date
from video_append import run_ffmpeg
from config import get_config_value, save_config
from video_import import import_videos
from utils import check_directory_exists, change_directory

console = Console()

def handle_organize_videos() -> None:
    input_directory = get_config_value('input_directory')
    if not input_directory or not check_directory_exists(input_directory, 'input'):
        console.print("No valid input directory set. Please select option 3 to set the input directory.", style="bold red")
        return
    organize_videos_by_date(input_directory)
    console.print(f"Videos in {input_directory} have been organized by date.", style="bold green")

def handle_concatenate_videos() -> None:
    input_directory = get_config_value('input_directory')
    output_directory = get_config_value('output_directory')
    if not input_directory or not check_directory_exists(input_directory, 'input'):
        console.print("No valid input directory set. Please select option 3 to set the input directory.", style="bold red")
        return
    if not output_directory or not check_directory_exists(output_directory, 'output'):
        console.print("No valid output directory set. Please select option 3 to set the output directory.", style="bold red")
        return
    select_files_option = Prompt.ask("Do you want to select specific files to concatenate?", choices=["yes", "no"]) == "yes"
    run_ffmpeg(input_directory, output_directory, select_files_option)
    console.print(f"FFmpeg script has been run in {input_directory} and the output directory has been opened.", style="bold green")

def handle_transfer_videos() -> None:
    input_directory = get_config_value('input_directory')
    output_directory = get_config_value('output_directory')
    if input_directory:
        if not check_directory_exists(input_directory, 'input'):
            return
        console.print(f"Input directory already set to: {input_directory}", style="bold green")
    else:
        input_directory = select_directory("Select Input Directory Containing Video Files")
        if input_directory:
            save_config('input_directory', input_directory)
            console.print(f"Input directory set to: {input_directory}", style="bold green")
        else:
            console.print("No directory selected.", style="bold red")
            return

    if output_directory:
        if not check_directory_exists(output_directory, 'output'):
            return
        console.print(f"Output directory already set to: {output_directory}", style="bold green")
    else:
        output_directory = select_directory("Select Output Directory for Imported Videos")
        if output_directory:
            save_config('output_directory', output_directory)
            console.print(f"Output directory set to: {output_directory}", style="bold green")
        else:
            console.print("No output directory selected.", style="bold red")
            return

    import_videos(input_directory, console)

def handle_settings() -> None:
    current_input_directory = get_config_value('input_directory')
    current_output_directory = get_config_value('output_directory')

    console.print("Settings:", style="bold green")
    console.print(f"1. Change input directory ([bold yellow]{current_input_directory}[/bold yellow])")
    console.print(f"2. Change output directory ([bold yellow]{current_output_directory}[/bold yellow])")

    settings_choice = Prompt.ask("Enter your choice", choices=["1", "2"])

    if settings_choice == "1":
        change_directory('input')
    elif settings_choice == "2":
        change_directory('output')