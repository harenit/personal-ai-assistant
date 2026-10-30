Write-Host "Starting AURA Personal Autonomous AI Companion..." -ForegroundColor Cyan

if (-not (Test-Path "node_modules")) {
    Write-Host "Installing frontend dependencies..." -ForegroundColor Yellow
    npm install
}

npm run dev
