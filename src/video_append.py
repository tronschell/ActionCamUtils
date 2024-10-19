import os
import ffmpeg
from datetime import datetime
from rich.console import Console
from rich.prompt import Prompt
from tkinter import Tk, filedialog
from utils import get_unique_filename, get_video_files, create_vidlist_file
from logging_setup import setup_logger

logger = setup_logger(__name__)
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
        logger.error(f"No video files found in {input_directory}.")
        print(f"Error: No video files found in {input_directory}.")
        os.chdir(original_cwd)
        return

    logger.info(f"Video files to be processed: {video_files}")

    vidlist_path = create_vidlist_file(output_directory, video_files)
    logger.info(f"vidlist.txt path: {vidlist_path}")

    # Concatenate videos
    try:
        concat_videos(input_directory, vidlist_path, concat_filename)
    except Exception as e:
        logger.error(f"Error concatenating videos: {e}")
        os.chdir(original_cwd)
        return

    os.rename(concat_filename, final_filename)

    os.chdir(original_cwd)
    os.startfile(output_directory)

def concat_videos(directory: str, vidlist_path: str, concat_filename: str) -> None:
    """Concatenate video files using FFmpeg.

    Args:
        directory (str): The directory containing the video files.
        vidlist_path (str): The path to the vidlist.txt file.
        concat_filename (str): The output filename for the concatenated video.
    """
    input_args = ffmpeg.input(vidlist_path, format='concat', safe=0)
    concat_output_args = (
        ffmpeg
        .output(input_args, concat_filename, vcodec='copy', acodec='copy')
        .global_args('-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda', "-reset_timestamps", "1", "-avoid_negative_ts", "1", "-re")
    )

    logger.info(f"Constructed FFmpeg concat command: {concat_output_args.compile()}")

    try:
        logger.info(f"Running FFmpeg concat command in directory: {directory}")
        ffmpeg.run(concat_output_args)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        logger.error(f"Error running FFmpeg concat script: {error_message}")
        print(f"Error running FFmpeg concat script: {error_message}")
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        raise