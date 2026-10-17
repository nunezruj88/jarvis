@echo off
cd /d "%~dp0"
where node >nul 2>nul
if errorlevel 1 (
 echo Instala Node.js 22 o posterior y vuelve a iniciar.
 pause
 exit /b 1
)
node server.mjs
pause
