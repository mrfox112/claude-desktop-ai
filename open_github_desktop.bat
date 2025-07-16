@echo off
echo 🚀 Opening Claude Desktop AI project in GitHub Desktop...

REM Check if GitHub Desktop is installed
if exist "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe" (
    echo ✅ GitHub Desktop found
    start "" "%LOCALAPPDATA%\GitHubDesktop\GitHubDesktop.exe" "%CD%"
) else (
    echo ❌ GitHub Desktop not found
    echo Please install GitHub Desktop from: https://desktop.github.com/
    pause
    exit /b 1
)

echo ✅ GitHub Desktop opened with project
pause
