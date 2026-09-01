@echo off
title AI Financial Advisor - Stop
echo Stopping AI Financial Advisor servers (backend :8001, frontend :5173)...

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":8001" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /T /F >nul 2>nul
)

for /f "tokens=5" %%P in ('netstat -ano ^| findstr ":5173" ^| findstr "LISTENING"') do (
    taskkill /PID %%P /T /F >nul 2>nul
)

echo Done. If a server window is still open, you can close it manually.
pause
