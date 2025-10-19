@echo off
echo =====================================
echo 🐾 Iniciando Mascota Live2D
echo =====================================

REM Activar entorno virtual
call venv\Scripts\activate

REM Ejecutar el main.py dentro de la carpeta
python live2d_mascota\main.py

REM Mantener la ventana abierta después de cerrar
echo.
echo 💤 Mascota cerrada. Presiona una tecla para salir.
pause >nul
