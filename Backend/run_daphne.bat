@echo off
REM Activate virtual environment
call env\Scripts\activate.bat

REM Run Daphne server
daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application

REM Pause to keep window open
pause