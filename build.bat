@echo off
echo ========================================
echo    Compilando Padel App
echo ========================================
echo.

REM Activar entorno virtual
call venv\Scripts\activate.bat

echo [1/3] Instalando PyInstaller...
pip install pyinstaller

echo.
echo [2/3] Compilando aplicacion...
pyinstaller --name="PadelApp" ^
    --onefile ^
    --windowed ^
    --add-data "templates;templates" ^
    --add-data "static;static" ^
    --hidden-import=webview ^
    --hidden-import=flask ^
    --clean ^
    app.py

echo.
echo [3/3] Limpiando archivos temporales...
rmdir /s /q build

echo.
echo ========================================
echo    Compilacion completada!
echo    Ejecutable en: dist\PadelApp.exe
echo ========================================
pause
