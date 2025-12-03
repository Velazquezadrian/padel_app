@echo off
cd /d "%~dp0"

REM Crear script temporal de PowerShell
echo $psi = New-Object System.Diagnostics.ProcessStartInfo > %TEMP%\iniciar_padel.ps1
echo $psi.FileName = '%~dp0venv\Scripts\python.exe' >> %TEMP%\iniciar_padel.ps1
echo $psi.Arguments = '%~dp0app_escritorio.py' >> %TEMP%\iniciar_padel.ps1
echo $psi.WorkingDirectory = '%~dp0' >> %TEMP%\iniciar_padel.ps1
echo $psi.WindowStyle = [System.Diagnostics.ProcessWindowStyle]::Hidden >> %TEMP%\iniciar_padel.ps1
echo $psi.CreateNoWindow = $true >> %TEMP%\iniciar_padel.ps1
echo [System.Diagnostics.Process]::Start($psi) ^| Out-Null >> %TEMP%\iniciar_padel.ps1

REM Ejecutar PowerShell en modo oculto
powershell -WindowStyle Hidden -ExecutionPolicy Bypass -File %TEMP%\iniciar_padel.ps1

REM Limpiar
del %TEMP%\iniciar_padel.ps1

exit
