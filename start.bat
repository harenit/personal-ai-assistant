@echo off
title AURA - Autonomous AI Companion
cd /d "%~dp0frontend"

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

echo Starting AURA...
call npm run dev

pause
