@echo off
chcp 65001 >nul
cd /d "%~dp0java"
javac -encoding UTF-8 *.java || (echo Java JDK 17+ kerek & pause & exit /b)
java -Dstdout.encoding=UTF-8 -Dstdin.encoding=UTF-8 -Dfile.encoding=UTF-8 SmartphoneCatalog
pause
