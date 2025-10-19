@echo off
echo =====================================
echo  🐍 Configurando entorno Mascota Live2D
echo =====================================

REM Crea el entorno virtual
python -m venv venv

REM Activa el entorno
call venv\Scripts\activate

REM Instala PySide6
pip install PySide6

REM Crea la carpeta del proyecto
mkdir live2d_mascota

REM Crea main.py
echo from PySide6.QtCore import QUrl> live2d_mascota\main.py
echo from PySide6.QtWidgets import QApplication>> live2d_mascota\main.py
echo from PySide6.QtWebEngineWidgets import QWebEngineView>> live2d_mascota\main.py
echo import sys>> live2d_mascota\main.py
echo.>> live2d_mascota\main.py
echo app = QApplication(sys.argv)>> live2d_mascota\main.py
echo.>> live2d_mascota\main.py
echo view = QWebEngineView()>> live2d_mascota\main.py
echo view.setWindowTitle("Mascota Live2D")>> live2d_mascota\main.py
echo view.load(QUrl.fromLocalFile("index.html"))  ^# carga el HTML local>> live2d_mascota\main.py
echo view.setFixedSize(400, 400)  ^# tamaño base>> live2d_mascota\main.py
echo view.show()>> live2d_mascota\main.py
echo.>> live2d_mascota\main.py
echo sys.exit(app.exec())>> live2d_mascota\main.py

REM Crea index.html
(
echo ^<!DOCTYPE html^>
echo ^<html lang="es"^>
echo ^<head^>
echo     ^<meta charset="UTF-8" /^>
echo     ^<title>Mascota^</title^>
echo ^</head^>
echo ^<body style="background: #222; color: white; display:flex; align-items:center; justify-content:center;"^>
echo     ^<h2^>Hola, soy tu futura mascota 😄^</h2^>
echo ^</body^>
echo ^</html^>
) > live2d_mascota\index.html

echo =====================================
echo ✅ Proyecto creado correctamente
echo Para ejecutarlo:
echo 1. call venv\Scripts\activate
echo 2. cd live2d_mascota
echo 3. python main.py
echo =====================================

pause
