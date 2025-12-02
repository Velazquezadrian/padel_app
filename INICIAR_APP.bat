@echo off
title Sistema de Turnos Padel - Navegador
color 0A

cls
echo.
echo ========================================
echo   SISTEMA DE TURNOS - VERSION WEB
echo ========================================
echo.

REM Verificar Python
python --version >nul 2>&1
if errorlevel 1 (
    color 0C
    echo ERROR: Python no instalado
    echo Descarga: https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Instalar si es primera vez
if not exist "venv" (
    echo Instalando... espera 1-2 minutos
    python -m venv venv
    venv\Scripts\python.exe -m pip install -q --upgrade pip
    venv\Scripts\python.exe -m pip install -q -r requirements.txt
    echo Listo!
    echo.
)

REM Iniciar
cls
echo.
echo ========================================
echo   INICIANDO EN NAVEGADOR
echo ========================================
echo.
echo Abriendo: http://localhost:5000
echo.
echo Presiona Ctrl+C para detener
echo ========================================
echo.

start http://localhost:5000
venv\Scripts\python.exe -c "from app import app; app.run(host='0.0.0.0', port=5000, debug=False)"
