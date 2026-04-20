# Resume AI - Complete Application Launcher
# Starts backend and frontend together with health checks

param(
    [switch]$NoWait = $false
)

$ErrorActionPreference = "Stop"

Write-Host "`n════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host "[*] Resume AI - Complete Application Launcher" -ForegroundColor Cyan
Write-Host "════════════════════════════════════════════════════════`n" -ForegroundColor Cyan

# Get script directory
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$backendDir = $scriptDir
$flutterDir = Join-Path $scriptDir "flutter_app"

# Clean up any existing processes
Write-Host "[*] Checking for existing processes..." -ForegroundColor Yellow
$existingPython = Get-Process -Name "python" -ErrorAction SilentlyContinue
$existingFlutter = Get-Process -Name "flutter" -ErrorAction SilentlyContinue

if ($existingPython -or $existingFlutter) {
    Write-Host "[!] Found existing processes, cleaning up..." -ForegroundColor Yellow
    Get-Process | Where-Object {$_.ProcessName -match "python|flutter|dart"} | Stop-Process -Force -ErrorAction SilentlyContinue
    Start-Sleep -Seconds 2
    Write-Host "[+] Cleanup complete" -ForegroundColor Green
}

# Start Backend
Write-Host "`n[*] Starting Backend Server..." -ForegroundColor Cyan
$backendProcess = Start-Process -FilePath "python" -ArgumentList "run_backend.py" -WorkingDirectory $backendDir -PassThru
Write-Host "[+] Backend process started (PID: $($backendProcess.Id))" -ForegroundColor Green

# Wait for backend to be healthy
Write-Host "`n[*] Waiting for backend to be ready..." -ForegroundColor Yellow
$maxAttempts = 30
$attempt = 0
$backendReady = $false

while ($attempt -lt $maxAttempts -and -not $backendReady) {
    try {
        $response = Invoke-WebRequest -Uri "http://127.0.0.1:5000/api/health" -TimeoutSec 5 -UseBasicParsing -ErrorAction SilentlyContinue
        if ($response.StatusCode -eq 200) {
            $backendReady = $true
            Write-Host "[+] Backend is ready!" -ForegroundColor Green
        }
    }
    catch {
        $attempt++
        Write-Host "    Attempt $attempt/$maxAttempts - waiting..." -ForegroundColor Gray
        Start-Sleep -Seconds 1
    }
}

if (-not $backendReady) {
    Write-Host "[!] Backend failed to start or respond" -ForegroundColor Red
    Write-Host "    Killing backend process..." -ForegroundColor Yellow
    Stop-Process -Id $backendProcess.Id -Force -ErrorAction SilentlyContinue
    exit 1
}

# Start Frontend
Write-Host "`n[*] Starting Frontend Application..." -ForegroundColor Cyan
$flutterProcess = Start-Process -FilePath "flutter" -ArgumentList "run", "-d", "windows" -WorkingDirectory $flutterDir -PassThru
Write-Host "[+] Frontend process started (PID: $($flutterProcess.Id))" -ForegroundColor Green

Write-Host "`n════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "[+] Application Started Successfully!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════" -ForegroundColor Green
Write-Host "`n[*] Backend: http://127.0.0.1:5000" -ForegroundColor Cyan
Write-Host "[*] Frontend: Flutter app on Windows" -ForegroundColor Cyan
Write-Host "`n[!] Both processes are running in the background." -ForegroundColor Yellow
Write-Host "[!] Close either window to stop that component." -ForegroundColor Yellow
Write-Host "[!] Close both to fully stop the application.`n" -ForegroundColor Yellow

# Monitor both processes
if (-not $NoWait) {
    Write-Host "[*] Monitoring processes..." -ForegroundColor Gray
    
    while ($true) {
        # Check if either process has exited
        $backendAlive = Get-Process -Id $backendProcess.Id -ErrorAction SilentlyContinue
        $flutterAlive = Get-Process -Id $flutterProcess.Id -ErrorAction SilentlyContinue
        
        if (-not $backendAlive) {
            Write-Host "`n[!] Backend process has stopped!" -ForegroundColor Yellow
            if ($flutterAlive) {
                Write-Host "[*] Stopping frontend..." -ForegroundColor Yellow
                Stop-Process -Id $flutterProcess.Id -Force -ErrorAction SilentlyContinue
            }
            break
        }
        
        if (-not $flutterAlive) {
            Write-Host "`n[!] Frontend process has stopped!" -ForegroundColor Yellow
            Write-Host "[*] Backend is still running at http://127.0.0.1:5000" -ForegroundColor Cyan
            break
        }
        
        Start-Sleep -Seconds 2
    }
}

Write-Host "`n[+] Application launcher complete" -ForegroundColor Green
