@echo off
REM Multi Desk Backend Startup Script for Windows

echo 🚀 Starting Multi Desk Backend...

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python is not installed. Please install Python 3.8 or higher.
    pause
    exit /b 1
)

REM Navigate to backend directory
cd /d "%~dp0"

REM Create virtual environment if it doesn't exist
if not exist "venv" (
    echo 📦 Creating virtual environment...
    python -m venv venv
)

REM Activate virtual environment
echo 🔧 Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo 📥 Installing dependencies...
pip install -r requirements.txt

REM Check if .env file exists
if exist ".env" (
    echo 🔐 Environment variables loaded from .env file
) else (
    echo ⚠️  .env file not found. Please create one with your configuration.
)

REM Start the FastAPI server
echo 🌐 Starting FastAPI server on http://localhost:8000
echo 📧 Email service ready for OTP verification
echo 🔑 Authentication system ready...
echo.
echo Press Ctrl+C to stop the server
echo.

uvicorn main:app --host 0.0.0.0 --port 8000 --reload

pause