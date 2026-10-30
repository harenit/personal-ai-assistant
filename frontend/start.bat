@echo off
title AURA - Autonomous AI Companion

if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

echo Starting AURA...
call npm run dev

pause
