@echo off
setlocal

rem === ir a la carpeta del proyecto (donde está este .bat) ===
cd /d "%~dp0" || (echo [ERROR] No puedo cambiar a "%~dp0" & pause & exit /b 1)

rem === comprobar que existe \web\index.html ===
if not exist "web\index.html" (
  echo [ERROR] No existe "%~dp0web\index.html"
  pause & exit /b 1
)

rem === levantar servidor HTTP sirviendo la carpeta web ===
pushd "web" || (echo [ERROR] No puedo entrar a "%~dp0web" & pause & exit /b 1)
start "Live2D-Web-Server" cmd /c python -m http.server 5500 --bind 127.0.0.1
popd

rem pequeña espera para que levante
timeout /t 1 >nul

rem === lanzar la app Python ===
python "%~dp0main.py"

endlocal
