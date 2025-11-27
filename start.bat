@echo off
echo ================================================
echo Starting DocuQuery Application
echo ================================================
echo.

REM Start backend
echo Starting backend server...
start "DocuQuery Backend" cmd /k "cd backend && venv\Scripts\python.exe main.py"

REM Wait a bit for backend to start
timeout /t 5 /nobreak >nul

REM Start frontend
echo Starting frontend server...
start "DocuQuery Frontend" cmd /k "cd frontend && npm start"

echo.
echo ================================================
echo Application Starting!
echo ================================================
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo.
echo Press any key to stop all servers...
pause >nul

REM Kill processes
taskkill /FI "WindowTitle eq DocuQuery Backend*" /T /F >nul 2>&1
taskkill /FI "WindowTitle eq DocuQuery Frontend*" /T /F >nul 2>&1

echo Servers stopped.
