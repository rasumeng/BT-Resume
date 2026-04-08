# Build script for Resume AI installer (PowerShell)
# Usage: .\build.ps1

$ErrorActionPreference = "Stop"

Write-Host ""
Write-Host "======================================"
Write-Host "Resume AI - Build Script"
Write-Host "======================================"
Write-Host ""

# Check Python
try {
    python --version | Out-Null
} catch {
    Write-Host "ERROR: Python not found. Please install Python 3.11+ and add it to PATH." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check PyInstaller
$pyinstaller_check = python -m pip show pyinstaller 2>$null
if (-not $pyinstaller_check) {
    Write-Host "INFO: Installing dependencies from requirements.txt..." -ForegroundColor Yellow
    pip install -r requirements.txt
}

# Check Inno Setup
$inno_path = "C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
$skip_installer = $false

if (-not (Test-Path $inno_path)) {
    Write-Host "WARNING: Inno Setup not found at: $inno_path" -ForegroundColor Yellow
    Write-Host "Download from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host ""
    $skip_installer = $true
}

# Step 1: Clean previous build
Write-Host "[1/4] Cleaning previous build..." -ForegroundColor Cyan
Get-ChildItem -Path @("dist", "build", "__pycache__") -ErrorAction SilentlyContinue | Remove-Item -Recurse -Force
Write-Host ""

# Step 2: Build executable with PyInstaller
Write-Host "[2/4] Building executable with PyInstaller..." -ForegroundColor Cyan
Write-Host "(This may take 5-10 minutes on first build)"
Write-Host ""

python -m PyInstaller resume-ai.spec
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: PyInstaller failed." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "✓ Executable built successfully!" -ForegroundColor Green
Write-Host ""

# Step 3: Copy icon if it exists
if (Test-Path "resume-ai.ico") {
    Write-Host "[3/4] Copying icon..." -ForegroundColor Cyan
    Copy-Item "resume-ai.ico" "dist\ResumeAI\resume-ai.ico" -Force
    Write-Host "✓ Icon copied" -ForegroundColor Green
    Write-Host ""
}

# Step 4: Build installer with Inno Setup
if ($skip_installer) {
    Write-Host "[4/4] Skipping installer build (Inno Setup not found)" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To create the installer:" -ForegroundColor Yellow
    Write-Host "1. Install Inno Setup from: https://jrsoftware.org/isdl.php" -ForegroundColor Yellow
    Write-Host "2. Open ResumeAI.iss with Inno Setup" -ForegroundColor Yellow
    Write-Host "3. Click Build > Compile" -ForegroundColor Yellow
    Write-Host ""
} else {
    Write-Host "[4/4] Building installer with Inno Setup..." -ForegroundColor Cyan
    & $inno_path ResumeAI.iss
    
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERROR: Inno Setup build failed." -ForegroundColor Red
        Read-Host "Press Enter to exit"
        exit 1
    }
    
    Write-Host ""
    Write-Host "✓ Installer built successfully!" -ForegroundColor Green
    Write-Host ""
}

Write-Host "======================================"
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "======================================"
Write-Host ""

Write-Host "Output files:" -ForegroundColor Cyan
if (Test-Path "dist\ResumeAI\ResumeAI.exe") {
    Write-Host "✓ dist\ResumeAI\ResumeAI.exe (executable)"
    Write-Host ""
    Write-Host "Test the executable:" -ForegroundColor Yellow
    Write-Host "  dist\ResumeAI\ResumeAI.exe"
    Write-Host ""
}

if (Test-Path "dist\ResumeAI-Setup-1.0.exe") {
    Write-Host "✓ dist\ResumeAI-Setup-1.0.exe (installer)" -ForegroundColor Green
    Write-Host ""
    Write-Host "Distribute the installer:" -ForegroundColor Yellow
    Write-Host "  dist\ResumeAI-Setup-1.0.exe"
    Write-Host ""
}

if (-not $skip_installer) {
    Write-Host "Ready to distribute! The installer includes:" -ForegroundColor Green
    Write-Host "- Complete Python runtime"
    Write-Host "- All dependencies"
    Write-Host "- Setup wizard for Ollama"
    Write-Host "- Automatic model download"
    Write-Host ""
}

Read-Host "Press Enter to exit"
