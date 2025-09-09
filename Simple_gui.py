import tkinter as tk
from tkinter import messagebox, ttk, filedialog
import subprocess
import threading
from pathlib import Path
import requests
import re
import os
import json

# Setup paths
download_folder = Path.home() / "Downloads" / "NinjaVideoDownloader"
yt_dlp_path = download_folder / "yt-dlp.exe"
config_file_path = download_folder / "config.json"

# URLs for required downloads
yt_dlp_url = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"

class SimpleVideoDownloader:
    def __init__(self, root):
        self.root = root
        root.title("Ninja Video Downloader v1.2.0")
        root.geometry("600x350")
        root.resizable(True, False)
        
        # Ensure download folder exists
        download_folder.mkdir(parents=True, exist_ok=True)
        
        # Load config
        self.load_config()
        
        # Main frame
        main_frame = tk.Frame(root, padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Title
        title_label = tk.Label(main_frame, text="Ninja Video Downloader", 
                              font=("Arial", 16, "bold"), fg="blue")
        title_label.pack(pady=(0, 10))
        
        # URL input
        url_frame = tk.Frame(main_frame)
        url_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(url_frame, text="Video URL (YouTube, TikTok, Instagram):", 
                font=("Arial", 10)).pack(anchor=tk.W)
        self.url_entry = tk.Entry(url_frame, font=("Arial", 10))
        self.url_entry.pack(fill=tk.X, pady=(5, 0))
        self.url_entry.bind('<Return>', lambda e: self.start_download())
        
        # Platform detection label
        self.platform_label = tk.Label(main_frame, text="", font=("Arial", 9), fg="gray")
        self.platform_label.pack(pady=(0, 5))
        self.url_entry.bind('<KeyRelease>', self.detect_platform)
        
        # Download directory
        dir_frame = tk.Frame(main_frame)
        dir_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Label(dir_frame, text="Download Directory:", font=("Arial", 10)).pack(anchor=tk.W)
        
        dir_input_frame = tk.Frame(dir_frame)
        dir_input_frame.pack(fill=tk.X, pady=(5, 0))
        
        self.dir_entry = tk.Entry(dir_input_frame, font=("Arial", 9))
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.dir_entry.insert(0, self.config.get('download_path', str(download_folder)))
        
        browse_btn = tk.Button(dir_input_frame, text="Browse", command=self.browse_directory)
        browse_btn.pack(side=tk.RIGHT, padx=(5, 0))
        
        # Options frame
        options_frame = tk.Frame(main_frame)
        options_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Quality selection (YouTube only)
        quality_frame = tk.Frame(options_frame)
        quality_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        tk.Label(quality_frame, text="Quality:", font=("Arial", 9)).pack(anchor=tk.W)
        self.quality_var = tk.StringVar(value="best")
        self.quality_combo = ttk.Combobox(quality_frame, textvariable=self.quality_var,
                                         values=["best", "worst", "audio only"], 
                                         state="readonly", width=12)
        self.quality_combo.pack(pady=(2, 0))
        
        # Options checkboxes
        checkbox_frame = tk.Frame(options_frame)
        checkbox_frame.pack(side=tk.LEFT)
        
        self.metadata_var = tk.BooleanVar(value=True)
        metadata_check = tk.Checkbutton(checkbox_frame, text="Save metadata",
                                       variable=self.metadata_var, font=("Arial", 9))
        metadata_check.pack(anchor=tk.W)
        
        self.subtitle_var = tk.BooleanVar(value=False)
        subtitle_check = tk.Checkbutton(checkbox_frame, text="Download subtitles",
                                       variable=self.subtitle_var, font=("Arial", 9))
        subtitle_check.pack(anchor=tk.W)
        
        # Download button
        self.download_btn = tk.Button(main_frame, text="Download Video", 
                                     command=self.start_download, 
                                     font=("Arial", 12, "bold"),
                                     bg="#4CAF50", fg="white",
                                     height=2, cursor="hand2")
        self.download_btn.pack(fill=tk.X, pady=(10, 10))
        
        # Progress bar
        self.progress = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress.pack(fill=tk.X, pady=(0, 10))
        
        # Status label
        self.status_label = tk.Label(main_frame, text="Ready", 
                                    font=("Arial", 9), fg="green")
        self.status_label.pack()
        
        # Footer
        footer_frame = tk.Frame(main_frame)
        footer_frame.pack(pady=(10, 0))
        
        info_label = tk.Label(footer_frame, text="Supports YouTube, TikTok, Instagram", 
                             font=("Arial", 8), fg="gray")
        info_label.pack()
        
        thanks_label = tk.Label(footer_frame, text="Thanks to yt-dlp", 
                               font=("Arial", 8), fg="gray")
        thanks_label.pack()
        
        # Initialize yt-dlp
        self.ensure_ytdlp()
        
    def load_config(self):
        """Load configuration from file"""
        self.config = {}
        if config_file_path.exists():
            try:
                with config_file_path.open('r') as f:
                    self.config = json.load(f)
            except Exception as e:
                print(f"Failed to load config: {e}")
                self.config = {}
        
        # Set defaults
        if 'download_path' not in self.config:
            self.config['download_path'] = str(download_folder)
    
    def save_config(self):
        """Save configuration to file"""
        try:
            with config_file_path.open('w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def browse_directory(self):
        """Browse for download directory"""
        folder = filedialog.askdirectory(initialdir=self.dir_entry.get())
        if folder:
            self.dir_entry.delete(0, tk.END)
            self.dir_entry.insert(0, folder)
    
    def detect_platform(self, event=None):
        """Detect platform from URL and update UI"""
        url = self.url_entry.get().strip()
        if not url:
            self.platform_label.config(text="")
            self.quality_combo.config(state="readonly")
            return
        
        platform = self.get_platform(url)
        if platform == "youtube":
            self.platform_label.config(text="✓ YouTube detected", fg="blue")
            self.quality_combo.config(state="readonly")
        elif platform == "tiktok":
            self.platform_label.config(text="✓ TikTok detected", fg="purple")
            self.quality_combo.config(state="disabled")
        elif platform == "instagram":
            self.platform_label.config(text="✓ Instagram detected", fg="orange")
            self.quality_combo.config(state="disabled")
        else:
            self.platform_label.config(text="⚠ Unknown platform", fg="red")
            self.quality_combo.config(state="disabled")
    
    def get_platform(self, url):
        """Detect platform from URL"""
        if re.match(r'https?://(www\.)?(youtube\.com|youtu\.be)', url):
            return "youtube"
        elif re.match(r'https?://(www\.)?tiktok\.com', url):
            return "tiktok"
        elif re.match(r'https?://(www\.)?instagram\.com/(p|reel|tv)', url):
            return "instagram"
        return "unknown"
    
    def ensure_ytdlp(self):
        """Download yt-dlp if it doesn't exist"""
        if yt_dlp_path.exists():
            self.update_status("Ready", "green")
            return
        
        self.update_status("Setting up downloader...", "blue")
        
        def download_ytdlp():
            try:
                response = requests.get(yt_dlp_url, timeout=30)
                response.raise_for_status()
                yt_dlp_path.write_bytes(response.content)
                self.root.after(0, lambda: self.update_status("Ready", "green"))
            except Exception as e:
                self.root.after(0, lambda: self.update_status("Setup failed", "red"))
                self.root.after(0, lambda: messagebox.showerror("Setup Error", 
                    f"Failed to download yt-dlp: {e}\nPlease check your internet connection."))
        
        thread = threading.Thread(target=download_ytdlp, daemon=True)
        thread.start()
    
    def update_status(self, message, color="black"):
        """Update status label"""
        self.status_label.config(text=message, fg=color)
        self.root.update_idletasks()
    
    def start_download(self):
        """Start download in separate thread"""
        thread = threading.Thread(target=self.download, daemon=True)
        thread.start()
    
    def download(self):
        """Main download function"""
        url = self.url_entry.get().strip()
        download_path = Path(self.dir_entry.get().strip())
        
        # Validation
        if not url:
            messagebox.showwarning("No URL", "Please enter a video URL")
            return
        
        if not re.match(r'https?://', url):
            messagebox.showerror("Invalid URL", "Please enter a valid HTTP/HTTPS URL")
            return
        
        if not yt_dlp_path.exists():
            messagebox.showerror("Error", "yt-dlp not available. Please restart the application.")
            return
        
        # Save current directory to config
        self.config['download_path'] = str(download_path)
        self.save_config()
        
        # Disable UI during download
        self.download_btn.config(state="disabled", text="Downloading...")
        self.progress.start()
        self.update_status("Downloading...", "blue")
        
        try:
            # Create download directory
            download_path.mkdir(parents=True, exist_ok=True)
            
            # Build command
            platform = self.get_platform(url)
            output_template = str(download_path / "%(title)s.%(ext)s")
            
            cmd = [str(yt_dlp_path), url, "-o", output_template]
            
            # Platform-specific options
            if platform == "youtube":
                quality_map = {
                    "best": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                    "worst": "worstvideo[ext=mp4]+worstaudio[ext=m4a]/worst",
                    "audio only": "bestaudio/best"
                }
                quality = quality_map.get(self.quality_var.get(), "best")
                cmd.extend(["-f", quality, "--merge-output-format", "mp4"])
            else:
                cmd.extend(["--merge-output-format", "mp4"])
            
            # Common options
            if self.metadata_var.get():
                cmd.extend(["--write-description", "--write-thumbnail"])
            
            if self.subtitle_var.get():
                cmd.extend(["--write-subs", "--write-auto-subs"])
            
            cmd.extend(["--no-playlist", "--verbose"])
            
            # Run download
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
            
            if result.returncode == 0:
                self.update_status("Download completed!", "green")
                messagebox.showinfo("Success", 
                    f"Video downloaded successfully!\n\nSaved to:\n{download_path}")
            else:
                error_msg = result.stderr or result.stdout or "Unknown error"
                self.update_status("Download failed", "red")
                
                # Show a more user-friendly error message
                if "This video is unavailable" in error_msg:
                    messagebox.showerror("Download Failed", "This video is unavailable or private.")
                elif "Video unavailable" in error_msg:
                    messagebox.showerror("Download Failed", "Video is not available for download.")
                elif "Sign in to confirm your age" in error_msg:
                    messagebox.showerror("Download Failed", "Age-restricted video. Cannot download.")
                else:
                    messagebox.showerror("Download Failed", 
                        f"Failed to download video.\n\nError details:\n{error_msg[:300]}...")
                
        except subprocess.TimeoutExpired:
            self.update_status("Download timed out", "red")
            messagebox.showerror("Timeout", "Download took too long and was cancelled.")
        except Exception as e:
            self.update_status("Error occurred", "red")
            messagebox.showerror("Error", f"An unexpected error occurred:\n{e}")
        
        finally:
            # Re-enable UI
            self.download_btn.config(state="normal", text="Download Video")
            self.progress.stop()

if __name__ == "__main__":
    root = tk.Tk()
    app = SimpleVideoDownloader(root)
    
    # Center the window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (root.winfo_width() // 2)
    y = (root.winfo_screenheight() // 2) - (root.winfo_height() // 2)
    root.geometry(f"+{x}+{y}")
    
    # Set minimum size
    root.minsize(500, 300)
    
    root.mainloop()
