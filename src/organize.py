import os
import shutil
from datetime import datetime
import mimetypes
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the path to the current directory
current_directory = os.getcwd()

# Function to move video files into folders based on their creation date
def organize_videos_by_date(directory):
    logging.info(f'Starting to organize videos in directory: {directory}')
    
    # Check and rename existing directories
    for item in os.listdir(directory):
        item_path = os.path.join(directory, item)
        if os.path.isdir(item_path):
            try:
                old_date = datetime.strptime(item, '%m-%d-%Y')
                new_date = old_date.strftime('%Y-%m-%d')
                new_date_directory = os.path.join(directory, new_date)
                if not os.path.exists(new_date_directory):
                    logging.info(f'Renaming directory {item} to {new_date}')
                    os.rename(item_path, new_date_directory)
            except ValueError:
                continue
    
    for filename in os.listdir(directory):
        file_path = os.path.join(directory, filename)
        
        logging.info(f'Processing file: {filename}')
        
        # Ignore folders, .toproj, and .bat files
        if not os.path.isfile(file_path) or file_path.endswith('.toproj') or file_path.endswith('.bat'):
            logging.info(f'Skipping folder, .toproj file, or .bat file: {filename}')
            continue
        
        # Skip files that are not .mp4
        if not filename.lower().endswith('.mp4'):
            logging.info(f'Skipping non-.mp4 file: {filename}')
            continue
        
        mime_type = mimetypes.guess_type(file_path)[0]
        if mime_type is not None and mime_type.startswith('video'):
            logging.info(f'Identified video file: {filename}')
            
            creation_time = os.path.getctime(file_path)
            creation_date = datetime.fromtimestamp(creation_time).strftime('%Y-%m-%d')
            date_directory = os.path.join(directory, creation_date)
            
            if not os.path.exists(date_directory):
                logging.info(f'Creating new directory for date: {creation_date}')
                os.makedirs(date_directory)
            
            # Check if the file is already in the correct directory
            if os.path.abspath(file_path).startswith(os.path.abspath(date_directory)):
                logging.info(f'File {filename} is already in the correct directory: {date_directory}')
                continue
            
            logging.info(f'Moving file {filename} to directory: {date_directory}')
            shutil.move(file_path, os.path.join(date_directory, filename))
        else:
            logging.info(f'File is not a video or MIME type could not be determined: {file_path}')
