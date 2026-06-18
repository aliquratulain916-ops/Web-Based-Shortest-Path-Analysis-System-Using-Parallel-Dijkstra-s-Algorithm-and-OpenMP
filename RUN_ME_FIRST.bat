@echo off
REM ============================================================
REM Dijkstra's Algorithm - Automatic Setup Script
REM Run this first on Windows
REM ============================================================

echo.
echo ============================================================
echo DIJKSTRA'S SHORTEST PATH - SETUP WIZARD
echo ============================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo.
    echo Please install Python 3.8+ from: https://www.python.org/downloads/
    echo IMPORTANT: Check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)

echo ✓ Python found
python --version
echo.

REM Install dependencies
echo Installing dependencies... (this may take 2-3 minutes)
echo.
pip install -r requirements.txt --quiet

if errorlevel 1 (
    echo ERROR: Failed to install dependencies
    echo Try running: pip install --upgrade pip
    pause
    exit /b 1
)

echo.
echo ✓ Dependencies installed successfully!
echo.
echo ============================================================
echo SETUP COMPLETE - Starting Application
echo ============================================================
echo.

REM Run the application
python main.py

REM Keep window open if there's an error
if errorlevel 1 (
    echo.
    echo ERROR: Application failed
    pause
)
