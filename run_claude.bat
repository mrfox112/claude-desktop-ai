@echo off
echo 🚀 Starting Claude Desktop AI...
echo.

REM Check if virtual environment exists
if not exist "venv" (
    echo ❌ Virtual environment not found!
    echo Please run setup.ps1 first to install dependencies.
    pause
    exit /b 1
)

REM Activate virtual environment and run the application
call venv\Scripts\activate.bat
python claude_desktop.py

pause
