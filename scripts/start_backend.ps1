Write-Host "Starting JARVIS Python Backend..." -ForegroundColor Cyan
$backendDir = Join-Path $PSScriptRoot "..\backend"
Set-Location -Path $backendDir

$venvPython = Join-Path $backendDir ".venv\Scripts\python.exe"
if (Test-Path $venvPython) {
    & $venvPython main.py
} else {
    python main.py
}
