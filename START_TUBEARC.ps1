# TubeArc Media Archiver Launcher
# Codename: Kitsune 🦊

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "TubeArc Media Archiver" -ForegroundColor Cyan
Write-Host "Codename: Kitsune" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $PSScriptRoot

# Set Python path
$PYTHON_EXE = "C:\Users\nam2long\AppData\Local\Programs\Python\Python314\python.exe"

# Verify Python exists
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "[ERROR] Python not found at: $PYTHON_EXE" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Using Python at: $PYTHON_EXE" -ForegroundColor Green
& $PYTHON_EXE --version
Write-Host ""

# Check for requests library
Write-Host "Checking for required library..." -ForegroundColor Yellow
$checkRequests = & $PYTHON_EXE -c "import requests" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing requests library..." -ForegroundColor Yellow
    & $PYTHON_EXE -m pip install requests
    Write-Host ""
    Write-Host "[OK] Installation complete" -ForegroundColor Green
}

Write-Host "[OK] All dependencies ready" -ForegroundColor Green
Write-Host ""
Write-Host "Starting TubeArc Media Archiver..." -ForegroundColor Cyan
Write-Host ""

# Run the application
& $PYTHON_EXE tubearc.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "[ERROR] Application encountered an error" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
}
