@echo off
setlocal enabledelayedexpansion
title JARVIS - Windows Installation & Setup
color 0B

echo ===============================================================================
echo          JARVIS : STUDENT-CENTRIC AUTONOMOUS AI AGENT COMPANION
echo                          WINDOWS INSTALLATION SCRIPT
echo ===============================================================================
echo.

:: 1. Check Python
echo [1/5] Checking Python installation...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Python is not installed or not in your system PATH.
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do echo [OK] Found %%i

:: 2. Check Node.js and npm
echo.
echo [2/5] Checking Node.js and npm...
node --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Node.js is not installed or not in your system PATH.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('node --version') do echo [OK] Found Node.js %%i
for /f "tokens=*" %%i in ('npm --version') do echo [OK] Found npm %%i

:: 3. Setup Python Virtual Environment & Dependencies
echo.
echo [3/5] Setting up Python virtual environment and dependencies...
cd /d "%~dp0backend"

if not exist ".venv\Scripts\python.exe" (
    echo Creating virtual environment at backend\.venv...
    python -m venv .venv
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo Activating virtual environment and upgrading pip...
call .venv\Scripts\activate.bat
python -m pip install --upgrade pip

echo Installing backend dependencies from requirements.txt...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo [WARNING] Some dependencies had warnings during install, retrying essential packages...
    pip install fastapi uvicorn httpx pydantic openpyxl python-docx python-pptx pypdf keyring playwright
)

:: 4. Install Playwright Chromium for LMS automation
echo.
echo [4/5] Installing Playwright Chromium browser for LMS automation...
python -m playwright install chromium
if %ERRORLEVEL% NEQ 0 (
    echo [NOTE] Playwright chromium can be installed later or run without browser sandbox.
)

:: 5. Install Frontend Dependencies
echo.
echo [5/5] Installing Frontend Electron dependencies...
cd /d "%~dp0frontend"
call npm install
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Failed to install frontend packages.
    pause
    exit /b 1
)

echo.
echo ===============================================================================
echo                INSTALLATION AND VERIFICATION COMPLETE!
echo ===============================================================================
echo.
echo You can now launch JARVIS anytime by running:
echo     START_JARVIS.bat
echo.
echo Or by double-clicking START_JARVIS.bat in this folder.
echo ===============================================================================
pause
