@echo off
echo Starting Alumni System Development Environment...

REM Start Frontend in new window
echo Starting Frontend...
start "Alumni Frontend" cmd /k "cd frontend && npm run dev"

REM Wait a moment
timeout /t 3 /nobreak > nul

REM Start Backend in new window
echo Starting Backend...
start "Alumni Backend" cmd /k "cd backend && .\env\Scripts\Activate && daphne -b 0.0.0.0 -p 8000 alumni_system.asgi:application"

echo Both services are starting...
echo Frontend: http://localhost:5173
echo Backend: http://localhost:8000
pause