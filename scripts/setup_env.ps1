# Fortis AI - Automated Environment Setup Script for Windows PowerShell

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "🛡️ FORTIS AI: Autonomous Governance & Security Copilot" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
Write-Host "`n[1/5] Verifying Python installation..." -ForegroundColor Yellow
$pythonCmd = "python"
if (-not (Get-Command $pythonCmd -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Python was not found in PATH. Please install Python 3.10+." -ForegroundColor Red
    exit 1
}
& $pythonCmd --version

# 2. Create Virtual Environment if needed
$venvPath = Join-Path $PSScriptRoot "..\.venv"
$venvPython = Join-Path $venvPath "Scripts\python.exe"
$venvPip = Join-Path $venvPath "Scripts\pip.exe"

if (-not (Test-Path $venvPython) -or -not (Test-Path $venvPip)) {
    if (Test-Path $venvPath) {
        Write-Host "`n[2/5] Cleaning up incomplete virtual environment..." -ForegroundColor Yellow
        Remove-Item -Recurse -Force $venvPath -ErrorAction SilentlyContinue
    }
    Write-Host "`n[2/5] Creating Python virtual environment (.venv) - please wait ~15-30 seconds..." -ForegroundColor Yellow
    & $pythonCmd -m venv $venvPath
    
    if (-not (Test-Path $venvPip)) {
        Write-Host "Standard venv creation interrupted or missing pip. Installing pip via ensurepip..." -ForegroundColor Yellow
        & $venvPython -m ensurepip --default-pip
    }
} else {
    Write-Host "`n[2/5] Virtual environment (.venv) verified and ready." -ForegroundColor Green
}

# 3. Install Dependencies
Write-Host "`n[3/5] Installing Python dependencies from requirements.txt..." -ForegroundColor Yellow
$reqPath = Join-Path $PSScriptRoot "..\backend\requirements.txt"
& $venvPip install -r $reqPath

# 4. Run Django Migrations & Generate Tick Dataset
Write-Host "`n[4/5] Running Django database migrations and seeding 5,000+ row tick dataset..." -ForegroundColor Yellow
$managePy = Join-Path $PSScriptRoot "..\backend\manage.py"
& $venvPython $managePy migrate --noinput

$genScript = Join-Path $PSScriptRoot "generate_tick_data.py"
& $venvPython $genScript

# 5. Start Development Server
Write-Host "`n[5/5] Launching Fortis AI Storefront Server..." -ForegroundColor Green
Write-Host "----------------------------------------------------------"
Write-Host "🌐 Dashboard URL     : http://127.0.0.1:8000/" -ForegroundColor Cyan
Write-Host "🎮 Agent Playground  : http://127.0.0.1:8000/playground/" -ForegroundColor Cyan
Write-Host "⚡ x402 Machine API  : http://127.0.0.1:8000/api/v1/scan/" -ForegroundColor Cyan
Write-Host "----------------------------------------------------------"
Write-Host "Press Ctrl+C to stop the server.`n"

& $venvPython $managePy runserver 0.0.0.0:8000
