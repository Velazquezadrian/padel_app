@echo off
title Sistema de Turnos Padel - App Escritorio
color 0A

cls
echo.
echo ========================================
echo   APP DE ESCRITORIO - TURNOS PADEL
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

REM Iniciar aplicacion
cls
echo.
echo ========================================
echo   ABRIENDO APLICACION
echo ========================================
echo.
echo Ventana independiente (sin navegador)
echo.
echo Para CERRAR: Cierra la ventana
echo ========================================
echo.

venv\Scripts\python.exe app_escritorio.py

pause
