@echo off
setlocal EnableExtensions
REM === Ruta absoluta a la carpeta donde está este BAT ===
set "ROOT=%~dp0"

echo =====================================
echo 🐾 Iniciando Mascota Live2D
echo =====================================

REM --- Activar entorno virtual (Windows) ---
if exist "%ROOT%venv\Scripts\activate.bat" (
  call "%ROOT%venv\Scripts\activate.bat"
) else (
  echo ⚠️ No se encontró venv\Scripts\activate.bat
  echo    Crea el entorno:  python -m venv venv  &&  venv\Scripts\pip install -r requirements.txt
  goto :END
)

REM --- Iniciar servidor web primero (en live2d_mascota\web) ---
if exist "%ROOT%live2d_mascota\web" (
  echo 🚀 Iniciando servidor web en puerto 5500...
  start "" cmd /c "pushd "%ROOT%live2d_mascota\web" && python -m http.server 5500"
) else (
  echo ⚠️ No existe la carpeta "%ROOT%live2d_mascota\web"
  goto :END
)

REM --- Esperar un poco para que levante el server ---
timeout /t 2 >nul

REM --- Ejecutar la mascota (main.py) ---
if exist "%ROOT%live2d_mascota\main.py" (
  echo 🐍 Ejecutando live2d_mascota\main.py ...
  start "" cmd /c "pushd "%ROOT%live2d_mascota" && python main.py"
) else (
  echo ⚠️ No existe "%ROOT%live2d_mascota\main.py"
  goto :END
)

:END
echo.
echo 💤 Mascota cerrada. Presiona una tecla para salir.
pause >nul
