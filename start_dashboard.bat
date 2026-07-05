@echo off
setlocal
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (
    echo Python 3 was not found. Install Python 3 and enable "Add Python to PATH".
    pause
    exit /b 1
)
python web\dashboard_server.py --open
pause
