"""
TubeArc Media Archiver v3.0.1
Codename: Kitsune 🦊

A self-contained video archiver that automatically downloads all required tools
(yt-dlp, 7-Zip, FFmpeg) and provides a simple interface for archiving videos
from multiple platforms.

Evolution:
    v1.0 - Codename: Unicorn - The beginning
    v2.0 - Codename: Phoenix - Rise from the ashes
    v3.0 - Codename: Kitsune - Clever and adaptable

Features:
- Automatic tool downloads (yt-dlp, 7-Zip, FFmpeg)
- Self-updating capability
- Multi-platform support (YouTube, TikTok, Instagram)
- Download video, audio, or both separately
- Merged video+audio option (default)
- Optional metadata and subtitle downloads
- Persistent configuration

Author: Your Name
License: MIT
"""

import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import subprocess
import threading
from pathlib import Path
import re
import json
import shutil
import sys
from datetime import datetime, timedelta

# Try to import requests, handle if not available
try:
    import requests
    REQUESTS_AVAILABLE = True
except ImportError:
    REQUESTS_AVAILABLE = False

# ============================================================================
# VERSION & UPDATE CONFIGURATION
# Kitsune keeps itself sharp and up-to-date
# ============================================================================

TUBEARC_VERSION = "3.0.1"
TUBEARC_CODENAME = "Kitsune"

# GitHub repository for updates
GITHUB_REPO_OWNER = "SilentPSLLC"
GITHUB_REPO_NAME = "NinjaVideoDownloader"
GITHUB_RAW_URL = f"https://raw.githubusercontent.com/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/main"
GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/releases/latest"

# ============================================================================
# CONFIGURATION & CONSTANTS
# Project Kitsune - Like the mythical fox, adaptable and clever
# ============================================================================

# Define application directories and paths
SCRIPT_DIR = Path(__file__).parent.resolve()
BIN_DIR = SCRIPT_DIR / "bin"
DOWNLOAD_FOLDER = SCRIPT_DIR / "TubeArcDownloads"
CONFIG_PATH = SCRIPT_DIR / "config.json"
VERSION_CACHE_PATH = SCRIPT_DIR / "version_cache.json"

# Tool paths
YT_DLP_PATH = BIN_DIR / "yt-dlp.exe"
SEVEN_ZIP_PATH = BIN_DIR / "7zr.exe"
FFMPEG_PATH = BIN_DIR / "ffmpeg.exe"
FFMPEG_ARCHIVE = BIN_DIR / "ffmpeg-git-full.7z"

# Download URLs
YT_DLP_URL = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
SEVEN_ZIP_URL = "https://7-zip.org/a/7zr.exe"

# FFmpeg URLs - Primary and fallback
FFMPEG_URLS = [
    "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z",
    "https://github.com/GyanD/codexffmpeg/releases/download/7.1/ffmpeg-7.1-full_build.7z",
]

# Platform detection patterns
PLATFORM_PATTERNS = {
    "youtube": r'https?://(www\.)?(youtube\.com|youtu\.be)',
    "tiktok": r'https?://(www\.)?tiktok\.com',
    "instagram": r'https?://(www\.)?instagram\.com/(p|reel|tv)'
}

# Platform UI configuration
PLATFORM_CONFIG = {
    "youtube": {"label": "✓ YouTube detected", "color": "blue"},
    "tiktok": {"label": "✓ TikTok detected", "color": "purple"},
    "instagram": {"label": "✓ Instagram detected", "color": "orange"},
    "unknown": {"label": "⚠ Unknown platform", "color": "red"}
}


# ============================================================================
# MAIN APPLICATION CLASS
# Kitsune's clever interface for media archiving
# ============================================================================

