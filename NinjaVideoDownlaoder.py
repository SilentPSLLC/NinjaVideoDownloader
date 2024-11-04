import os
import json
import subprocess
import time
import tkinter as tk
from tkinter import messagebox, filedialog, ttk
import re
from pathlib import Path
import requests

# Define version, company name, and product name
__version__ = "1.1.2"
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
    return re.match(r'https?://(www\.)?(youtube\.com|youtu\.be|tiktok\.com)/.+', url)

# GUI Setup
class VideoDownloader:
    def __init__(self, master):
        self.master = master
        master.title("Ninja Video Downloader")
        master.geometry("500x350")

        # URL Entry
        self.url_label = tk.Label(master, text="Enter Video URL:")
        self.url_label.pack(pady=10)
        self.url_entry = tk.Entry(master, width=60)
        self.url_entry.pack(pady=5)

        # Download Directory Entry
        self.dir_label = tk.Label(master, text="Specific Download Directory:")
        self.dir_label.pack(pady=10)
        self.path_entry = tk.Entry(master, width=60)
        self.path_entry.pack(pady=5)
        self.path_entry.insert(0, config.get('DownloadPath', str(download_folder)))

        # Browse Button
        self.browse_button = tk.Button(master, text="Browse", command=self.browse)
        self.browse_button.pack(pady=5)

        # Quality Options
        self.quality_label = tk.Label(master, text="Select Quality (for YouTube only):")
        self.quality_label.pack(pady=10)
        self.quality_var = tk.StringVar(value="best")
        self.quality_options = ttk.Combobox(master, textvariable=self.quality_var, values=["best", "worst", "audio only"], state="readonly")
        self.quality_options.pack(pady=5)

        # Download Button
        self.download_button = tk.Button(master, text="Start Download", command=self.download)
        self.download_button.pack(pady=10)

        # Progress Bar
        self.progress_bar = ttk.Progressbar(master, orient="horizontal", mode="indeterminate")
        self.progress_bar.pack(pady=10, fill=tk.X)

    def browse(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, folder_selected)

    def download(self):
        url = self.url_entry.get().strip()
        download_path = Path(self.path_entry.get().strip())
        
        # Validate URL
        print("Validating URL...")
        if not is_valid_url(url):
            messagebox.showerror("Error", "Please enter a valid YouTube or TikTok URL.")
            return

        # Start Download Process
        print("Starting download...")
        self.progress_bar.start()

        output_template = download_path / "%(title)s.%(ext)s"
        
        # Determine format option - Only set format for YouTube
        if "youtube" in url or "youtu.be" in url:
            format_option = {
                "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "worst": "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst",
                "audio only": "bestaudio/best"
            }.get(self.quality_var.get(), "best")
            yt_dlp_args = [str(yt_dlp_path), url, "-f", format_option, "-o", str(output_template), "--merge-output-format", "mp4", "--verbose"]
        else:
            # For TikTok, don't specify a format; let yt-dlp choose the best
            yt_dlp_args = [str(yt_dlp_path), url, "-o", str(output_template), "--merge-output-format", "mp4", "--verbose"]

        # Add ffmpeg/bin directory to PATH for yt-dlp merging
        ffmpeg_bin_path = ffmpeg_extracted_folder / "bin"
        os.environ["PATH"] += os.pathsep + str(ffmpeg_bin_path)

        try:
            log_file_name = sanitize_filename(url.split("/")[-1]) + ".log"
            log_file_path = download_path / log_file_name
            with log_file_path.open('w') as log_file:
                print("Running yt-dlp command...")
                process = subprocess.Popen(
                    yt_dlp_args,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True
                )

                while True:
                    output = process.stdout.readline()
                    if output == "" and process.poll() is not None:
                        break
                    if output:
                        print(output.strip())
                        log_file.write(output)

                returncode = process.wait()
                self.progress_bar.stop()
                print(f"yt-dlp exited with code {returncode}")

                if returncode == 0:
                    print("Download complete.")
                    messagebox.showinfo("Success", "Download complete!")

                    # Locate the final merged mp4 file by timestamp to ensure the current time is applied
                    final_file = max(download_path.glob("*.mp4"), key=os.path.getctime)
                    print(f"Final file to update timestamp: {final_file}")
                    current_time = time.time()
                    os.utime(final_file, (current_time, current_time))

                else:
                    print(f"Download failed with exit code {returncode}.")
                    messagebox.showerror("Error", f"Download failed with exit code {returncode}. Please try updating yt-dlp.")

            # Save the current configuration
            config['DownloadPath'] = str(download_path)
            config_file_path.write_text(json.dumps(config))

        except Exception as e:
            self.progress_bar.stop()
            print(f"An error occurred during download process: {e}")
            messagebox.showerror("Error", f"An error occurred: {e}")

# Run the application
if __name__ == "__main__":
    try:
        root = tk.Tk()
        app = VideoDownloader(root)
        root.mainloop()
    except Exception as e:
        print(f"An error occurred: {e}")
        messagebox.showerror("Fatal Error", f"An error occurred: {e}")
