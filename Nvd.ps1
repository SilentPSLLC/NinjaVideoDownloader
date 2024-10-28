# Define paths
$downloadFolder = "C:\Program Files\NinjaVideoDownloader"
$ytDlpPath = "$downloadFolder\yt-dlp.exe"
$tempLogPath = "$env:TEMP\NinjaVideoDownloader.log"
$finalLogPath = "$downloadFolder\NinjaVideoDownloader.log"

# Create the download directory if it doesn't exist
if (-Not (Test-Path $downloadFolder)) {
    New-Item -ItemType Directory -Path $downloadFolder | Out-Null
    Write-Host "Created directory: $downloadFolder" | Out-File -Append -FilePath $tempLogPath
} else {
    Write-Host "Directory already exists: $downloadFolder" | Out-File -Append -FilePath $tempLogPath
}

# Download yt-dlp if it doesn't exist
if (-Not (Test-Path $ytDlpPath)) {
    $ytDlpUrl = "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp.exe"
    Invoke-WebRequest -Uri $ytDlpUrl -OutFile $ytDlpPath
    Write-Host "Downloaded yt-dlp to $ytDlpPath" | Out-File -Append -FilePath $tempLogPath
}

# Function to download video
function Download-Video {
    param (
        [string]$url
    )

    # Specify output path
    $outputPath = "$downloadFolder\%(title)s.%(ext)s"

    # Execute the yt-dlp command with verbose flag and output path
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $ytDlpPath
    $processInfo.Arguments = "`"$url`" --output `"$outputPath`" --verbose"
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true
    $processInfo.UseShellExecute = $false
    $processInfo.CreateNoWindow = $true

    $process = [System.Diagnostics.Process]::Start($processInfo)

    # Capture output
    $output = $process.StandardOutput.ReadToEnd()
    $error = $process.StandardError.ReadToEnd()

    $process.WaitForExit()

    # Log output and error
    Write-Host $output | Out-File -Append -FilePath $tempLogPath
    Write-Host $error | Out-File -Append -FilePath $tempLogPath

    if ($process.ExitCode -eq 0) {
        Write-Host "Download complete." | Out-File -Append -FilePath $tempLogPath
    } else {
        Write-Host "Download failed with exit code $($process.ExitCode)." | Out-File -Append -FilePath $tempLogPath
    }
}

# Ask for the URL and download the video
$url = Read-Host "Enter the TikTok or YouTube video URL"
Download-Video -url $url

# Move the log file to the NinjaVideoDownloader directory
if (Test-Path $tempLogPath) {
    Move-Item -Path $tempLogPath -Destination $finalLogPath -Force
    Write-Host "Log moved to: $finalLogPath"
} else {
    Write-Host "No log file to move."
}
