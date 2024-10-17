# ActionCam Utils

ActionCam Utils is a Python-based utility designed to help users manage and process video files from action cameras such as GoPros or DJI Osmo Action cameras. This tool provides functionalities for importing, organizing, and concatenating video files using FFmpeg.

## Features

- **Import Videos**: Easily import videos from a selected directory.
- **Organize Videos**: Automatically organize videos into folders based on their creation date.
- **Concatenate Videos**: Concatenate multiple video files into a single file using FFmpeg.

## Installation

1. Clone the repository into your directory:
    ```sh
    git clone https://github.com/yourusername/actioncam_utils.git
    cd actioncam_utils
    ```

2. Install the required dependencies:
    ```sh
    pip install -r requirements.txt
    ```

2. Run the program:
    ```sh
    cd src
    python main.py
    ```

## Configuration

The configuration settings are stored in `config.ini`. You can edit this file to set the default input and output directories.

Example `config.ini`:
```
[DEFAULT]
input_directory = C:/your/input/directory
output_directory = D:/your/output/directory

```

## Contributing

Contributions are appreciated and welcome! If you have any improvements or new features to add, please fork the repository and submit a pull request. Make sure to follow the existing code style and include relevant tests for your changes.

## Author
Tron Schell (tron.schell@icloud.com)