@echo off
echo ======================================
echo    PANEL DE CONTROL - ANIME ZONE ESP
echo ======================================
echo.
echo Iniciando servidor...
cd /d "C:\Users\Rafael\CascadeProjects\windsurf-project"

:: Abrir el navegador después de 3 segundos
start cmd /c "timeout /t 3 >nul && start http://localhost:5000"

:: Iniciar el servidor
python panel_server.py

echo.
echo Servidor detenido.
pause
