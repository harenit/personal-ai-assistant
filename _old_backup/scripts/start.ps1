# JARVIS - Master Launcher (Backend + Frontend)
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " JARVIS — Permission-Aware Autonomous AI Agent" -ForegroundColor Cyan
Write-Host " Master Startup Script" -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$rootDir = Split-Path -Parent $PSScriptRoot
if (-not $rootDir) { $rootDir = Get-Location }

# 1. Check Python
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "[ERROR] Python 3.11+ is required but not found in PATH." -ForegroundColor Red
    Exit 1
}

# 2. Check Node
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "[ERROR] Node.js is required but not found in PATH." -ForegroundColor Red
    Exit 1
}

Write-Host "[OK] Environment verified: Python $(python --version), Node $(node --version)" -ForegroundColor Green

# 3. Check Ollama
try {
    $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 2 -ErrorAction Stop
    Write-Host "[OK] Ollama is active with local models: $(($tags.models | Select-Object -First 3).name -join ', ')" -ForegroundColor Green
} catch {
    Write-Host "[WARN] Ollama is not running on http://localhost:11434. Start Ollama with 'ollama serve' if using local LLM." -ForegroundColor Yellow
}

Write-Host "`n[LAUNCHING] Starting Backend and Frontend services..." -ForegroundColor Cyan

# Launch Backend in new window
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$rootDir\scripts\start_backend.ps1"

# Launch Frontend in new window
Start-Process powershell -ArgumentList "-NoExit", "-ExecutionPolicy", "Bypass", "-File", "$rootDir\scripts\start_frontend.ps1"

Write-Host "`n==========================================================" -ForegroundColor Green
Write-Host " JARVIS is booting up!" -ForegroundColor Green
Write-Host " Backend API:   http://127.0.0.1:8000" -ForegroundColor White
Write-Host " API Docs:      http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host " Web Dashboard: http://localhost:5173" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
