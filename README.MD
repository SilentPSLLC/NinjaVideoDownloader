# Ninja Video Downloader v1.2.0

Ninja Video Downloader is a tool for downloading and converting videos from popular video sites such as YouTube and TikTok. It leverages `yt-dlp` and `ffmpeg` for handling downloads and format conversions. 

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Linux Setup and Installation](#linux-setup-and-installation)
- [Windows Setup and Installation](#windows-setup-and-installation)
- [Usage](#usage)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)
- [Credits](#credits)
- [License](#license)
- [Contributing](#contributing)

---

## Project Overview

- **Version**: 2.1.2
- **Author**: Christopher Sparrowgrove
- **Product Name**: Ninja Video Downloader
- **Thank You Note**: Special thanks to `yt-dlp` and `ffmpeg` for their contributions to this tool indirectly.

---

## Features

- Download videos from YouTube and TikTok.
- Supports multiple quality options for YouTube (`best`, `worst`, `audio only`).
- Customizable download directory.
- Simple, user-friendly GUI interface.
  
---

## Requirements

- Python 3.x
- `yt-dlp`, `7-zip`, and `ffmpeg` (automatically downloaded).
- Internet connection for initial downloads and video downloads.

---

## Linux Setup and Installation

1. **Clone the Repository**:
   ```shell
   git clone https://github.com/yourusername/NinjaVideoDownloader.git  
   cd NinjaVideoDownloader  
   ```

2. **Install Python Packages**:
   Ensure that you have `requests` and `tkinter` available for your Python version.
   ```shell
   pip install requests  
   ```

3. **Run the Script**:
   Run the script with Python:
   ```shell
   python ninja_video_downloader.py  
   ```
    OR
   ```shell
   python simple_gui.py
   ```

---
## Windows Setup and Installation

1. **Download the Repository**:
   ```shell
   Download Link: https://github.com/SilentPSLLC/NinjaVideoDownloader/archive/refs/heads/main.zip  
   ```

2. **Install Python**:
    Ensure that you are on the windows machine you wish to install python on.
    ```shell
    Download Link: https://www.python.org/downloads/
    ```

3. **Install Python Packages**:
   Ensure that you have `requests` and `tkinter` available for your Python version. To do this run:
   ```shell
   py -m pip install requests
   ```
   Or Run:
   ```shell
   python -m pip install requests
   ```

3. **Extract the Script**:
   Navigate to the location you saved the NinjaVideoDownloader and unzip it.

4. **Run The Script"
   Run the "simple_gui.py" file by double clicking it to see the Graphical User Interface (GUI) or the "ninja_video_downloader.py  " if you're a Ninjawith the Command-Line Interpreter (CLI). 

---


## Usage

1. **Enter Video URL**: Paste the video URL from YouTube or TikTok into the provided field.
2. **Select Download Directory**: Choose or change the directory where videos will be saved.
3. **Choose Quality**: Select the preferred quality or leave it default (YouTube videos only).
4. **Start Download**: Click the "Start Download" button.

The video will download and, if necessary, merge audio and video components.

---

## Configuration

- Configuration settings are saved in `config.json`, located in the download folder.
- The default download directory is the `Downloads/NinjaVideoDownloader` folder, which can be customized in the application and saved to `config.json`.

---

## Troubleshooting

- **Failed Downloads**: Ensure `yt-dlp` and `ffmpeg` are downloaded successfully. Check internet connectivity if you encounter download issues.
- **Errors During Extraction**: The program uses `7-zip` for extraction. Make sure it downloads correctly to the designated download folder.
- **Updates**: Try updating `yt-dlp` to the latest version if downloads fail, as changes in video platform APIs can affect functionality.

---

## Credits

This project uses the following open-source tools:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - For video downloading.
- [ffmpeg](https://www.gyan.dev/ffmpeg) - For media processing.
- [7-zip](https://7-zip.org/) - For extracting compressed files.
- [Claude.ai 3.7 Sonnet](https://claude.ai/) - For Assisting with Debuging & Rebuilding Code

---

## License
This project is licensed under the GNU General Public License v3.0 - see the LICENSE.txt file for details.
Key License Points:
 - ✅ Free to use, modify, and distribute
 - ✅ Source code must remain open (copyleft)
 - ❌ NO WARRANTY - Software provided "as-is"
 - ❌ NO LIABILITY - Author not responsible for damages
 - ❌ NO SUPPORT - No technical support provided

---

## Contributing
While contributions are welcome, please note:
- No support or responses are guaranteed
- Pull requests may or may not be reviewed
- Issues may not be addressed
- The project is maintained on an "if and when" basis

--
Enjoy downloading with Ninja Video Downloader!
