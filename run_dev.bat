@echo off
REM Change to script directory
cd /d "%~dp0"

REM Ensure python is available
where python >nul 2>&1
if errorlevel 1 (
  echo Python not found in PATH. Install Python and re-run this script.
  exit /b 1
)

REM Create venv if missing
if not exist "venv\Scripts\python.exe" (
  echo Creating virtual environment...
  python -m venv venv
)

REM Activate venv
call venv\Scripts\activate.bat

REM Install requirements if present
if exist requirements.txt (
  echo Installing Python dependencies...
  venv\Scripts\python.exe -m pip install --upgrade pip
  venv\Scripts\python.exe -m pip install -r requirements.txt
) else (
  echo No requirements.txt found — skipping pip install.
)

REM Start uvicorn
start "" venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000 --reload

timeout /t 2 /nobreak >nul
start "" "http://127.0.0.1:8000"

