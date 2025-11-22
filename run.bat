@echo off
REM AI Hotel Receptionist - Quick Start Script for Windows

echo ==========================================
echo AI Hotel Receptionist - Starting...
echo ==========================================
echo.

REM Check if virtual environment is activated
if not defined VIRTUAL_ENV (
    echo WARNING: Virtual environment not activated!
    echo Please run: venv\Scripts\activate
    echo.
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo WARNING: .env file not found!
    echo Please copy .env.example to .env and configure it:
    echo   copy .env.example .env
    echo.
    pause
    exit /b 1
)

REM Check if database exists
if not exist hotel_receptionist.db (
    echo Database not found. Initializing...
    python scripts\init_database.py
    echo.
)

REM Change to the script's directory
cd /d "%~dp0"

REM Start the application
echo Starting AI Hotel Receptionist...
echo Current directory: %CD%
echo.
echo Access the application at:
echo   - Main Page: http://localhost:8000
echo   - Chat UI: http://localhost:8000/api/chat-ui
echo   - API Docs: http://localhost:8000/docs
echo.
echo Press Ctrl+C to stop the server
echo.

python main.py
pause
