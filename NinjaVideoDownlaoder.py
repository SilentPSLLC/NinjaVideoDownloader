import os
import json
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import re
from pathlib import Path
import requests
import threading

# Define version, company name, and product name
__version__ = "1.2.0"
__company__ = "Christopher Sparrowgrove"
__product_name__ = "Ninja Video Downloader"
__thank_you_note__ = "Thanks to yt-dlp and ffmpeg."

# Paths and URLs
download_folder = Path.home() / "Downloads" / "NinjaVideoDownloader"
yt_dlp_path = download_folder / "yt-dlp.exe"
seven_zip_exe = download_folder / "7zr.exe"
ffmpeg_archive_path = download_folder / "ffmpeg.7z"
ffmpeg_extracted_folder = download_folder / "ffmpeg"
config_file_path = download_folder / "config.json"

# URLs for required downloads
yt_dlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
seven_zip_url = "https://7-zip.org/a/7zr.exe"
ffmpeg_url = "https://www.gyan.dev/ffmpeg/builds/ffmpeg-git-full.7z"

# Ensure the download directory exists
download_folder.mkdir(parents=True, exist_ok=True)

# Download yt-dlp if it doesn't exist
if not yt_dlp_path.is_file():
    try:
        print("Downloading yt-dlp...")
        response = requests.get(yt_dlp_url, timeout=10)
        response.raise_for_status()
        yt_dlp_path.write_bytes(response.content)
        print("yt-dlp downloaded successfully.")
    except requests.RequestException as e:
        print(f"Failed to download yt-dlp: {e}")
        messagebox.showerror("Error", "Failed to download yt-dlp. Check your network connection.")
        exit(1)

