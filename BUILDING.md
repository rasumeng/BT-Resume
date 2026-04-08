# Building & Packaging Resume AI

This guide explains how to build the standalone Windows installer for Resume AI.

## Overview

The installer handles:
- ✓ Zero Python installation required
- ✓ Automated Ollama detection & setup
- ✓ Automatic model downloading
- ✓ Professional installer UI
- ✓ Desktop shortcuts & Start Menu integration

## Prerequisites

1. **Windows (7 or later)**
2. **Python 3.11+** (only needed for building, not for end users)
3. **Inno Setup** - Download from: https://jrsoftware.org/isdl.php

## Step 1: Update Dependencies

Before building, update your virtual environment with PyInstaller:

```powershell
pip install -r requirements.txt
```

## Step 2: Create Application Icon

Create a 256x256 PNG icon and convert it to .ico format (optional but recommended):

```powershell
# Using PIL/Pillow to convert PNG to ICO
python -c "from PIL import Image; Image.open('resume-ai.png').save('resume-ai.ico')"
```

Or use an online converter: https://icoconvert.com/

Place `resume-ai.ico` in the project root directory.

## Step 3: Build the Executable

Run PyInstaller to create the standalone executable:

```powershell
pyinstaller resume-ai.spec
```

This creates a `dist\ResumeAI\` folder containing the executable and all dependencies.

**Expected output structure:**
```
dist/
└── ResumeAI/
    ├── ResumeAI.exe (main executable)
    ├── resume-ai.ico
    ├── core/
    ├── gui/
    ├── samples/
    └── [other .dll files and dependencies]
```

**Build time:** 5-10 minutes (first time)
**Size:** ~300-400 MB (mostly Python runtime)

## Step 4: Test the Executable

Before packaging, test the standalone executable:

```powershell
dist\ResumeAI\ResumeAI.exe
```

This should:
1. Detect Ollama status
2. Prompt for setup if needed
3. Launch the GUI normally

## Step 5: Create the Installer

### Option A: Using Inno Setup GUI (Recommended)

1. **Open Inno Setup Compiler**
2. **File → Open** → Select `ResumeAI.iss`
3. **Build → Compile** (or press Ctrl+F9)
4. Output: `dist\ResumeAI-Setup-1.0.exe`

### Option B: Command Line

```powershell
& 'C:\Program Files (x86)\Inno Setup 6\ISCC.exe' ResumeAI.iss
```

Adjust the path if you installed Inno Setup elsewhere.

## Step 6: Test the Installer

1. **Run** `dist\ResumeAI-Setup-1.0.exe`
2. **Follow the wizard**
3. **Choose installation location** (default: `C:\Program Files\Resume AI`)
4. **Verify shortcuts** were created on Desktop and Start Menu
5. **Launch the app** from the installer's final screen
6. **Test the setup wizard**:
   - Should detect Ollama
   - Should prompt to download if missing
   - Should pull models if needed

## Step 7: Distribution

The installer file `ResumeAI-Setup-1.0.exe` is ready to distribute!

- Upload to GitHub Releases
- Host on your website
- Share via email or cloud storage

## What Users See (End-User Experience)

1. **Downloads** `ResumeAI-Setup-1.0.exe` (~100 MB)
2. **Double-clicks** installer
3. **Sees** professional setup wizard
4. **Chooses** installation folder (default: `C:\Program Files\Resume AI`)
5. **Installer completes** and launches the app
6. **First-run setup** runs:
   - Detects Ollama
   - Offers to install if missing
   - Downloads Llama 3 and Mistral (⏱ takes 5-15 min depending on internet)
   - Shows progress
7. **App launches** ready to use

## Troubleshooting Build Issues

### PyInstaller errors?
```powershell
# Rebuild the spec file
pyinstaller --onefile --windowed --add-data "core:core" --add-data "gui:gui" --add-data "samples:samples" run.py
```

### Missing DLLs?
```powershell
# Add to hidden imports in resume-ai.spec
hiddenimports=['your_module_name']
```

### Inno Setup won't find executable?
```
- Verify dist\ResumeAI\ResumeAI.exe exists
- Check ResumeAI.iss Source path: "dist\ResumeAI\*"
```

### Icon not showing?
```
- Ensure resume-ai.ico is in project root
- Re-run PyInstaller
```

## Updating the Installer

When you release updates:

1. **Update version** in:
   - `ResumeAI.iss` → `AppVersion=X.X`
   - `resume-ai.spec` (if needed)
2. **Rebuild EXE** → `pyinstaller resume-ai.spec`
3. **Build new installer** → Inno Setup compile
4. **Test thoroughly** before distribution

## Uninstalling (User Side)

Users can uninstall through:
- Windows Settings → Apps
- Or: `Control Panel → Programs → Programs and Features → Resume AI → Uninstall`

The uninstaller (created by Inno Setup) automatically:
- Removes program files
- Removes Start Menu shortcuts
- Removes Desktop shortcut
- Leaves config & downloaded models (in `%APPDATA%\ResumeAI\`)

## Advanced: Code Signing

For professional distribution, you can digitally sign the installer:

```powershell
# After building with Inno Setup, sign the EXE
& 'C:\Program Files (x86)\Windows Kits\10\bin\10.0.19041.0\x64\signtool.exe' sign /f mycert.pfx /p mypassword /t http://timestamp.server.com dist\ResumeAI-Setup-1.0.exe
```

(Requires a code signing certificate - optional for testing/distribution)

## Architecture

```
[User clicks ResumeAI-Setup-1.0.exe]
           ↓
    [Inno Setup Wizard]
           ↓
    [Copies files to C:\Program Files\Resume AI]
           ↓
    [Creates Start Menu & Desktop shortcuts]
           ↓
    [User clicks shortcut → C:\Program Files\Resume AI\ResumeAI.exe]
           ↓
    [First-run SetupWizard runs]
           ↓
    [Detects/Installs Ollama]
           ↓
    [Downloads models using ollama pull]
           ↓
    [CustomTkinter GUI launches]
           ↓
    [Ready to process resumes!]
```

## Notes

- **No Python required**: Users don't need Python installed
- **All local**: No cloud dependencies or external servers
- **Portable**: App works even if moved/reinstalled
- **Config location**: `%APPDATA%\ResumeAI\` (Windows)
- **Models location**: Ollama manages this (default: `%USERPROFILE%\.ollama\models\`)

---

**Questions?** Check that:
- [ ] PyInstaller completed without errors
- [ ] `dist\ResumeAI\ResumeAI.exe` exists and runs
- [ ] `ResumeAI.iss` Source path points to correct dist folder
- [ ] Inno Setup was installed successfully
