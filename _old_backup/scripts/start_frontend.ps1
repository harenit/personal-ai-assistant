# JARVIS - Start React Frontend Server
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " JARVIS — React + Vite Student Dashboard" -ForegroundColor Cyan
Write-Host " Starting Frontend..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

$npmCmd = Get-Command npm -ErrorAction SilentlyContinue
if (-not $npmCmd) {
    Write-Host "[ERROR] Node.js & npm are not installed or not in PATH." -ForegroundColor Red
    Exit 1
}

Write-Host "[OK] Node detected: $(node --version)" -ForegroundColor Green

Set-Location "$PSScriptRoot\..\frontend"
if (-not (Test-Path "node_modules")) {
    Write-Host "[INSTALLING] Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

Write-Host "`n[STARTING] Frontend dev server on http://localhost:5173" -ForegroundColor Cyan
npm run dev
