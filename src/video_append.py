import os
import logging
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from tkinter import Tk, filedialog
from utils import get_unique_filename, get_video_files, create_vidlist_file
from ffmpeg_utils import concat_videos

# Create logs directory if it doesn't exist
if not os.path.exists('logs'):
    os.makedirs('logs')

# Set up logging
log_handler = logging.handlers.TimedRotatingFileHandler('logs/app.log', when='midnight', interval=1)
log_handler.suffix = "%Y-%m-%d"
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', handlers=[log_handler])

console = Console()

def select_files(title: str) -> list:
    """Open a file dialog to select multiple files.

    Args:
        title (str): The title of the file dialog.

    Returns:
        list: The selected file paths.
    """
    root = Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title=title)
    root.destroy()
    return list(file_paths)

def run_ffmpeg(input_directory: str, output_directory: str, select_files_option: bool) -> None:
    """Run the FFmpeg command in the specified directory to concatenate videos.

    Args:
        input_directory (str): The directory containing the video files.
        output_directory (str): The directory to save the vidlist.txt file and concatenated video.
        select_files_option (bool): Whether to allow the user to select specific files.
    """
    original_cwd = os.getcwd()
    os.chdir(input_directory)

    # Generate filenames
    concat_filename = os.path.join(output_directory, get_unique_filename(output_directory, "concat", "mp4"))
    final_filename = os.path.join(output_directory, get_unique_filename(output_directory, "output", "mp4"))

    if select_files_option:
        video_files = select_files("Select Video Files to Concatenate")
    else:
        video_files = [os.path.join(input_directory, f) for f in get_video_files(input_directory)]

    if not video_files:
        logging.error(f"No video files found in {input_directory}.")
        print(f"Error: No video files found in {input_directory}.")
        os.chdir(original_cwd)
        return

    logging.info(f"Video files to be processed: {video_files}")

    vidlist_path = create_vidlist_file(output_directory, video_files)
    logging.info(f"vidlist.txt path: {vidlist_path}")

    # Concatenate videos
    try:
        concat_videos(input_directory, vidlist_path, concat_filename)
    except Exception as e:
        logging.error(f"Error concatenating videos: {e}")
        os.chdir(original_cwd)
        return

    os.rename(concat_filename, final_filename)

    os.chdir(original_cwd)
    os.startfile(output_directory)