Write-Host "Starting JARVIS Electron Frontend..." -ForegroundColor Cyan
$frontendDir = Join-Path $PSScriptRoot "..\frontend"
Set-Location -Path $frontendDir

if (-not (Test-Path "node_modules")) {
    npm install
}

npm run dev
