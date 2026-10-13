@echo off
echo ====================================================================
echo  EthicPrivAI: Privacy-Preserving Data Mining for Ethical AI Systems
echo ====================================================================
echo.

echo [1/2] Starting EthicPrivAI FastAPI Server on http://localhost:8000 ...
start "EthicPrivAI Backend" cmd /k ".venv\Scripts\python.exe run_server.py"

echo [2/2] Starting EthicPrivAI Interactive React Dashboard on http://localhost:5173 ...
cd frontend
start "EthicPrivAI Frontend" cmd /k "npm run dev"

echo.
echo Both servers are launching!
echo Backend:  http://localhost:8000/docs
echo Frontend: http://localhost:5173
echo ====================================================================
