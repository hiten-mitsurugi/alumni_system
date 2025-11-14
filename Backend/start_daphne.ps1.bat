@echo off
REM Activate the Python virtual environment and start Daphne server in PowerShell
cd /d %~dp0
if exist env\Scripts\activate.bat (
    call env\Scripts\activate.bat
) else (
    echo Virtual environment not found at Backend\env
    echo Please create it with: python -m venv env
    pause
    exit /b 1
)
powershell -NoExit -Command "daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application"
