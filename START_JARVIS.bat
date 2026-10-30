@echo off
setlocal enabledelayedexpansion
title JARVIS - Student Autonomous AI Companion
color 0A

echo ===============================================================================
echo          JARVIS : STUDENT-CENTRIC AUTONOMOUS AI AGENT COMPANION
echo                          LAUNCHING APPLICATION
echo ===============================================================================
echo.

cd /d "%~dp0"

:: 1. Verify Environment
if not exist "backend\.venv\Scripts\python.exe" (
    echo [WARNING] Python virtual environment not found in backend\.venv.
    echo Running one-time installation setup now...
    call INSTALL_WINDOWS.bat
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Setup failed. Please check your Python installation.
        pause
        exit /b 1
    )
)

if not exist "frontend\node_modules" (
    echo [INFO] Installing frontend modules...
    cd /d "%~dp0frontend"
    call npm install
    cd /d "%~dp0"
)

:: 2. Check for port 8756 collision and clear if lingering
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8756" ^| findstr "LISTENING"') do (
    echo [INFO] Cleaning up previous background backend on PID %%a...
    taskkill /F /PID %%a >nul 2>&1
)

:: 3. Launch JARVIS
echo.
echo [OK] Launching JARVIS (FastAPI Backend + Electron Companion UI)...
echo [OK] Brain: Groq Cloud (qwen/qwen3.8-27b) + Local Ollama Fallback
echo [OK] Voice: Fish Audio Neural TTS + Groq Whisper Cloud STT
echo [OK] Deliverables: Excel (.xlsx), Word (.docx), PowerPoint (.pptx), Study Packs
echo.
echo Press Ctrl+C in this terminal or close the window to stop JARVIS.
echo.

cd /d "%~dp0frontend"
call npm run dev

echo.
echo ===============================================================================
echo JARVIS has stopped.
echo ===============================================================================
pause
