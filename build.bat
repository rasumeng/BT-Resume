@echo off
REM Build script for Resume AI installer
REM This automates the entire build process

setlocal enabledelayedexpansion

echo.
echo ======================================
echo Resume AI - Build Script
echo ======================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.11+ and add it to PATH.
    pause
    exit /b 1
)

REM Check if PyInstaller is installed
python -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo INFO: Installing PyInstaller...
    python -m pip install -r requirements.txt
)

REM Check if Inno Setup is installed
set "INNO_PATH=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist "!INNO_PATH!" (
    echo WARNING: Inno Setup not found at: !INNO_PATH!
    echo Download from: https://jrsoftware.org/isdl.php
    echo.
    set "SKIP_INSTALLER=1"
)

REM Step 1: Clean previous build
echo [1/4] Cleaning previous build...
if exist "dist" (
    rmdir /s /q dist
)
if exist "build" (
    rmdir /s /q build
)
if exist "__pycache__" (
    rmdir /s /q __pycache__
)
echo.

REM Step 2: Build executable with PyInstaller
echo [2/4] Building executable with PyInstaller...
echo (This may take 5-10 minutes on first build)
echo.

python -m PyInstaller resume-ai.spec
if errorlevel 1 (
    echo ERROR: PyInstaller failed.
    pause
    exit /b 1
)

echo.
echo ✓ Executable built successfully!
echo.

REM Step 3: Copy icon if it exists
if exist "resume-ai.ico" (
    echo [3/4] Copying icon...
    copy /y resume-ai.ico dist\ResumeAI\resume-ai.ico >nul
    echo ✓ Icon copied
    echo.
)

REM Step 4: Build installer with Inno Setup
if defined SKIP_INSTALLER (
    echo [4/4] Skipping installer build (Inno Setup not found)
    echo.
    echo To create the installer:
    echo 1. Install Inno Setup from: https://jrsoftware.org/isdl.php
    echo 2. Open ResumeAI.iss with Inno Setup
    echo 3. Click Build ^> Compile
    echo.
) else (
    echo [4/4] Building installer with Inno Setup...
    "!INNO_PATH!" ResumeAI.iss
    if errorlevel 1 (
        echo ERROR: Inno Setup build failed.
        pause
        exit /b 1
    )
    echo.
    echo ✓ Installer built successfully!
    echo.
)

echo ======================================
echo Build Complete!
echo ======================================
echo.
echo Output files:
if exist "dist\ResumeAI\ResumeAI.exe" (
    echo ✓ dist\ResumeAI\ResumeAI.exe (executable)
    echo.
    echo Test the executable:
    echo   dist\ResumeAI\ResumeAI.exe
    echo.
)

if exist "dist\ResumeAI-Setup-1.0.exe" (
    echo ✓ dist\ResumeAI-Setup-1.0.exe (installer)
    echo.
    echo Distribute the installer:
    echo   dist\ResumeAI-Setup-1.0.exe
    echo.
)

if not defined SKIP_INSTALLER (
    echo Ready to distribute! The installer includes:
    echo - Complete Python runtime
    echo - All dependencies
    echo - Setup wizard for Ollama
    echo - Automatic model download
    echo.
)

pause
