@echo off
setlocal enabledelayedexpansion
title GARUM TPV Manager - Instalador
color 0A
cls

echo.
echo  ============================================================
echo   GARUM TPV Manager v7.6 - Instalador para Windows 64 bits
echo  ============================================================
echo.
echo  Instalador OFFLINE: solo copia y extrae ficheros.
echo  Python y las librerias van incluidos en el paquete.
echo  NO necesita conexion a internet. Tarda menos de 1 minuto.
echo.

REM -- Verificar administrador -------------------------------------------------
net session >nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  [ERROR] Ejecuta este fichero como Administrador.
    echo  Clic derecho sobre INSTALAR.bat y "Ejecutar como administrador"
    echo.
    pause
    exit /b 1
)

REM -- Comprobar que el paquete esta completo ----------------------------------
if not exist "%~dp0runtime\python-embed.zip" (
    color 0C
    echo.
    echo  [ERROR] No se encuentra runtime\python-embed.zip
    echo  Extrae el ZIP COMPLETO antes de ejecutar el instalador.
    echo.
    pause
    exit /b 1
)
if not exist "%~dp0runtime\ARRANCAR.bat" (
    color 0C
    echo.
    echo  [ERROR] No se encuentra runtime\ARRANCAR.bat
    echo  Extrae el ZIP COMPLETO antes de ejecutar el instalador.
    echo.
    pause
    exit /b 1
)

REM -- Ruta fija: C:\GARUMTOOLS\GarumTPV (sin preguntar) -----------------------
set "INST=C:\GARUMTOOLS\GarumTPV"
echo.
echo  Se instalara en: !INST!
timeout /t 1 >nul
cls
set "PY=!INST!\python"
set "APP=!INST!\app"

echo  Creando carpetas en !INST! ...
if not exist "!INST!"             mkdir "!INST!"
if not exist "!APP!"              mkdir "!APP!"
if not exist "!APP!\templates"    mkdir "!APP!\templates"

echo  Copiando ficheros de la aplicacion...
copy "%~dp0app\server.py"                  "!APP!\server.py"         >nul
copy "%~dp0app\templates\index.html"       "!APP!\templates\index.html"     >nul
copy "%~dp0app\templates\diagnostico.html" "!APP!\templates\diagnostico.html" >nul

if not exist "!APP!\server.py" (
    color 0C
    echo  [ERROR] No se encontraron los ficheros de la app.
    echo  Asegurate de que INSTALAR.bat esta dentro de la carpeta
    echo  garum_tpv_manager junto a las carpetas app\ y runtime\
    pause
    exit /b 1
)
echo  [OK] Ficheros de la app copiados.
echo.

REM -- Instalar Python embebido (extraer el zip incluido) ----------------------
echo  [1/2] Instalando Python 3.11 embebido (incluido en el paquete)...
echo        Espera unos segundos...
echo.

if exist "!PY!" rmdir /s /q "!PY!"
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "Expand-Archive -Path '%~dp0runtime\python-embed.zip' -DestinationPath '!PY!' -Force"

if not exist "!PY!\python.exe" (
    color 0C
    echo.
    echo  [ERROR] No se pudo preparar Python.
    echo  El fichero runtime\python-embed.zip puede estar danado;
    echo  vuelve a extraer el ZIP completo e intentalo de nuevo.
    pause
    exit /b 1
)
echo  [OK] Python listo en !PY!
echo.

REM -- Instalar el lanzador ARRANCAR.bat (se copia, no se genera) --------------
echo  [2/2] Instalando el lanzador...
copy "%~dp0runtime\ARRANCAR.bat" "!INST!\ARRANCAR.bat" >nul
if not exist "!INST!\ARRANCAR.bat" (
    color 0C
    echo.
    echo  [ERROR] No se pudo copiar ARRANCAR.bat
    pause
    exit /b 1
)
echo  [OK] Lanzador instalado.
echo.

REM -- Acceso directo en el escritorio -----------------------------------------
powershell -NoProfile -ExecutionPolicy Bypass -Command ^
 "$ws=New-Object -ComObject WScript.Shell; $s=$ws.CreateShortcut([Environment]::GetFolderPath('CommonDesktopDirectory')+'\GARUM TPV Manager.lnk'); $s.TargetPath='!INST!\ARRANCAR.bat'; $s.WorkingDirectory='!INST!'; $s.Description='GARUM TPV Manager v7.6'; $s.Save()"

REM -- Listo -------------------------------------------------------------------
color 0A
cls
echo.
echo  ============================================================
echo   INSTALACION COMPLETADA
echo  ============================================================
echo.
echo   Carpeta: !INST!
echo   Acceso directo "GARUM TPV Manager" creado en el Escritorio.
echo.
echo   PARA ABRIR LA APP:
echo   Doble clic en "GARUM TPV Manager" del Escritorio
echo   (o ejecuta: !INST!\ARRANCAR.bat)
echo.
echo  ============================================================
echo.
pause
