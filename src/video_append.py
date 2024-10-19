"""Module to concatenate video files using FFmpeg."""

import os
import platform
from tkinter import Tk, filedialog
from contextlib import contextmanager
import ffmpeg
from rich.console import Console
from utils import get_unique_filename, get_video_files, create_vidlist_file
from logging_setup import setup_logger

logger = setup_logger(__name__)
console = Console()


def select_files(title: str) -> list:
    """Open a file dialog to select multiple files."""
    root = Tk()
    root.withdraw()  # Hide the root window
    file_paths = filedialog.askopenfilenames(title=title)
    root.destroy()
    if not file_paths:
        logger.info("No files selected.")
        return []
    return list(file_paths)


@contextmanager
def change_dir(path):
    """Context manager for changing the current working directory."""
    origin = os.getcwd()
    try:
        os.chdir(path)
        yield
    finally:
        os.chdir(origin)


def run_ffmpeg(input_directory: str, output_directory: str, select_files_option: bool) -> None:
    """Run the FFmpeg command in the specified directory to concatenate videos."""
    with change_dir(input_directory):
        # Generate filenames
        concat_filename = os.path.join(
            output_directory, get_unique_filename(output_directory, "concat", "mp4"))
        final_filename = os.path.join(
            output_directory, get_unique_filename(output_directory, "output", "mp4"))

        if select_files_option:
            video_files = select_files("Select Video Files to Concatenate")
        else:
            video_files = [os.path.join(input_directory, f)
                           for f in get_video_files(input_directory)]

        if not video_files:
            logger.error("No video files found in %s.", input_directory)
            print(f"Error: No video files found in {input_directory}.")
            return

        logger.info("Video files to be processed: %s", video_files)

        vidlist_path = create_vidlist_file(output_directory, video_files)
        logger.info("vidlist.txt path: %s", vidlist_path)

        # Concatenate videos
        try:
            concat_videos(input_directory, vidlist_path, concat_filename)
        except ffmpeg.Error as e:
            logger.error("Error concatenating videos: %s", e, exc_info=True)
            print(f"Error: {e}")
        except Exception as e:  # Catch any other unexpected exceptions
            logger.error(
                "Unexpected error during concatenation: %s", e, exc_info=True)
            print(f"Unexpected error: {e}")
            return

        if os.path.exists(final_filename):
            logger.warning(
                "File %s already exists. Appending timestamp.", final_filename)
            final_filename = get_unique_filename(
                output_directory, "output", "mp4")

        os.rename(concat_filename, final_filename)

    open_output_directory(output_directory)


def concat_videos(directory: str, vidlist_path: str, concat_filename: str) -> None:
    """Concatenate video files using FFmpeg."""
    input_args = ffmpeg.input(vidlist_path, format='concat', safe=0)
    concat_output_args = (
        ffmpeg
        .output(input_args, concat_filename, vcodec='copy', acodec='copy')
        .global_args("-reset_timestamps", "1", "-avoid_negative_ts", "1", "-re")
    )

    # Attempt to use CUDA acceleration if available
    try:
        concat_output_args = concat_output_args.global_args(
            '-hwaccel', 'cuda', '-hwaccel_output_format', 'cuda')
    except ffmpeg.Error:
        logger.warning("CUDA acceleration not available. Falling back to CPU.")

    logger.info("Constructed FFmpeg concat command: %s",
                concat_output_args.compile())
    logger.info("Running FFmpeg concat command in directory: %s", directory)

    try:
        ffmpeg.run(concat_output_args)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        logger.error("Error running FFmpeg concat script: %s",
                     error_message, exc_info=True)
        print(f"Error running FFmpeg concat script: {error_message}")
        raise
    except Exception as e:
        logger.error("Unexpected error: %s", e, exc_info=True)
        print(f"Unexpected error: {e}")
        raise


def open_output_directory(path: str) -> None:
    """Open the output directory using the default file explorer."""
    try:
        if platform.system() == "Windows":
            os.startfile(path)
        elif platform.system() == "Darwin":  # macOS
            os.system(f"open {path}")
        else:  # Linux and other Unix-like
            os.system(f"xdg-open {path}")
    except Exception as e:
        logger.error("Failed to open output directory: %s", e)
        print(f"Output directory: {path}")
