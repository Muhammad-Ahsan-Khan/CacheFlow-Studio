@echo off
setlocal
cd /d "%~dp0"
python web\console_runner.py --policy fifo --accesses 30
pause
