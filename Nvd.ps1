# ============================================================================
# TubeArc Media Archiver - PowerShell Launcher
# Version: 3.1.0 (Codename: Kitsune 🦊)
# ============================================================================
# This script automatically finds Python, verifies dependencies, and launches
# TubeArc Media Archiver with proper error handling and status reporting.
# ============================================================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   TubeArc Media Archiver v3.1.0" -ForegroundColor Cyan
Write-Host "   Codename: Kitsune 🦊" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Get the directory where this script is located
$SCRIPT_DIR = Split-Path -Parent $MyInvocation.MyCommand.Path
$TUBEARC_PY = Join-Path $SCRIPT_DIR "tubearc.py"

# ============================================================================
# STEP 1: Verify tubearc.py exists
# ============================================================================
Write-Host "Checking for TubeArc application..." -ForegroundColor Yellow

if (-not (Test-Path $TUBEARC_PY)) {
    Write-Host "[ERROR] tubearc.py not found in the current directory!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Expected location: $TUBEARC_PY" -ForegroundColor Yellow
    Write-Host "Please make sure this script is in the same folder as tubearc.py" -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Found: tubearc.py" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 2: Find Python installation
# ============================================================================
Write-Host "Searching for Python installation..." -ForegroundColor Yellow

# Function to test if a command exists
function Test-Command {
    param($command)
    try {
        if (Get-Command $command -ErrorAction Stop) {
            return $true
        }
    } catch {
        return $false
    }
    return $false
}

# Function to get full path of Python executable
function Get-PythonPath {
    param($command)
    try {
        $path = (Get-Command $command -ErrorAction Stop).Source
        return $path
    } catch {
        return $null
    }
}

# Try to find Python
$PYTHON_EXE = $null
$pythonCommands = @("python", "python3", "py")

foreach ($cmd in $pythonCommands) {
    if (Test-Command $cmd) {
        $PYTHON_EXE = Get-PythonPath $cmd
        if ($PYTHON_EXE) {
            break
        }
    }
}

# If Python not found, show error
if (-not $PYTHON_EXE) {
    Write-Host "[ERROR] Python not found!" -ForegroundColor Red
    Write-Host ""
    Write-Host "TubeArc requires Python 3.7 or higher." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Installation instructions:" -ForegroundColor Cyan
    Write-Host "  1. Download Python from: https://www.python.org/downloads/" -ForegroundColor White
    Write-Host "  2. Run the installer" -ForegroundColor White
    Write-Host "  3. CHECK the box: 'Add Python to PATH'" -ForegroundColor Yellow
    Write-Host "  4. Complete the installation" -ForegroundColor White
    Write-Host "  5. Restart this script" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# ============================================================================
# STEP 3: Verify Python exists at detected path
# ============================================================================
if (-not (Test-Path $PYTHON_EXE)) {
    Write-Host "[ERROR] Python not found at: $PYTHON_EXE" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[OK] Using Python at: $PYTHON_EXE" -ForegroundColor Green

# ============================================================================
# STEP 4: Display Python version
# ============================================================================
try {
    & $PYTHON_EXE --version
    Write-Host ""
} catch {
    Write-Host "[WARNING] Could not determine Python version" -ForegroundColor Yellow
    Write-Host ""
}

# ============================================================================
# STEP 5: Check for requests library
# ============================================================================
Write-Host "Checking for required library..." -ForegroundColor Yellow

$checkRequests = & $PYTHON_EXE -c "import requests" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[INFO] Installing requests library..." -ForegroundColor Yellow
    Write-Host ""
    
    try {
        & $PYTHON_EXE -m pip install requests
        Write-Host ""
        
        if ($LASTEXITCODE -eq 0) {
            Write-Host "[OK] Installation complete" -ForegroundColor Green
        } else {
            Write-Host "[WARNING] Installation may have failed" -ForegroundColor Yellow
            Write-Host "TubeArc will attempt to start anyway..." -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARNING] Could not install requests library" -ForegroundColor Yellow
        Write-Host "Error: $_" -ForegroundColor Yellow
        Write-Host "TubeArc will attempt to start anyway..." -ForegroundColor Yellow
    }
} else {
    Write-Host "[OK] requests library already installed" -ForegroundColor Green
}

Write-Host "[OK] All dependencies ready" -ForegroundColor Green
Write-Host ""

# ============================================================================
# STEP 6: Launch TubeArc
# ============================================================================
Write-Host "Starting TubeArc Media Archiver..." -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Change to script directory
Set-Location $SCRIPT_DIR

# Run the application
& $PYTHON_EXE tubearc.py

# ============================================================================
# STEP 7: Check for errors
# ============================================================================
if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host "[ERROR] Application encountered an error" -ForegroundColor Red
    Write-Host "==========================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Exit code: $LASTEXITCODE" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Troubleshooting tips:" -ForegroundColor Cyan
    Write-Host "  1. Make sure Python 3.7+ is installed" -ForegroundColor White
    Write-Host "  2. Try running: py -m pip install requests" -ForegroundColor White
    Write-Host "  3. Check that tubearc.py is not corrupted" -ForegroundColor White
    Write-Host "  4. Run tubearc.py directly to see error details" -ForegroundColor White
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit $LASTEXITCODE
}

# Success!
Write-Host ""
Write-Host "[OK] TubeArc closed successfully" -ForegroundColor Green
Write-Host ""
