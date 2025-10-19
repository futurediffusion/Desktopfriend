@echo off
chcp 65001 >nul
title 🛠️ Configuración Live2D Desktop Friend
color 0B

echo.
echo ====================================
echo   🐍 Configurando entorno
echo ====================================
echo.

REM === Verificar Python ===
python --version >nul 2>&1
if errorlevel 1 (
  echo [❌] Python no encontrado. Instálalo primero:
  echo     https://www.python.org/downloads/
  pause & exit /b 1
)

REM === Crear entorno virtual si no existe ===
if not exist "venv\" (
  echo [✓] Creando entorno virtual...
  python -m venv venv
) else (
  echo [✓] Entorno virtual ya existe
)

REM === Activar entorno ===
call venv\Scripts\activate

REM === Instalar PySide6 ===
echo [✓] Instalando PySide6...
pip install --quiet PySide6

REM === Verificar estructura ===
if not exist "live2d_mascota\" (
  echo [❌] Falta carpeta: live2d_mascota
  pause & exit /b 1
)

if not exist "web\index.html" (
  echo [❌] Falta carpeta: web (con tus modelos Live2D)
  echo.
  echo ➡️  Descarga los modelos de:
  echo     https://www.live2d.com/en/download/sample-data/
  pause & exit /b 1
)

echo.
echo ====================================
echo   ✅ Configuración completa
echo ====================================
echo.
echo 📝 Ahora ejecuta:
echo     serve_and_run.bat
echo.
pause