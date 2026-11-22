@echo off
chcp 65001 >nul
cd /d "%~dp0java"
javac -encoding UTF-8 *.java || (echo Java JDK 17+ kerek & pause & exit /b)
start "" /min cmd /c "timeout /t 2 >nul & start http://localhost:8080"
java -Dstdout.encoding=UTF-8 -Dfile.encoding=UTF-8 SmartphoneServer
pause
