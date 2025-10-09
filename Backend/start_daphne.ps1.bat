@echo off
REM Activate the Python virtual environment and start Daphne server in PowerShell
cd /d %~dp0
cd ..\env
call Scripts\activate.bat
cd ..
cd Backend
powershell -NoExit -Command "daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application"
