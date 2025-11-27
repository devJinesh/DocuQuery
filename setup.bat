@echo off
echo ================================================
echo DocuQuery Application - Quick Setup
echo ================================================
echo.

REM Check Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo Please install Python 3.9 or higher from https://www.python.org/
    pause
    exit /b 1
)
echo [OK] Python found

REM Check Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js is not installed or not in PATH
    echo Please install Node.js 16+ from https://nodejs.org/
    pause
    exit /b 1
)
echo [OK] Node.js found

echo.
echo Setting up backend...
cd backend

REM Create virtual environment
if not exist venv (
    echo Creating virtual environment...
    python -m venv venv
)

REM Activate and install
echo Installing backend dependencies...
call venv\Scripts\activate.bat
pip install -r requirements.txt

REM Copy .env if not exists
if not exist .env (
    echo Creating .env file...
    copy .env.example .env
    echo [NOTE] Please edit backend\.env with your settings
)

cd ..

echo.
echo Setting up frontend...
cd frontend

REM Install npm packages
if not exist node_modules (
    echo Installing frontend dependencies...
    call npm install
)

REM Create .env if not exists
if not exist .env (
    echo REACT_APP_API_URL=http://localhost:8000/api > .env
)

cd ..

echo.
echo ================================================
echo Setup Complete!
echo ================================================
echo.
echo Next steps:
echo 1. Install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki
echo 2. Update backend\.env with Tesseract path and other settings
echo 3. Run start.bat to start the application
echo.
pause
