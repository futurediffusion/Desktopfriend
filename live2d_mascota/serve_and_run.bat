@echo off
chcp 65001 >nul
title 🐾 Live2D Desktop Friend
color 0A

cd /d "%~dp0" || (
  echo [❌] No puedo acceder a la carpeta del proyecto
  pause & exit /b 1
)

echo.
echo ====================================
echo   🚀 Iniciando Desktop Friend
echo ====================================
echo.

REM === Verificar que existe web/index.html ===
if not exist "web\index.html" (
  echo [❌] Falta: web\index.html
  echo ➡️  Asegúrate de tener la carpeta web con el Live2D
  pause & exit /b 1
)

REM === Activar entorno virtual ===
if exist "venv\Scripts\activate.bat" (
  echo [✓] Activando entorno virtual...
  call venv\Scripts\activate
) else (
  echo [⚠️] No hay entorno virtual. Ejecuta start.bat primero
  pause & exit /b 1
)

REM === Levantar servidor HTTP en segundo plano ===
echo [✓] Iniciando servidor Live2D en http://127.0.0.1:5500
pushd web
start /B "" python -m http.server 5500 --bind 127.0.0.1 >nul 2>&1
popd

REM Espera a que levante el servidor
timeout /t 2 >nul

REM === Ejecutar aplicación PySide6 ===
echo [✓] Abriendo ventana transparente...
echo.
python live2d_mascota\main.py

REM === Limpiar al cerrar ===
echo.
echo [✓] Cerrando servidor...
taskkill /F /IM python.exe /FI "WINDOWTITLE eq Live2D-Web-Server*" >nul 2>&1

echo.
echo ====================================
echo   💤 Mascota cerrada correctamente
echo ====================================
pause