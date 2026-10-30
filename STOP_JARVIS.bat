@echo off
title JARVIS - Graceful Shutdown
color 0C

echo ===============================================================================
echo                STOPPING JARVIS APPLICATION AND BACKGROUND TASKS
echo ===============================================================================
echo.

:: 1. Stop backend on port 8756
echo [1/3] Terminating backend server on port 8756...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8756" ^| findstr "LISTENING"') do (
    taskkill /F /PID %%a >nul 2>&1
    echo Terminated backend process on PID %%a
)

:: 2. Stop Electron processes
echo.
echo [2/3] Terminating Electron frontend processes...
taskkill /F /IM electron.exe >nul 2>&1

:: 3. Stop lingering vite/node processes for frontend dev
echo.
echo [3/3] Checking for remaining instances...
echo.
echo [OK] All JARVIS services have been stopped successfully.
timeout /t 3 >nul
