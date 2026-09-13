@echo off
title LiveKit AI Voice Agent - Laptop Controller
color 0A
cls
echo =================================================================
echo   LIVEKIT AI VOICE AGENT WORKER (LAPTOP VOICE CONTROLLER)
echo =================================================================
echo.
echo   Connecting to LiveKit Cloud...
echo   Keep this terminal open while talking in http://localhost:3000
echo.
cd /d "%~dp0\.."
py agent/agent.py dev
pause
