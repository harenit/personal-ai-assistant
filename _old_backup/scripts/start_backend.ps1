# JARVIS - Start Backend Server
Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host " JARVIS — Autonomous AI Student Productivity Agent" -ForegroundColor Cyan
Write-Host " Starting FastAPI Backend Server..." -ForegroundColor Cyan
Write-Host "==========================================================" -ForegroundColor Cyan

# 1. Check Python
$pythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonCmd) {
    Write-Host "[ERROR] Python 3.11+ is not installed or not in PATH." -ForegroundColor Red
    Exit 1
}
Write-Host "[OK] Python detected: $(python --version)" -ForegroundColor Green

# 2. Check Ollama
$ollamaCmd = Get-Command ollama -ErrorAction SilentlyContinue
if ($ollamaCmd) {
    Write-Host "[OK] Ollama detected." -ForegroundColor Green
    try {
        $tags = Invoke-RestMethod -Uri "http://localhost:11434/api/tags" -TimeoutSec 3 -ErrorAction Stop
        $modelNames = $tags.models | ForEach-Object { $_.name }
        if ($modelNames -like "*llama3.1*") {
            Write-Host "[OK] Local model llama3.1 is ready." -ForegroundColor Green
        } else {
            Write-Host "[WARN] Model llama3.1:8b not found in Ollama. Pull it using: ollama pull llama3.1:8b" -ForegroundColor Yellow
        }
    } catch {
        Write-Host "[WARN] Ollama service not responding at http://localhost:11434. Please start Ollama." -ForegroundColor Yellow
    }
} else {
    Write-Host "[WARN] Ollama not found on PATH. Ensure Ollama is running if using local LLM." -ForegroundColor Yellow
}

# 3. Start Backend
$env:PYTHONPATH = "."
Write-Host "`n[STARTING] Backend listening on http://127.0.0.1:8000" -ForegroundColor Cyan
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
