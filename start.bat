@echo off
title HideX Secure PII Guard Launcher
echo ===================================================
echo             HIDEX SECURE PII GUARD LAUNCHER
echo ===================================================
echo.

:: Check if backend virtual environment exists
if not exist "backend\venv\Scripts\python.exe" (
    echo [ERROR] Virtual environment 'backend\venv' not found.
    echo Please run installation first.
    pause
    exit /b 1
)

echo [INFO] Starting Backend (FastAPI)...
start "HideX Backend (FastAPI)" cmd /k "title HideX Backend && echo Starting FastAPI server... && backend\venv\Scripts\python.exe -m backend.main"

echo [INFO] Starting Frontend (Vite)...
start "HideX Frontend (React + Vite)" cmd /k "title HideX Frontend && echo Starting Vite development server... && cd frontend && npm run dev"

echo [INFO] Waiting for servers to initialize...
timeout /t 4 >nul

echo [INFO] Launching App in Browser...
start http://localhost:5173

echo.
echo ===================================================
echo [SUCCESS] Both servers are running in the background!
echo You can manage them in their respective cmd windows.
echo ===================================================
echo.
pause
