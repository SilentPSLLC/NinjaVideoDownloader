# TubeArc Media Archiver v3.1.0 🦊

**Codename: Kitsune** - Clever, adaptable, and always improving

TubeArc is a self-contained video archiver that automatically downloads all required tools (yt-dlp, FFmpeg, 7-Zip) and provides a simple interface for archiving videos from multiple platforms.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Features](#features)
- [Requirements](#requirements)
- [Windows Setup and Installation](#windows-setup-and-installation)
- [Linux Setup and Installation](#linux-setup-and-installation)
- [Usage](#usage)
- [Auto-Update System](#auto-update-system)
- [Configuration](#configuration)
- [Supported Platforms](#supported-platforms)
- [Troubleshooting](#troubleshooting)
- [Evolution History](#evolution-history)
- [Credits](#credits)
- [License](#license)
- [Contributing](#contributing)

---

## Project Overview

- **Version**: 3.1.0
- **Codename**: Kitsune 🦊
- **Author**: SilentPSLLC
- **Product Name**: TubeArc Media Archiver
- **Repository**: https://github.com/SilentPSLLC/TubeArc
- **Previous Name**: Ninja Video Downloader (legacy)

---

## Features

### Core Features
- ✅ **Automatic Tool Management**: Downloads yt-dlp, FFmpeg, and 7-Zip automatically
- ✅ **Self-Updating**: Checks for updates daily and auto-updates via GitHub releases
- ✅ **Multi-Platform Support**: YouTube, TikTok, Instagram, and more
- ✅ **Flexible Download Options**:
  - Combined video + audio (default)
  - Separate video and audio files
  - Audio-only extraction to MP3
- ✅ **Optional Features**:
  - Download metadata and thumbnails
  - Download subtitles (auto-generated and manual)
- ✅ **Persistent Configuration**: Saves your download directory preferences
- ✅ **Platform Detection**: Automatically detects video platform from URL
- ✅ **Professional UI**: Clean, intuitive interface with progress tracking

### Technical Features
- Self-contained dependencies (no manual installations)
- Version caching (checks updates once per day)
- Multi-file update system with automatic restart
- Comprehensive error handling
- FFmpeg integration for audio/video merging
- Tool version checking (yt-dlp auto-updates itself)

---

## Requirements

- **Python**: 3.7 or higher
- **Python Packages**: 
  - `tkinter` (usually included with Python)
  - `requests` (auto-installed or install manually)
- **Internet Connection**: Required for initial setup and downloads
- **Operating System**: Windows 10/11 (primary), Linux (supported)

---

## Windows Setup and Installation

### Quick Start (Recommended)

1. **Download Python**:
   - Visit: https://www.python.org/downloads/
   - Download Python 3.7 or newer
   - ✅ **IMPORTANT**: Check "Add Python to PATH" during installation

2. **Download TubeArc**:
   ```shell
   Download: https://github.com/SilentPSLLC/TubeArc/archive/refs/heads/main.zip
   ```
   
3. **Extract and Install Dependencies**:
   - Unzip the downloaded file
   - Open Command Prompt in the extracted folder
   - Run:
     ```shell
     py -m pip install requests
     ```

4. **Run TubeArc**:
   - Double-click `tubearc.py`
   - Or run in Command Prompt:
     ```shell
     py tubearc.py
     ```

5. **First Launch**:
   - TubeArc will automatically download:
     - yt-dlp (video downloader)
     - FFmpeg (media processor)
     - 7-Zip (archive extractor)
   - Wait for "Ready" status before downloading videos

### Using the Launcher (Alternative)

If you have the `launch_tubearc.bat` file:
- Simply double-click it to start TubeArc
- It automatically finds your Python installation

---

## Linux Setup and Installation

1. **Install Python and Dependencies**:
   ```bash
   sudo apt update
   sudo apt install python3 python3-pip python3-tk
   ```

2. **Clone the Repository**:
   ```bash
   git clone https://github.com/SilentPSLLC/TubeArc.git
   cd TubeArc
   ```

3. **Install Python Packages**:
   ```bash
   pip3 install requests
   ```

4. **Run TubeArc**:
   ```bash
   python3 tubearc.py
   ```

---

## Usage

### Basic Usage

1. **Paste Video URL**: 
   - Copy a video URL from YouTube, TikTok, or Instagram
   - Paste into the URL field
   - Platform will be auto-detected

2. **Choose Archive Directory** (Optional):
   - Default: `TubeArcDownloads` folder in the same directory as the script
   - Click "Browse" to change location
   - Setting is saved automatically

3. **Select Archive Type**:
   - **Video + Audio (Combined)**: Default, best quality merged file
   - **Video only**: Video without audio
   - **Audio only**: Extracts audio as MP3

4. **Optional Features**:
   - ☑ Download metadata & thumbnail
   - ☑ Download subtitles

5. **Start Download**:
   - Click "Archive Video" button
   - Progress bar shows activity
   - Status updates appear at bottom

### Keyboard Shortcuts

- Press `Enter` in URL field to start download immediately

### Menu Options

- **Help → Check for Updates**: Manually check for TubeArc updates
- **Help → About**: View version, credits, and project information

---

## Auto-Update System

TubeArc includes a sophisticated auto-update system:

### How It Works

1. **Automatic Checks**: 
   - Checks GitHub for updates once per day
   - Downloads latest version automatically

2. **Update Process**:
   - Downloads new files (tubearc.py, updater.py, README files)
   - Prompts user to accept update
   - Launches updater to replace old files
   - Restarts TubeArc automatically

3. **Update Components**:
   - **TubeArc**: Updates via GitHub releases
   - **yt-dlp**: Updates itself automatically
   - **FFmpeg**: Downloaded once (stable binary)
   - **7-Zip**: Downloaded once (stable binary)

### Manual Update Check

Use **Help → Check for Updates** to force an immediate check.

---

## Configuration

### Configuration File

Settings are saved in `config.json`:
```json
{
  "download_path": "C:\\path\\to\\TubeArcDownloads"
}
```

### Version Cache

Update checks are cached in `version_cache.json`:
```json
{
  "tubearc_version": "3.1.0",
  "last_check": "2025-02-05T12:00:00"
}
```

### Directory Structure

```
TubeArc/
├── tubearc.py              # Main application
├── updater.py              # Update handler
├── config.json             # User settings
├── version_cache.json      # Update cache
├── bin/                    # Auto-downloaded tools
│   ├── yt-dlp.exe
│   ├── ffmpeg.exe
│   └── 7zr.exe
└── TubeArcDownloads/       # Default download folder
```

---

## Supported Platforms

- ✅ **YouTube** (youtube.com, youtu.be)
- ✅ **TikTok** (tiktok.com)
- ✅ **Instagram** (Reels, Posts, IGTV)
- ℹ️ **Many Others**: Any platform supported by yt-dlp

### Platform Detection

TubeArc automatically detects the platform and displays:
- ✓ YouTube detected (blue)
- ✓ TikTok detected (purple)
- ✓ Instagram detected (orange)
- ⚠ Unknown platform (red) - may still work!

---

## Troubleshooting

### Common Issues

**"requests library not installed"**
```shell
py -m pip install requests
```

**Tools not downloading**
- Check internet connection
- Disable antivirus temporarily
- Check firewall settings

**Download fails**
- Video might be private or age-restricted
- Platform might have changed API
- Try updating yt-dlp: **Help → Check for Updates**

**Button appears as thin red line**
- Window too small - close and reopen
- Old version - update to v3.1.0+

**FFmpeg extraction fails**
- Ensure 7-Zip downloaded correctly
- Check bin folder permissions
- Restart TubeArc

### Error Messages

| Error | Solution |
|-------|----------|
| "Video unavailable" | Video is private or deleted |
| "Age-restricted video" | Cannot download age-restricted content |
| "HTTP Error 404" | Video not found |
| "yt-dlp not available" | Wait for setup to complete |
| "FFmpeg not available" | Wait for FFmpeg extraction |

### Debug Mode

Run from command line to see detailed logs:
```shell
py tubearc.py
```

---

## Evolution History

### Version History

- **v1.0 - Codename: Unicorn 🦄** (The Beginning)
  - Initial concept
  - Basic download functionality
  
- **v2.0 - Codename: Phoenix 🔥** (Rise from the Ashes)
  - Major rebuild
  - Improved UI
  - Better error handling

- **v3.0 - Codename: Kitsune 🦊** (Clever and Adaptable)
  - Auto-download tools system
  - Self-updating capability
  - GitHub integration

- **v3.1.0 - Codename: Kitsune 🦊** (Current)
  - Custom About dialog
  - Enhanced UI labels
  - Improved documentation
  - Comprehensive licensing

### Rebranding

**Ninja Video Downloader** → **TubeArc Media Archiver**
- More professional branding
- Better represents functionality
- Clearer project identity

---

## Credits

This project uses the following open-source tools:

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** - Video downloading engine (Unlicense)
- **[FFmpeg](https://ffmpeg.org/)** - Media processing and conversion (LGPL v2.1+ / GPL v2+)
- **[7-Zip](https://www.7-zip.org/)** - Archive extraction (LGPL v2.1 with unRAR restriction)
- **[Claude.ai (Sonnet 4)](https://claude.ai/)** - Development assistance and debugging

Special thanks to the open-source community for making this project possible.

---

## License

This project is licensed under the **GNU General Public License v3.0** - see the [LICENSE](LICENSE) file for details.

### Key License Points

**TubeArc:**
- ✅ Free to use, modify, and distribute
- ✅ Source code must remain open (copyleft)
- ❌ NO WARRANTY - Software provided "as-is"
- ❌ NO LIABILITY - Author not responsible for damages
- ❌ NO SUPPORT - No guaranteed technical support

**Bundled Tools:**
- yt-dlp: Public Domain (Unlicense)
- FFmpeg: LGPL v2.1+ / GPL v2+
- 7-Zip: LGPL v2.1 with unRAR restriction

See [LICENSE](LICENSE) file for complete licensing information including all component licenses.

---

## Contributing

Contributions are welcome! However, please note:

- ⚠️ No support or responses are guaranteed
- ⚠️ Pull requests may or may not be reviewed
- ⚠️ Issues may not be addressed
- ⚠️ Project is maintained on an "if and when" basis

### How to Contribute

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request
5. Wait patiently (no timeline guaranteed)

### Development Philosophy

Like the Kitsune, TubeArc is clever and adaptable. We prioritize:
- User-friendly design
- Self-contained functionality
- Minimal manual setup
- Robust error handling
- Clean, documented code

---

## Support

### No Guaranteed Support

This is a free, open-source project maintained on a volunteer basis:
- No SLA (Service Level Agreement)
- No guaranteed response time
- No warranty or liability

### Community Support

- Check [Issues](https://github.com/SilentPSLLC/TubeArc/issues) for similar problems
- Search documentation thoroughly
- Try troubleshooting steps first

### Reporting Bugs

If you encounter a bug:
1. Check if it's already reported in Issues
2. Gather error messages and steps to reproduce
3. Create a detailed issue report
4. Be patient - responses not guaranteed

---

## Philosophical Quote

> *"The belief in the Mandela Effect doesn't reveal a broken universe; it reveals how repetition shapes memory and how confidence in one's mind becomes exploitable."*

---

**Enjoy archiving with TubeArc! 🦊✨**

*Like the mythical Kitsune fox, this archiver is clever, adaptable, and always improving.*
