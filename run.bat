@echo off
setlocal enabledelayedexpansion
title AI Financial Advisor - Launcher
cd /d "%~dp0"

echo ============================================================
echo   AI-Based Intelligent Financial Advisory System
echo   Setup + Launch
echo ============================================================
echo.

REM ---------------------------------------------------------------
REM 1. Locate a Python launcher (py preferred, falls back to python)
REM ---------------------------------------------------------------
set "PY_CMD="
where py >nul 2>nul
if %errorlevel%==0 set "PY_CMD=py"
if not defined PY_CMD (
    where python >nul 2>nul
    if %errorlevel%==0 set "PY_CMD=python"
)
if not defined PY_CMD (
    echo [ERROR] Python was not found on PATH.
    echo         Install Python 3.11+ from https://www.python.org/downloads/
    echo         ^(check "Add python.exe to PATH" during install^) and re-run this file.
    pause
    exit /b 1
)
echo [OK] Using Python launcher: %PY_CMD%

REM ---------------------------------------------------------------
REM 2. Locate Node.js / npm
REM ---------------------------------------------------------------
where node >nul 2>nul
if not %errorlevel%==0 (
    echo [ERROR] Node.js was not found on PATH.
    echo         Install Node.js 18+ LTS from https://nodejs.org/ and re-run this file.
    pause
    exit /b 1
)
where npm >nul 2>nul
if not %errorlevel%==0 (
    echo [ERROR] npm was not found on PATH ^(usually installed alongside Node.js^).
    pause
    exit /b 1
)
echo [OK] Node.js and npm found.
echo.

REM ---------------------------------------------------------------
REM 3. Backend: create venv if missing, install deps, seed DB
REM ---------------------------------------------------------------
echo ------------------------------------------------------------
echo   Backend setup
echo ------------------------------------------------------------
if not exist "backend\venv\Scripts\python.exe" (
    echo [SETUP] Creating Python virtual environment...
    %PY_CMD% -m venv "backend\venv"
    if not %errorlevel%==0 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
)

echo [SETUP] Installing/updating backend dependencies ^(first run may take a few minutes^)...
"backend\venv\Scripts\python.exe" -m pip install --upgrade pip --quiet
"backend\venv\Scripts\python.exe" -m pip install -r "backend\requirements.txt" --quiet
if not %errorlevel%==0 (
    echo [ERROR] Failed to install backend dependencies.
    pause
    exit /b 1
)

if not exist "backend\.env" (
    if exist "backend\.env.example" (
        copy /y "backend\.env.example" "backend\.env" >nul
        echo [SETUP] Created backend\.env from .env.example ^(defaults to local SQLite^).
    )
)

if not exist "backend\ai_finance.db" (
    echo [SETUP] Seeding database with question banks and demo users...
    "backend\venv\Scripts\python.exe" "backend\scripts\seed.py"
) else (
    echo [OK] Database already exists, skipping seed ^(delete backend\ai_finance.db to reseed^).
)
echo.

REM ---------------------------------------------------------------
REM 4. Frontend: install npm deps if missing
REM ---------------------------------------------------------------
echo ------------------------------------------------------------
echo   Frontend setup
echo ------------------------------------------------------------
if not exist "frontend\node_modules" (
    echo [SETUP] Installing frontend dependencies ^(first run may take a few minutes^)...
    pushd frontend
    call npm install
    popd
    if not %errorlevel%==0 (
        echo [ERROR] Failed to install frontend dependencies.
        pause
        exit /b 1
    )
) else (
    echo [OK] Frontend dependencies already installed.
)

if not exist "frontend\.env" (
    if exist "frontend\.env.example" (
        copy /y "frontend\.env.example" "frontend\.env" >nul
        echo [SETUP] Created frontend\.env from .env.example.
    )
)
echo.

REM ---------------------------------------------------------------
REM 5. Launch backend and frontend in their own windows
REM     (each via a tiny generated launcher .cmd to avoid quoting
REM      issues with `start` + nested quoted paths)
REM ---------------------------------------------------------------
echo ------------------------------------------------------------
echo   Starting servers
echo ------------------------------------------------------------

> "%~dp0backend\_start_backend.cmd" (
    echo @echo off
    echo cd /d "%~dp0backend"
    echo "%~dp0backend\venv\Scripts\python.exe" -m uvicorn app.main:app --port 8001
)

> "%~dp0frontend\_start_frontend.cmd" (
    echo @echo off
    echo cd /d "%~dp0frontend"
    echo call npm run dev
)

echo [START] Backend API  -^> http://127.0.0.1:8001  (docs at /docs)
start "AI Finance - Backend" "%~dp0backend\_start_backend.cmd"

timeout /t 3 /nobreak >nul

echo [START] Frontend app -^> http://localhost:5173
start "AI Finance - Frontend" "%~dp0frontend\_start_frontend.cmd"

echo.
echo ============================================================
echo   Both servers are starting in separate windows.
echo   Backend:  http://127.0.0.1:8001/docs
echo   Frontend: http://localhost:5173
echo.
echo   Demo logins (password: password123):
echo     asha@example.com   - low income, high expenses, low risk
echo     rohan@example.com  - moderate income, balanced, moderate risk
echo     priya@example.com  - high income, strong savings, high risk
echo.
echo   Close the two new windows to stop the servers.
echo ============================================================
pause
