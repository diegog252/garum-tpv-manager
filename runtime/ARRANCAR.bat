@echo off
title GARUM TPV Manager v8.3
color 0A
cls
if not exist "%~dp0python\python.exe" (
    color 0C
    echo.
    echo  No se encuentra Python en esta carpeta.
    echo  Ejecuta ARRANCAR.bat desde la carpeta donde instalaste
    echo  la app, o usa el acceso directo del Escritorio.
    echo.
    pause
    exit /b 1
)
echo.
echo  ================================
echo   GARUM TPV Manager v8.3
echo  ================================
echo.
echo  Arrancando servidor...
echo  Se abrira el navegador en:
echo  http://127.0.0.1:5050
echo.
echo  Para cerrar: Ctrl+C o cierra esta ventana
echo  ----------------------------------------
echo.
"%~dp0python\python.exe" "%~dp0app\server.py"
pause
