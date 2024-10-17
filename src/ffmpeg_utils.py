import os
import ffmpeg
import logging

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

    logging.info(f"Constructed FFmpeg concat command: {concat_output_args.compile()}")

    try:
        logging.info(f"Running FFmpeg concat command in directory: {directory}")
        ffmpeg.run(concat_output_args)
    except ffmpeg.Error as e:
        error_message = e.stderr.decode() if e.stderr else str(e)
        logging.error(f"Error running FFmpeg concat script: {error_message}")
        print(f"Error running FFmpeg concat script: {error_message}")
        raise
    except Exception as e:
        logging.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        raise