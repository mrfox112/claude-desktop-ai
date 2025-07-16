@echo off
echo 🚀 Starting Claude Desktop AI...

REM Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Virtual environment not found!
    echo Please run setup.ps1 first
    pause
    exit /b 1
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Check if .env file exists
if not exist ".env" (
    echo ❌ .env file not found!
    echo Please add your API key to the .env file
    pause
    exit /b 1
)

REM Run the desktop application
python claude_desktop.py

REM Deactivate virtual environment
call venv\Scripts\deactivate.bat

pause
