import os
import shutil
from tkinter import Tk, filedialog
from rich.prompt import Prompt
from rich.console import Console
from tqdm import tqdm
from typing import Optional
from config import get_config_value, save_config

def select_directory(title: str) -> str:
    """Open a file dialog to select a directory.

    Args:
        title (str): The title of the file dialog.

    Returns:
        str: The selected directory path.
    """
    root = Tk()
    root.withdraw()  # Hide the root window
    directory = filedialog.askdirectory(title=title)
    root.destroy()
    return directory

def import_videos(input_directory: str, console: Optional[Console] = None) -> None:
    """Import videos from the selected directory and ask whether to delete or keep the videos.

    Args:
        input_directory (str): The directory containing the video files.
        console (Optional[Console]): The rich console instance for printing messages.
    """
    output_directory = get_config_value('output_directory')
    if not output_directory:
        output_directory = select_directory("Select Output Directory for Imported Videos")
        if output_directory:
            save_config('output_directory', output_directory)
            if console:
                console.print(f"Output directory set to: {output_directory}", style="bold green")
        else:
            if console:
                console.print("No output directory selected.", style="bold red")
            return

    delete_choice = Prompt.ask("Do you want to delete the videos from the source directory after importing them?", choices=["yes", "no"])
    mp4_files = [f for f in os.listdir(input_directory) if f.lower().endswith('.mp4')]
    
    with tqdm(total=len(mp4_files), desc="Overall Progress", unit="file") as overall_pbar:
        for filename in mp4_files:
            source_path = os.path.join(input_directory, filename)
            destination_path = os.path.join(output_directory, filename)
            move_file_with_progress(source_path, destination_path)
            overall_pbar.update(1)
            if console:
                console.print(f"Moved {filename} to {output_directory}/", style="bold green")

    if delete_choice.lower() == "yes":
        for filename in mp4_files:
            file_path = os.path.join(input_directory, filename)
            if os.path.isfile(file_path):
                os.remove(file_path)
        if console:
            console.print("Videos deleted from the source directory.", style="bold green")
    else:
        if console:
            console.print("Videos kept in the source directory.", style="bold green")

def move_file_with_progress(source: str, destination: str) -> None:
    """Move a file with a progress bar.

    Args:
        source (str): The source file path.
        destination (str): The destination file path.
    """
    total_size = os.path.getsize(source)
    with tqdm(total=total_size, unit='B', unit_scale=True, desc=os.path.basename(source)) as pbar:
        with open(source, 'rb') as src, open(destination, 'wb') as dst:
            while True:
                buffer = src.read(1024 * 1024)  # Read in chunks of 1MB
                if not buffer:
                    break
                dst.write(buffer)
                pbar.update(len(buffer))
    os.remove(source)