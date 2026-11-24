@echo off
chcp 65001 >nul
set PYTHONUTF8=1
cd /d "%~dp0"
start "" /min cmd /c "timeout /t 2 >nul & start http://localhost:8000"
python server.py
pause
