@echo off
title SSH Inventory Management System
color 0A
echo.
echo  ========================================
echo   SSH Consumables Inventory System 2026
echo  ========================================
echo.
echo  Starting backend server...
echo.

cd /d "%~dp0backend"

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo  ERROR: Python is not installed or not in PATH.
    echo  Please install Python 3.8+ from https://python.org
    pause
    exit /b 1
)

REM Install Flask if needed
python -c "import flask" >nul 2>&1
if errorlevel 1 (
    echo  Installing Flask...
    pip install flask --quiet
)

REM Initialize DB
python -c "import app; app.init_db()" >nul 2>&1

REM Start backend in background
start "SSH Inventory API" /MIN python app.py

echo  Backend starting on http://localhost:5050
echo.
timeout /t 2 /nobreak >nul

REM Open browser
echo  Opening application in browser...
start "" "%~dp0frontend\index.html"

echo.
echo  ========================================
echo   System is running!
echo   
echo   Default Login Accounts:
echo   admin   / admin123  (Administrator)
echo   sameh   / sameh123  (Engineer)
echo   ahmed   / ahmed123  (Technician)
echo   yousef  / yousef123 (Technician)
echo  ========================================
echo.
echo  Press any key to STOP the server and exit.
pause >nul

REM Kill the backend
taskkill /FI "WindowTitle eq SSH Inventory API" /F >nul 2>&1
echo  Server stopped.
