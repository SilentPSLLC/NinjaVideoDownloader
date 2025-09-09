# Ninja Video Downloader PowerShell Launcher v1.2.0
# Simple version that works reliably

param(
    [string]$Url = "",
    [switch]$Help
)

$ScriptName = "Ninja Video Downloader"
$Version = "1.2.0"

if ($Help) {
    Write-Host "=== $ScriptName v$Version ===" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Usage:" -ForegroundColor Yellow
    Write-Host "  .\Nvd.ps1                    # Launch GUI"
    Write-Host "  .\Nvd.ps1 -Url <video_url>   # Quick download"
    Write-Host "  .\Nvd.ps1 -Help              # Show this help"
    Write-Host ""
    Write-Host "Supported Platforms:" -ForegroundColor Green
    Write-Host "  • YouTube (youtube.com, youtu.be)"
    Write-Host "  • TikTok (tiktok.com)" 
    Write-Host "  • Instagram (instagram.com/p/, /reel/, /tv/)"
    Write-Host ""
    exit
}

Write-Host "=== $ScriptName v$Version ===" -ForegroundColor Cyan
Write-Host ""

# Check if Python is available
$pythonCmd = "python"
try {
    $version = & python --version 2>&1
    if ($version -match "Python") {
        Write-Host "Python found: $version" -ForegroundColor Green
    }
}
catch {
    try {
        $version = & python3 --version 2>&1
        if ($version -match "Python") {
            $pythonCmd = "python3"
            Write-Host "Python found: $version" -ForegroundColor Green
        }
    }
    catch {
        Write-Host "Python not found! Please install Python from python.org" -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
}

# Get script directory
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$PythonScript = Join-Path $ScriptDir "ninja_video_downloader.py"

# Quick download mode
if ($Url) {
    Write-Host "Quick download mode for: $Url" -ForegroundColor Cyan
    
    # Create simple download script
    $downloadScript = @"
import os
import sys
from pathlib import Path
import subprocess
import requests

# Setup paths
download_folder = Path.home() / "Downloads" / "NinjaVideoDownloader"
yt_dlp_path = download_folder / "yt-dlp.exe"
download_folder.mkdir(parents=True, exist_ok=True)

# Download yt-dlp if needed
if not yt_dlp_path.exists():
    print("Downloading yt-dlp...")
    response = requests.get("https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe")
    yt_dlp_path.write_bytes(response.content)
    print("yt-dlp ready!")

# Download video
url = "$Url"
output_path = download_folder / "%(title)s.%(ext)s"
cmd = [str(yt_dlp_path), url, "-o", str(output_path), "--merge-output-format", "mp4"]

print(f"Downloading to: {download_folder}")
result = subprocess.run(cmd)
sys.exit(result.returncode)
"@

    $tempFile = [System.IO.Path]::GetTempFileName() + ".py"
    $downloadScript | Out-File -FilePath $tempFile -Encoding UTF8
    
    try {
        & $pythonCmd $tempFile
        $exitCode = $LASTEXITCODE
        Remove-Item $tempFile -Force
        
        if ($exitCode -eq 0) {
            Write-Host "Download completed!" -ForegroundColor Green
        } else {
            Write-Host "Download failed!" -ForegroundColor Red
        }
    }
    catch {
        Write-Host "Error: $_" -ForegroundColor Red
        Remove-Item $tempFile -Force -ErrorAction SilentlyContinue
    }
}
else {
    # GUI mode
    if (Test-Path $PythonScript) {
        Write-Host "Launching GUI..." -ForegroundColor Green
        & $pythonCmd $PythonScript
    } else {
        Write-Host "GUI script not found: $PythonScript" -ForegroundColor Red
        Write-Host "Please ensure ninja_video_downloader.py is in the same folder" -ForegroundColor Yellow
    }
}

Write-Host "Done!" -ForegroundColor Cyan
