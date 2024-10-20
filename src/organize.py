"""Module to organize videos by date."""

import os
import shutil
from datetime import datetime
import mimetypes
from logging_setup import setup_logger

logger = setup_logger(__name__)

# Function to move video files into folders based on their creation date


def organize_videos_by_date(directory):
    """
    Organize video files into folders based on their creation date.

    Args:
        directory (str): The directory to organize videos in.

    Returns:
        None
    """
    # Ensure the directory exists
    if not os.path.exists(directory):
        logger.error("Directory does not exist: %s", directory)
        return

    logger.info('Starting to organize videos in directory: %s', directory)

    # Check and rename existing directories
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            try:
                old_date = datetime.strptime(item, '%m-%d-%Y')
                new_date = old_date.strftime('%Y-%m-%d')
                new_date_directory = os.path.join(directory, new_date)
                if not os.path.exists(new_date_directory):
                    logger.info('Renaming directory %s to %s', item, new_date)
                    os.rename(item_path, new_date_directory)
            except ValueError:
                continue

    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)

        logger.info("Processing file: %s", filename)

        # Ignore folders, .toproj, and .bat files
        if not os.path.isfile(file_path) or file_path.endswith('.toproj') or file_path.endswith('.bat'):
            logger.info(
                "Skipping folder, .toproj file, or .bat file: %s", filename)
            continue

        # Skip files that are not .mp4
        if not filename.lower().endswith('.mp4'):
            logger.info("Skipping non-.mp4 file: %s", filename)
            continue

        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type is not None and mime_type.startswith('video'):
            logger.info("Identified video file: %s", filename)

            creation_time = os.path.getctime(file_path)
            creation_date = datetime.fromtimestamp(
                creation_time).strftime('%Y-%m-%d')
            date_directory = os.path.join(directory, creation_date)

            if not os.path.exists(date_directory):
                logger.info("Creating new directory for date: %s",
                            creation_date)
                os.makedirs(date_directory)

            # Check if the file is already in the correct directory
            if os.path.abspath(file_path).startswith(os.path.abspath(date_directory)):
                logger.info(
                    "File %s is already in the correct directory: %s", filename, date_directory)
                continue

            logger.info('Moving file %s to directory: %s',
                        filename, date_directory)
            shutil.move(file_path, os.path.join(date_directory, filename))
        else:
            logger.info(
                'File is not a video or MIME type could not be determined: %s', file_path)
