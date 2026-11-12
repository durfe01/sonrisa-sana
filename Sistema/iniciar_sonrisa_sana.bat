@echo off
chcp 65001 >nul
cd /d "%~dp0"

echo ============================================================
echo   Clinica Odontologica "Sonrisa Sana" - Iniciando Sistema
echo ============================================================
echo.
echo   Servidor web: http://127.0.0.1:8000
echo   Para detener el sistema cierra esta ventana o presiona Ctrl+C
echo.

start "" /b cmd /c "timeout /t 2 /nobreak >nul && start http://127.0.0.1:8000"
python run_server.py

if errorlevel 1 (
    echo.
    echo [ERROR] No se pudo iniciar el servidor. Revisa el mensaje anterior.
    pause
)