# Download 7zr.exe if it doesn't already exist
if not seven_zip_exe.is_file():
    try:
        print("Downloading 7zr.exe...")
        response = requests.get(seven_zip_url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Save 7zr.exe
        with open(seven_zip_exe, 'wb') as f:
            f.write(response.content)
        print("7zr.exe downloaded successfully.")
    except requests.RequestException as e:
        print(f"Failed to download 7zr.exe: {e}")
        exit(1)

# Download ffmpeg.7z if it doesn't already exist
if not ffmpeg_archive_path.is_file():
    try:
        print("Downloading ffmpeg.7z...")
        response = requests.get(ffmpeg_url, stream=True, timeout=10)
        response.raise_for_status()
        
        # Save ffmpeg archive
        with open(ffmpeg_archive_path, 'wb') as f:
            f.write(response.content)
        print("ffmpeg.7z downloaded successfully.")
    except requests.RequestException as e:
        print(f"Failed to download ffmpeg: {e}")
        exit(1)

# Extract ffmpeg if not already extracted
if not ffmpeg_extracted_folder.is_dir():
    try:
        print("Extracting ffmpeg with 7zr.exe...")
        subprocess.run([str(seven_zip_exe), "x", str(ffmpeg_archive_path), f"-o{download_folder}"], check=True)
        print("Extraction complete.")

        # Locate and rename the extracted folder to 'ffmpeg' if necessary
        extracted_folder = next(download_folder.glob("ffmpeg*"), None)
        if extracted_folder and extracted_folder.is_dir():
            extracted_folder.rename(ffmpeg_extracted_folder)
            print(f"ffmpeg extracted and renamed to {ffmpeg_extracted_folder}")

        # Optionally, remove the archive after extraction
        ffmpeg_archive_path.unlink()

    except subprocess.CalledProcessError as e:
        print(f"7zr extraction failed: {e}")
        exit(1)
    except Exception as e:
        print(f"Unexpected error during extraction and renaming: {e}")
        exit(1)

# Load or create configuration
config = {}
if config_file_path.exists():
    with config_file_path.open('r') as config_file:
        config = json.load(config_file)
else:
    config['DownloadPath'] = str(download_folder)
    config_file_path.write_text(json.dumps(config))

def sanitize_filename(filename):
    return re.sub(r'[<>:"/\\|?*]', '_', filename)

def is_valid_url(url):
    # Extended to support Instagram
    patterns = [
        r'https?://(www\.)?(youtube\.com|youtu\.be)/.+',
        r'https?://(www\.)?tiktok\.com/.+',
        r'https?://(www\.)?instagram\.com/(p|reel|tv)/.+'
    ]
    return any(re.match(pattern, url) for pattern in patterns)

def detect_platform(url):
    if "youtube.com" in url or "youtu.be" in url:
        return "youtube"
    elif "tiktok.com" in url:
        return "tiktok"
    elif "instagram.com" in url:
        return "instagram"
    return "unknown"

# GUI Setup
class VideoDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Ninja Video Downloader v1.2.0")
        master.geometry("550x400")

        # URL Entry
        self.url_label = tk.Label(master, text="Enter Video URL (YouTube, TikTok, Instagram):")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(master, width=60)
        self.url_entry.pack(pady=5)

        # Platform detection display
        self.platform_label = tk.Label(master, text="Platform: Not detected", fg="gray")
        self.platform_label.pack(pady=2)
        
        # Bind URL entry to detect platform
        self.url_entry.bind('<KeyRelease>', self.on_url_change)

        # Download Directory Entry
        self.dir_label = tk.Label(master, text="Download Directory:")
        self.dir_label.pack(pady=10)
        self.path_entry = tk.Entry(master, width=60)
        self.path_entry.pack(pady=5)
        self.path_entry.insert(0, config.get('DownloadPath', str(download_folder)))

        # Browse Button
        self.browse_button = tk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack(pady=5)

        # Quality Options Frame
        self.quality_frame = tk.Frame(master)
        self.quality_frame.pack(pady=10)
        
        self.quality_label = tk.Label(self.quality_frame, text="Quality Options:")
        self.quality_label.pack()
        
        self.quality_var = tk.StringVar(value="best")
        self.quality_options = ttk.Combobox(
            self.quality_frame, 
            textvariable=self.quality_var, 
            values=["best", "worst", "audio only"], 
            state="readonly",
            width=15
        )
        self.quality_options.pack(pady=5)

        # Additional Options Frame
        self.options_frame = tk.Frame(master)
        self.options_frame.pack(pady=5)
        
        # Metadata option
        self.metadata_var = tk.BooleanVar(value=True)
        self.metadata_check = tk.Checkbutton(
            self.options_frame, 
            text="Save metadata (description, thumbnail)", 
            variable=self.metadata_var
        )
        self.metadata_check.pack(side=tk.LEFT, padx=5)

        # Subtitle option
        self.subtitle_var = tk.BooleanVar(value=False)
        self.subtitle_check = tk.Checkbutton(
            self.options_frame, 
            text="Download subtitles", 
            variable=self.subtitle_var
        )
        self.subtitle_check.pack(side=tk.LEFT, padx=5)

        # Download Button
        self.download_button = tk.Button(master, text="Start Download", command=self.start_download_thread)
        self.download_button.pack(pady=15)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(pady=5, fill=tk.X, padx=20)
        
        # Status Label
        self.status_label = tk.Label(master, text="Ready", fg="green")
        self.status_label.pack(pady=5)

    def on_url_change(self, event):
        url = self.url_entry.get().strip()
        if url:
            platform = detect_platform(url)
            if platform != "unknown":
                self.platform_label.config(text=f"Platform: {platform.title()}", fg="blue")
                # Enable/disable quality options based on platform
                if platform == "youtube":
                    self.quality_options.config(state="readonly")
                    self.quality_label.config(text="Quality Options (YouTube):")
                else:
                    self.quality_options.config(state="disabled")
                    self.quality_label.config(text="Quality Options (Not available for this platform):")
            else:
                self.platform_label.config(text="Platform: Unknown/Invalid URL", fg="red")
        else:
            self.platform_label.config(text="Platform: Not detected", fg="gray")

    def browse(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def start_download_thread(self):
        # Run download in separate thread to prevent GUI freezing
        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()

    def update_status(self, message, color="black"):
        self.status_label.config(text=message, fg=color)
        self.master.update_idletasks()

    def download(self):
        url = self.url_entry.get().strip()
        download_path = Path(self.path_entry.get().strip())
        
        # Validate URL
        self.update_status("Validating URL...", "blue")
        if not is_valid_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube, TikTok, or Instagram URL.")
            self.update_status("Invalid URL", "red")
            return

        # Disable download button during download
        self.download_button.config(state="disabled")
        
        # Start Download Process
        self.update_status("Starting download...", "blue")
        self.progress_bar.start()

        platform = detect_platform(url)
        output_template = download_path / "%(title)s.%(ext)s"
        
        # Build yt-dlp arguments based on platform
        yt_dlp_args = [str(yt_dlp_path), url, "-o", str(output_template)]
        
        if platform == "youtube":
            # YouTube-specific options
            format_option = {
                "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "worst": "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst", 
                "audio only": "bestaudio/best"
            }.get(self.quality_var.get(), "best")
            yt_dlp_args.extend(["-f", format_option, "--merge-output-format", "mp4"])
        
        elif platform == "instagram":
            # Instagram-specific options
            yt_dlp_args.extend([
                "--no-playlist",  # Don't download entire albums/stories
                "--write-info-json" if self.metadata_var.get() else "--no-write-info-json"
            ])
        
        elif platform == "tiktok":
            # TikTok-specific options
            yt_dlp_args.extend(["--merge-output-format", "mp4"])

        # Add common options
        if self.metadata_var.get():
            yt_dlp_args.extend(["--write-description", "--write-thumbnail"])
        
        if self.subtitle_var.get():
            yt_dlp_args.extend(["--write-subs", "--write-auto-subs"])
        
        yt_dlp_args.append("--verbose")

        # Add ffmpeg/bin directory to PATH for yt-dlp merging
        ffmpeg_bin_path = ffmpeg_extracted_folder / "bin"
        env = os.environ.copy()
        env["PATH"] += os.pathsep + str(ffmpeg_bin_path)

        try:
            # Create download directory if it doesn't exist
            download_path.mkdir(parents=True, exist_ok=True)
            
            log_file_name = sanitize_filename(url.split("/")[-1]) + ".log"
            log_file_path = download_path / log_file_name
            
            self.update_status("Downloading...", "blue")
            
            with log_file_path.open('w', encoding='utf-8') as log_file:
                process = subprocess.Popen(
                    yt_dlp_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    env=env,
                    encoding='utf-8',
                    errors='replace'
                )

                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                        log_file.write(output)
                        # Update status with download progress if available
                        if "%" in output and "ETA" in output:
                            progress_match = re.search(r'(\d+\.?\d*)%', output)
                            if progress_match:
                                self.update_status(f"Downloading... {progress_match.group(1)}%", "blue")

                returncode = process.wait()
                self.progress_bar.stop()

                if returncode == 0:
                    self.update_status("Download complete!", "green")
                    messagebox.showinfo("Success", "Download complete!")

                    # Update timestamp of downloaded files
                    try:
                        video_files = list(download_path.glob("*.mp4")) + list(download_path.glob("*.webm")) + list(download_path.glob("*.mkv"))
                        if video_files:
                            for file_path in video_files:
                                current_time = time.time()
                                os.utime(file_path, (current_time, current_time))
                    except Exception as e:
                        print(f"Failed to update file timestamps: {e}")

                else:
                    self.update_status("Download failed", "red")
                    messagebox.showerror("Error", f"Download failed with exit code {returncode}. Check the log file for details.")

            # Save the current configuration
            config['DownloadPath'] = str(download_path)
            config_file_path.write_text(json.dumps(config, indent=2))

        except Exception as e:
            self.progress_bar.stop()
            self.update_status("Error occurred", "red")
            print(f"An error occurred during download process: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")
        
        finally:
            # Re-enable download button
            self.download_button.config(state="normal")
            if self.progress_bar.cget("mode") == "indeterminate":
                self.progress_bar.stop()

# Run the application
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VideoDownloader(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Fatal Error", f"An error occurred: {e}")
