@echo off
setlocal

REM Run from this script's directory (handles spaces in path)
cd /d "%~dp0"

echo Starting EMS backend and frontend...

REM Start FastAPI backend in a new terminal window
start "EMS Backend" cmd /k "if exist .venv\Scripts\activate.bat (call .venv\Scripts\activate.bat) && uvicorn main:app --reload --host 127.0.0.1 --port 8000"

REM Start React frontend in a new terminal window
start "EMS Frontend" cmd /k "cd frontend && npm run dev -- --host 127.0.0.1 --port 5173"

REM Give servers a moment to boot before opening browser tabs
timeout /t 3 /nobreak >nul

REM Open EMS app and API docs
start "" "http://127.0.0.1:5173"
start "" "http://127.0.0.1:8000/docs"
start "" "http://127.0.0.1:8000/chatbot/faqs"

echo.
echo Backend:  http://127.0.0.1:8000/docs
echo Chatbot:  http://127.0.0.1:8000/chatbot/faqs
echo Frontend: http://127.0.0.1:5173
