@echo off
title JARVIS Launcher
echo ========================================================
echo  Starting JARVIS AI Agent & Web Dashboard...
echo ========================================================

:: Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Python is not installed or not in your PATH.
    pause
    exit /b 1
)

:: Start unified server
echo Starting JARVIS Unified Server on http://127.0.0.1:8000 ...
start "JARVIS Server" cmd /k "python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload"

:: Wait 3 seconds for server to initialize and open browser
timeout /t 3 >nul
echo Opening JARVIS in your default browser...
start http://127.0.0.1:8000

echo.
echo ========================================================
echo  JARVIS is running!
echo  URL: http://127.0.0.1:8000
echo ========================================================
