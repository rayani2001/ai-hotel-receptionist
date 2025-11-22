@echo off
cd /d "%~dp0"
echo ========================================
echo AI HOTEL RECEPTIONIST SYSTEM
echo ========================================
echo.
echo Starting server...
echo.
echo Access the application at:
echo - Main Page: http://localhost:8000
echo - Chat UI:   http://localhost:8000/api/chat-ui
echo - Voice UI:  http://localhost:8000/api/voice-ui
echo - API Docs:  http://localhost:8000/docs
echo.
echo Press CTRL+C to stop the server
echo ========================================
echo.
python main.py
pause
