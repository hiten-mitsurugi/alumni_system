@echo off
echo Starting Celery Worker for Alumni System...
echo.
cd /d "%~dp0"
.\env\Scripts\celery.exe -A alumni_system worker -l info --pool=solo
