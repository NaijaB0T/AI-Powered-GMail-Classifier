@echo off
echo 🚀 Starting Inbox Clarity Development Environment

REM Check if .env files exist
if not exist "backend\.env" (
    echo ❌ Backend .env file not found. Please copy backend\.env.example to backend\.env and configure it.
    pause
    exit /b 1
)

if not exist "frontend\.env" (
    echo ❌ Frontend .env file not found. Please copy frontend\.env.example to frontend\.env and configure it.
    pause
    exit /b 1
)

echo 🔧 Starting backend server...
cd backend
start "Backend Server" python app.py

REM Wait a moment for backend to start
timeout /t 3 /nobreak > nul

echo ⚛️  Starting frontend server...
cd ..\frontend
start "Frontend Server" npm run dev

echo ✅ Development servers started!
echo 🔗 Frontend: http://localhost:5173
echo 🔗 Backend: http://localhost:5000
echo.
echo Press any key to stop all servers
pause > nul

echo 🛑 Stopping servers...
taskkill /f /im python.exe 2>nul
taskkill /f /im node.exe 2>nul