class TubeArcArchiver:
    """
    Main application class for TubeArc Media Archiver.
    
    Like the Kitsune, this archiver is clever, adaptable, and efficient.
    Manages the GUI interface, configuration, tool downloads, and video archiving.
    """
    
    def __init__(self, root):
        """
        Initialize the application.
        
        Args:
            root: The tkinter root window
        """
        self.root = root
        self._configure_window()
        self._ensure_directories()
        self.config = self._load_config()
        self._build_ui()
        self._initialize_tools()
    
    # ------------------------------------------------------------------------
    # INITIALIZATION METHODS
    # ------------------------------------------------------------------------
    
    def _configure_window(self):
        """Configure the main application window properties."""
        self.root.title(f"TubeArc Media Archiver v{TUBEARC_VERSION} ({TUBEARC_CODENAME})")
        self.root.geometry("600x380")
        self.root.resizable(True, False)
        self.root.minsize(500, 380)
    
    def _ensure_directories(self):
        """Create necessary application directories if they don't exist."""
        BIN_DIR.mkdir(parents=True, exist_ok=True)
        DOWNLOAD_FOLDER.mkdir(parents=True, exist_ok=True)
    
    def _load_config(self):
        """
        Load application configuration from JSON file.
        
        Returns:
            dict: Configuration dictionary with default values if file doesn't exist
        """
        default_config = {'download_path': str(DOWNLOAD_FOLDER)}
        
        if not CONFIG_PATH.exists():
            return default_config
        
        try:
            with CONFIG_PATH.open('r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Config load error: {e}")
            return default_config
    
    def _save_config(self):
        """Save current configuration to JSON file."""
        try:
            with CONFIG_PATH.open('w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Config save error: {e}")
    
    # ------------------------------------------------------------------------
    # UI CONSTRUCTION
    # Kitsune's beautiful interface
    # ------------------------------------------------------------------------
    
    def _build_ui(self):
        """Construct the complete user interface."""
        # Create menu bar
        self._create_menu_bar()
        
        main_frame = tk.Frame(self.root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        self._create_header(main_frame)
        self._create_url_section(main_frame)
        self._create_directory_section(main_frame)
        self._create_options_section(main_frame)
        self._create_download_button(main_frame)
        self._create_progress_section(main_frame)
        self._create_footer(main_frame)
    
    def _create_menu_bar(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="Check for Updates", command=self._manual_update_check)
        help_menu.add_separator()
        help_menu.add_command(label=f"About TubeArc v{TUBEARC_VERSION}", command=self._show_about)
    
    def _manual_update_check(self):
        """Manually check for updates (triggered from menu)."""
        self._update_status("Checking for updates...", "blue")
        threading.Thread(target=self._force_update_check, daemon=True).start()
    
    def _force_update_check(self):
        """Force an update check regardless of cache."""
        if not REQUESTS_AVAILABLE:
            self.root.after(0, lambda: messagebox.showerror(
                "Error", "requests library not installed"))
            return
        
        self._check_tubearc_update()
        self._check_ytdlp_version()
        self.root.after(0, lambda: self._update_status("Update check complete", "green"))
        self.root.after(2000, lambda: self._update_status("Ready", "green"))
    
    def _show_about(self):
        """Show about dialog."""
        messagebox.showinfo(
            f"About TubeArc",
            f"TubeArc Media Archiver\n"
            f"Version: {TUBEARC_VERSION}\n"
            f"Codename: {TUBEARC_CODENAME} 🦊\n\n"
            f"A clever video archiver for YouTube, TikTok, and Instagram.\n\n"
            f"Powered by:\n"
            f"• yt-dlp\n"
            f"• FFmpeg\n"
            f"• 7-Zip\n\n"
            f"Like the mythical Kitsune fox, this archiver is\n"
            f"clever, adaptable, and always learning."
        )
    
    def _create_header(self, parent):
        """Create the application title header."""
        tk.Label(parent, text="TubeArc Media Archiver", 
                font=("Arial", 16, "bold"), fg="#FF6B35").pack(pady=(0, 5))
        tk.Label(parent, text=f"v{TUBEARC_VERSION} • {TUBEARC_CODENAME} 🦊", 
                font=("Arial", 9), fg="gray").pack(pady=(0, 10))
    
    def _create_url_section(self, parent):
        """Create the URL input section with platform detection."""
        url_frame = tk.Frame(parent)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(url_frame, text="Video URL (YouTube, TikTok, Instagram):", 
                font=("Arial", 10)).pack(anchor=tk.W)
        
        self.url_entry = tk.Entry(url_frame, font=("Arial", 10))
        self.url_entry.pack(fill=tk.X, pady=(5, 0))
        self.url_entry.bind('<Return>', lambda e: self._start_download())
        self.url_entry.bind('<KeyRelease>', self._detect_platform)
        
        # Platform detection label
        self.platform_label = tk.Label(parent, text="", font=("Arial", 9), fg="gray")
        self.platform_label.pack(pady=(0, 5))
    
    def _create_directory_section(self, parent):
        """Create the download directory selection section."""
        dir_frame = tk.Frame(parent)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(dir_frame, text="Archive Directory:", 
                font=("Arial", 10)).pack(anchor=tk.W)
        
        input_frame = tk.Frame(dir_frame)
        input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.dir_entry = tk.Entry(input_frame, font=("Arial", 9))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dir_entry.insert(0, self.config.get('download_path', str(DOWNLOAD_FOLDER)))
        
        tk.Button(input_frame, text="Browse", 
                 command=self._browse_directory).pack(side=tk.RIGHT, padx=(5, 0))
    
    def _create_options_section(self, parent):
        """Create the download options section."""
        options_frame = tk.Frame(parent)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Left column - Download type
        left_col = tk.Frame(options_frame)
        left_col.pack(side=tk.LEFT, padx=(0, 30))
        
        tk.Label(left_col, text="Archive Type:", 
                font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.combined_var = tk.BooleanVar(value=True)
        tk.Checkbutton(left_col, text="Video + Audio (Combined)",
                      variable=self.combined_var, font=("Arial", 9),
                      command=self._toggle_separate_options).pack(anchor=tk.W)
        
        # Separate download options (disabled by default)
        separate_frame = tk.Frame(left_col)
        separate_frame.pack(anchor=tk.W, padx=(20, 0))
        
        self.video_only_var = tk.BooleanVar(value=False)
        self.video_only_check = tk.Checkbutton(separate_frame, text="Video only",
                                               variable=self.video_only_var, 
                                               font=("Arial", 9),
                                               state="disabled")
        self.video_only_check.pack(anchor=tk.W)
        
        self.audio_only_var = tk.BooleanVar(value=False)
        self.audio_only_check = tk.Checkbutton(separate_frame, text="Audio only",
                                               variable=self.audio_only_var, 
                                               font=("Arial", 9),
                                               state="disabled")
        self.audio_only_check.pack(anchor=tk.W)
        
        # Right column - Additional options
        right_col = tk.Frame(options_frame)
        right_col.pack(side=tk.LEFT)
        
        tk.Label(right_col, text="Additional Options:", 
                font=("Arial", 9, "bold")).pack(anchor=tk.W)
        
        self.metadata_var = tk.BooleanVar(value=False)
        tk.Checkbutton(right_col, text="Download metadata & thumbnail",
                      variable=self.metadata_var, font=("Arial", 9)).pack(anchor=tk.W)
        
        self.subtitle_var = tk.BooleanVar(value=False)
        tk.Checkbutton(right_col, text="Download subtitles",
                      variable=self.subtitle_var, font=("Arial", 9)).pack(anchor=tk.W)
    
    def _toggle_separate_options(self):
        """Enable/disable separate download options based on combined checkbox."""
        if self.combined_var.get():
            # Combined is checked - disable separate options
            self.video_only_check.config(state="disabled")
            self.audio_only_check.config(state="disabled")
            self.video_only_var.set(False)
            self.audio_only_var.set(False)
        else:
            # Combined is unchecked - enable separate options
            self.video_only_check.config(state="normal")
            self.audio_only_check.config(state="normal")
    
    def _create_download_button(self, parent):
        """Create the main download button."""
        self.download_btn = tk.Button(parent, text="Archive Video", 
                                     command=self._start_download, 
                                     font=("Arial", 12, "bold"),
                                     bg="#FF6B35", fg="white",
                                     height=2, cursor="hand2")
        self.download_btn.pack(fill=tk.X, pady=(10, 10))
    
    def _create_progress_section(self, parent):
        """Create the progress bar and status label."""
        self.progress = ttk.Progressbar(parent, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        self.status_label = tk.Label(parent, text="Initializing...", 
                                    font=("Arial", 9), fg="orange")
        self.status_label.pack()
    
    def _create_footer(self, parent):
        """Create the footer with attribution information."""
        footer = tk.Frame(parent)
        footer.pack(pady=(10, 0))
        
        tk.Label(footer, text="Supports YouTube, TikTok, Instagram", 
                font=("Arial", 8), fg="gray").pack()
        tk.Label(footer, text="Powered by yt-dlp + FFmpeg", 
                font=("Arial", 8), fg="gray").pack()
    
    # ------------------------------------------------------------------------
    # PLATFORM DETECTION
    # Kitsune's keen senses identify the source
    # ------------------------------------------------------------------------
    
    def _detect_platform(self, event=None):
        """
        Detect video platform from URL and update UI accordingly.
        """
        url = self.url_entry.get().strip()
        
        if not url:
            self.platform_label.config(text="")
            return
        
        platform = self._get_platform(url)
        config = PLATFORM_CONFIG[platform]
        
        self.platform_label.config(text=config["label"], fg=config["color"])
    
    def _get_platform(self, url):
        """
        Identify the video platform from a URL.
        
        Args:
            url: The video URL to analyze
            
        Returns:
            str: Platform identifier ('youtube', 'tiktok', 'instagram', or 'unknown')
        """
        for platform, pattern in PLATFORM_PATTERNS.items():
            if re.match(pattern, url):
                return platform
        return "unknown"
    
    # ------------------------------------------------------------------------
    # TOOL MANAGEMENT
    # Kitsune gathers its tools
    # ------------------------------------------------------------------------
    
    def _initialize_tools(self):
        """Check for required tools and download if necessary."""
        self._update_status("Checking for updates...", "orange")
        threading.Thread(target=self._check_updates_and_tools, daemon=True).start()
    
    def _check_updates_and_tools(self):
        """Check for updates to TubeArc and tools, then download if necessary."""
        if not REQUESTS_AVAILABLE:
            self.root.after(0, lambda: self._update_status(
                "Error: requests library not installed", "red"))
            self.root.after(0, lambda: messagebox.showerror(
                "Missing Library",
                "The 'requests' library is required.\n\n"
                "Please run: pip install requests"))
            return
        
        # Check if we should check for updates (once per day)
        should_check = self._should_check_for_updates()
        
        if should_check:
            # Check for TubeArc updates
            self._check_tubearc_update()
            
            # Check for tool updates
            self._check_tool_updates()
        
        # Download tools if missing
        self._download_all_tools()
    
    def _should_check_for_updates(self):
        """Determine if we should check for updates (once per day)."""
        if not VERSION_CACHE_PATH.exists():
            return True
        
        try:
            with VERSION_CACHE_PATH.open('r') as f:
                cache = json.load(f)
            
            last_check = datetime.fromisoformat(cache.get('last_check', '2000-01-01'))
            return (datetime.now() - last_check) > timedelta(days=1)
        except:
            return True
    
    def _update_version_cache(self, data):
        """Update the version cache file."""
        try:
            cache = {}
            if VERSION_CACHE_PATH.exists():
                with VERSION_CACHE_PATH.open('r') as f:
                    cache = json.load(f)
            
            cache.update(data)
            cache['last_check'] = datetime.now().isoformat()
            
            with VERSION_CACHE_PATH.open('w') as f:
                json.dump(cache, f, indent=2)
        except Exception as e:
            print(f"Failed to update version cache: {e}")
    
    def _check_tubearc_update(self):
        """Check if a new version of TubeArc is available on GitHub."""
        try:
            self.root.after(0, lambda: self._update_status(
                "Checking for TubeArc updates...", "blue"))
            
            print(f"Checking for updates... Current version: {TUBEARC_VERSION}")
            
            # Try to get latest release from GitHub
            response = requests.get(GITHUB_API_URL, timeout=10)
            
            if response.status_code == 200:
                release = response.json()
                latest_version = release['tag_name'].lstrip('v')
                
                print(f"Latest version on GitHub: {latest_version}")
                
                if self._is_newer_version(latest_version, TUBEARC_VERSION):
                    self.root.after(0, lambda: self._prompt_tubearc_update(latest_version, release))
                else:
                    print("TubeArc is up to date!")
                
                self._update_version_cache({'tubearc_version': latest_version})
            else:
                print(f"Could not check for updates (HTTP {response.status_code})")
                
        except Exception as e:
            print(f"Update check failed: {e}")
    
    def _is_newer_version(self, latest, current):
        """Compare version strings (e.g., '3.1.0' > '3.0.0')."""
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]
            return latest_parts > current_parts
        except:
            return False
    
    def _prompt_tubearc_update(self, new_version, release_info):
        """Prompt user to update TubeArc."""
        release_notes = release_info.get('body', 'No release notes available.')
        
        response = messagebox.askyesno(
            "Update Available! 🦊",
            f"TubeArc v{new_version} is available!\n"
            f"Current version: v{TUBEARC_VERSION}\n\n"
            f"Release Notes:\n{release_notes[:200]}...\n\n"
            f"Would you like to download the update?",
            icon='info'
        )
        
        if response:
            self._download_tubearc_update(release_info)
    
    def _download_tubearc_update(self, release_info):
        """Download the latest TubeArc script from GitHub."""
        try:
            self._update_status("Downloading TubeArc update...", "blue")
            
            # Get the download URL for tubearc.py
            script_url = f"{GITHUB_RAW_URL}/tubearc.py"
            
            response = requests.get(script_url, timeout=30)
            response.raise_for_status()
            
            # Save as tubearc_new.py
            new_script = SCRIPT_DIR / "tubearc_new.py"
            new_script.write_text(response.text, encoding='utf-8')
            
            messagebox.showinfo(
                "Update Downloaded! 🦊",
                "TubeArc has been updated!\n\n"
                "The new version is saved as 'tubearc_new.py'\n\n"
                "To complete the update:\n"
                "1. Close TubeArc\n"
                "2. Delete or rename the old 'tubearc.py'\n"
                "3. Rename 'tubearc_new.py' to 'tubearc.py'\n"
                "4. Restart TubeArc\n\n"
                "Or simply replace tubearc.py with tubearc_new.py"
            )
            
        except Exception as e:
            messagebox.showerror(
                "Update Failed",
                f"Failed to download update:\n{e}"
            )
    
    def _check_tool_updates(self):
        """Check if tools (yt-dlp, ffmpeg) need updates."""
        try:
            # Check yt-dlp version
            if YT_DLP_PATH.exists():
                self._check_ytdlp_version()
        except Exception as e:
            print(f"Tool update check failed: {e}")
    
    def _check_ytdlp_version(self):
        """Check if yt-dlp needs an update."""
        try:
            result = subprocess.run(
                [str(YT_DLP_PATH), "--version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                current_version = result.stdout.strip()
                print(f"Current yt-dlp version: {current_version}")
                
                # yt-dlp can update itself
                self.root.after(0, lambda: self._update_status(
                    "Checking yt-dlp for updates...", "blue"))
                
                update_result = subprocess.run(
                    [str(YT_DLP_PATH), "-U"],
                    capture_output=True,
                    text=True,
                    timeout=30
                )
                
                if "Updated" in update_result.stdout or "updated" in update_result.stdout:
                    print("yt-dlp was updated!")
                elif "up to date" in update_result.stdout.lower():
                    print("yt-dlp is already up to date")
                    
        except Exception as e:
            print(f"Failed to check yt-dlp version: {e}")
    
    def _download_all_tools(self):
        """Download all required tools in sequence."""
        if not REQUESTS_AVAILABLE:
            self.root.after(0, lambda: self._update_status(
                "Error: requests library not installed", "red"))
            self.root.after(0, lambda: messagebox.showerror(
                "Missing Library",
                "The 'requests' library is required.\n\n"
                "Please run: pip install requests"))
            return
        
        try:
            # Step 1: Download yt-dlp
            if not YT_DLP_PATH.exists():
                self.root.after(0, lambda: self._update_status(
                    "Downloading yt-dlp...", "blue"))
                self._download_file(YT_DLP_URL, YT_DLP_PATH)
            
            # Step 2: Download 7-Zip
            if not SEVEN_ZIP_PATH.exists():
                self.root.after(0, lambda: self._update_status(
                    "Downloading 7-Zip...", "blue"))
                self._download_file(SEVEN_ZIP_URL, SEVEN_ZIP_PATH)
            
            # Step 3: Download and extract FFmpeg
            if not FFMPEG_PATH.exists():
                self.root.after(0, lambda: self._update_status(
                    "Downloading FFmpeg (large file, may take a minute)...", "blue"))
                
                # Download FFmpeg archive - try multiple URLs
                if not FFMPEG_ARCHIVE.exists():
                    ffmpeg_downloaded = False
                    for i, url in enumerate(FFMPEG_URLS, 1):
                        try:
                            self.root.after(0, lambda u=url: self._update_status(
                                f"Trying FFmpeg download {i}/{len(FFMPEG_URLS)}...", "blue"))
                            print(f"\nAttempting FFmpeg download from URL {i}/{len(FFMPEG_URLS)}")
                            self._download_file(url, FFMPEG_ARCHIVE)
                            
                            # Verify download
                            if FFMPEG_ARCHIVE.exists() and FFMPEG_ARCHIVE.stat().st_size > 0:
                                print(f"✓ FFmpeg downloaded successfully from URL {i}")
                                ffmpeg_downloaded = True
                                break
                            else:
                                print(f"✗ Download from URL {i} resulted in 0 bytes")
                                if FFMPEG_ARCHIVE.exists():
                                    FFMPEG_ARCHIVE.unlink()
                        except Exception as e:
                            print(f"✗ Failed to download from URL {i}: {e}")
                            if FFMPEG_ARCHIVE.exists():
                                FFMPEG_ARCHIVE.unlink()
                            continue
                    
                    if not ffmpeg_downloaded:
                        raise Exception("Failed to download FFmpeg from all available sources!")
                
                # Extract FFmpeg using 7-Zip
                self.root.after(0, lambda: self._update_status(
                    "Extracting FFmpeg...", "blue"))
                self._extract_ffmpeg()
                
                # Wait a moment for file system to sync
                import time
                time.sleep(1)
            
            # All tools ready - Kitsune is prepared
            self.root.after(0, lambda: self._update_status("Ready", "green"))
            
        except Exception as e:
            self.root.after(0, lambda: self._update_status(
                "Setup failed", "red"))
            self.root.after(0, lambda: messagebox.showerror(
                "Setup Error",
                f"Failed to download required tools:\n\n{e}\n\n"
                "Please check your internet connection."))
    
    def _download_file(self, url, destination):
        """
        Download a file from a URL to a destination path.
        
        Args:
            url: URL to download from
            destination: Path to save the file
        """
        print(f"Downloading from: {url}")
        print(f"Saving to: {destination}")
        
        try:
            # Get file size first
            response = requests.head(url, timeout=30, allow_redirects=True)
            total_size = int(response.headers.get('content-length', 0))
            print(f"File size: {total_size / (1024*1024):.2f} MB")
            
            # Download with streaming
            response = requests.get(url, timeout=300, stream=True, allow_redirects=True)
            response.raise_for_status()
            
            downloaded = 0
            with destination.open('wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        # Print progress every 10MB
                        if downloaded % (10 * 1024 * 1024) < 8192:
                            progress = (downloaded / total_size * 100) if total_size > 0 else 0
                            print(f"Progress: {downloaded / (1024*1024):.1f} MB / {total_size / (1024*1024):.1f} MB ({progress:.1f}%)")
            
            final_size = destination.stat().st_size
            print(f"Download complete! Final size: {final_size / (1024*1024):.2f} MB")
            
            if final_size == 0:
                raise Exception("Downloaded file is 0 bytes!")
                
        except Exception as e:
            print(f"Download error: {e}")
            # Clean up partial download
            if destination.exists():
                destination.unlink()
            raise Exception(f"Failed to download {url}: {e}")
    
    def _extract_ffmpeg(self):
        """Extract FFmpeg from the downloaded archive using 7-Zip."""
        try:
            print(f"Extracting FFmpeg archive: {FFMPEG_ARCHIVE}")
            print(f"Archive size: {FFMPEG_ARCHIVE.stat().st_size / (1024*1024):.2f} MB")
            
            # Verify 7-Zip exists
            if not SEVEN_ZIP_PATH.exists():
                raise Exception("7-Zip not found! Cannot extract FFmpeg.")
            
            # Verify archive exists and is not empty
            if not FFMPEG_ARCHIVE.exists():
                raise Exception("FFmpeg archive does not exist!")
            
            if FFMPEG_ARCHIVE.stat().st_size == 0:
                raise Exception("FFmpeg archive is 0 bytes! Download failed.")
            
            print("Running 7-Zip extraction...")
            
            # Extract the archive
            result = subprocess.run([
                str(SEVEN_ZIP_PATH), "x",
                str(FFMPEG_ARCHIVE),
                f"-o{BIN_DIR}",
                "-y"  # Overwrite without prompt
            ], check=True, capture_output=True, text=True)
            
            print("7-Zip output:", result.stdout)
            if result.stderr:
                print("7-Zip errors:", result.stderr)
            
            print("Searching for ffmpeg.exe in extracted files...")
            
            # Find the ffmpeg.exe in the extracted folder
            found = False
            for item in BIN_DIR.rglob("ffmpeg.exe"):
                print(f"Found ffmpeg.exe at: {item}")
                # Move it to the bin directory
                if item != FFMPEG_PATH:
                    shutil.move(str(item), str(FFMPEG_PATH))
                    print(f"Moved to: {FFMPEG_PATH}")
                found = True
                break
            
            if not found:
                raise Exception("Could not find ffmpeg.exe in extracted archive!")
            
            # Verify ffmpeg was extracted successfully
            if not FFMPEG_PATH.exists():
                raise Exception("FFmpeg extraction failed - ffmpeg.exe not found!")
            
            print(f"FFmpeg ready at: {FFMPEG_PATH}")
            print(f"FFmpeg size: {FFMPEG_PATH.stat().st_size / (1024*1024):.2f} MB")
            
            # Clean up: remove the archive and extracted folder
            print("Cleaning up temporary files...")
            if FFMPEG_ARCHIVE.exists():
                FFMPEG_ARCHIVE.unlink()
                print("Removed archive")
            
            # Remove extracted directory
            for item in BIN_DIR.iterdir():
                if item.is_dir() and item.name.startswith("ffmpeg"):
                    print(f"Removing extracted folder: {item}")
                    shutil.rmtree(item)
            
            print("FFmpeg extraction complete!")
                    
        except subprocess.CalledProcessError as e:
            error_msg = f"7-Zip extraction failed: {e}\nStdout: {e.stdout}\nStderr: {e.stderr}"
            print(error_msg)
            raise Exception(error_msg)
        except Exception as e:
            print(f"FFmpeg extraction error: {e}")
            raise Exception(f"Failed to extract FFmpeg: {e}")
    
    # ------------------------------------------------------------------------
    # USER INTERACTIONS
    # ------------------------------------------------------------------------
    
    def _browse_directory(self):
        """Open directory browser dialog to select download location."""
        folder = filedialog.askdirectory(initialdir=self.dir_entry.get())
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)
    
    def _update_status(self, message, color="black"):
        """
        Update the status label text and color.
        
        Args:
            message: Status message to display
            color: Text color (e.g., 'green', 'red', 'blue')
        """
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    # ------------------------------------------------------------------------
    # DOWNLOAD PROCESS
    # Kitsune's archiving magic
    # ------------------------------------------------------------------------
    
    def _start_download(self):
        """Launch the download process in a separate thread."""
        threading.Thread(target=self._download, daemon=True).start()
    
    def _download(self):
        """
        Main download function that handles the entire archiving workflow.
        """
        url = self.url_entry.get().strip()
        download_path = Path(self.dir_entry.get().strip())
        
        # Validate inputs
        if not self._validate_inputs(url):
            return
        
        # Save configuration
        self.config['download_path'] = str(download_path)
        self._save_config()
        
        # Prepare UI for download
        self._set_downloading_state(True)
        
        try:
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Build and execute download command
            cmd = self._build_download_command(url, download_path)
            
            # Debug: Print the command
            print("Executing command:", ' '.join(cmd))
            
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            # Handle result
            if result.returncode == 0:
                self._handle_success(download_path)
            else:
                self._handle_error(result.stderr or result.stdout)
                
        except subprocess.TimeoutExpired:
            self._update_status("Archive timed out", "red")
            messagebox.showerror("Timeout", "Archiving took too long and was cancelled.")
        except Exception as e:
            self._update_status("Error occurred", "red")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        finally:
            self._set_downloading_state(False)
    
    def _validate_inputs(self, url):
        """
        Validate user inputs before starting download.
        
        Args:
            url: The video URL to validate
            
        Returns:
            bool: True if inputs are valid, False otherwise
        """
        if not url:
            messagebox.showwarning("No URL", "Please enter a video URL")
            return False
        
        if not re.match(r'https?://', url):
            messagebox.showerror("Invalid URL", "Please enter a valid HTTP/HTTPS URL")
            return False
        
        if not YT_DLP_PATH.exists():
            messagebox.showerror("Error", "yt-dlp not available. Please wait for setup to complete.")
            return False
        
        if not FFMPEG_PATH.exists() and self.combined_var.get():
            messagebox.showerror("Error", "FFmpeg not available. Please wait for setup to complete.")
            return False
        
        # Validate separate download options
        if not self.combined_var.get():
            if not self.video_only_var.get() and not self.audio_only_var.get():
                messagebox.showwarning("No Selection", 
                    "Please check 'Video only' and/or 'Audio only', or enable 'Video + Audio (Combined)'")
                return False
        
        return True
    
    def _build_download_command(self, url, download_path):
        """
        Build the yt-dlp command with appropriate flags and options.
        
        Args:
            url: Video URL to download
            download_path: Directory to save downloaded files
            
        Returns:
            list: Command arguments for subprocess
        """
        platform = self._get_platform(url)
        
        # Build proper output template
        output_template = str(download_path / "%(title)s.%(ext)s")
        
        # Base command
        cmd = [str(YT_DLP_PATH), url, "-o", output_template]
        
        # Set FFmpeg location
        cmd.extend(["--ffmpeg-location", str(FFMPEG_PATH)])
        
        # Download type selection
        if self.combined_var.get():
            # Combined video + audio - Kitsune merges them cleverly
            cmd.extend(["-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/bestvideo+bestaudio/best"])
            cmd.extend(["--merge-output-format", "mp4"])
            # Ensure audio codec is copied properly
            cmd.extend(["--postprocessor-args", "ffmpeg:-c:v copy -c:a aac"])
        else:
            # Separate downloads
            if self.video_only_var.get() and self.audio_only_var.get():
                # Download both separately
                cmd.extend(["-f", "bestvideo[ext=mp4],bestaudio[ext=m4a]"])
                cmd.append("--keep-video")
            elif self.video_only_var.get():
                # Video only
                cmd.extend(["-f", "bestvideo[ext=mp4]/bestvideo"])
            elif self.audio_only_var.get():
                # Audio only - extract to mp3
                cmd.extend(["-f", "bestaudio/best"])
                cmd.extend(["-x", "--audio-format", "mp3"])
        
        # Optional features
        if self.metadata_var.get():
            cmd.extend(["--write-description", "--write-thumbnail"])
        
        if self.subtitle_var.get():
            cmd.extend(["--write-subs", "--write-auto-subs", "--sub-format", "srt"])
        
        # Common options
        cmd.extend(["--no-playlist"])
        
        return cmd
    
    def _set_downloading_state(self, is_downloading):
        """
        Toggle UI state between downloading and ready.
        
        Args:
            is_downloading: True to disable UI, False to enable
        """
        if is_downloading:
            self.download_btn.config(state="disabled", text="Archiving...")
            self.progress.start()
            self._update_status("Archiving...", "blue")
        else:
            self.download_btn.config(state="normal", text="Archive Video")
            self.progress.stop()
    
    def _handle_success(self, download_path):
        """Handle successful download completion."""
        self._update_status("Archive completed!", "green")
        messagebox.showinfo("Success", 
            f"Video archived successfully!\n\nSaved to:\n{download_path}")
    
    def _handle_error(self, error_msg):
        """
        Handle download errors with user-friendly messages.
        
        Args:
            error_msg: Error message from yt-dlp
        """
        self._update_status("Archive failed", "red")
        
        # Map common errors to user-friendly messages
        error_patterns = {
            "This video is unavailable": "This video is unavailable or private.",
            "Video unavailable": "Video is not available for download.",
            "Sign in to confirm your age": "Age-restricted video. Cannot download.",
            "HTTP Error 404": "Video not found (404 error).",
            "Private video": "This is a private video."
        }
        
        for pattern, message in error_patterns.items():
            if pattern in error_msg:
                messagebox.showerror("Archive Failed", message)
                return
        
        # Generic error message
        messagebox.showerror("Archive Failed", 
            f"Failed to archive video.\n\nError details:\n{error_msg[:300]}...")


# ============================================================================
# APPLICATION ENTRY POINT
# Kitsune awakens
# ============================================================================

def main():
    """Initialize and run the application."""
    try:
        root = tk.Tk()
        app = TubeArcArchiver(root)
        
        # Center window on screen
        root.update_idletasks()
        x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
        y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
        root.geometry(f"+{x}+{y}")
        
        root.mainloop()
    except Exception as e:
        # Show error in a message box if GUI fails to start
        error_root = tk.Tk()
        error_root.withdraw()
        messagebox.showerror("Startup Error", 
            f"Failed to start TubeArc Media Archiver:\n\n{str(e)}\n\n"
            f"Please ensure you have Python and required libraries installed.")
        error_root.destroy()


if __name__ == "__main__":
    main()
