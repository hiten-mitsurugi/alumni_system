@echo off
echo ========================================
echo Starting Alumni System for LAN Access
echo ========================================
echo.

REM Get local IP address
for /f "tokens=2 delims=:" %%a in ('ipconfig ^| findstr /c:"IPv4 Address"') do (
    set IP=%%a
    goto :done
)
:done
set IP=%IP:~1%
echo Your Local IP: %IP%
echo.
echo Frontend will be accessible at: http://%IP%:5173
echo Backend will be accessible at: http://%IP%:8000
echo.
echo ========================================
echo.

REM Start backend
start "Alumni Backend" cmd /k "cd Backend && python manage.py runserver 0.0.0.0:8000"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start frontend
start "Alumni Frontend" cmd /k "cd Frontend && npm run dev"

echo.
echo Both services started!
echo Share this URL with others on your network: http://%IP%:5173
echo.
pause
