@echo off
setlocal

echo =========================================
echo   Mapa Interactivo de Red - Launcher
echo =========================================
echo.

echo Verificando dependencias...
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PYCMD=%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        where py >nul 2>&1
        if errorlevel 1 (
            echo No se encontró Python en el PATH.
            echo Instala Python y vuelve a ejecutar este archivo.
            pause
            exit /b 1
        ) else (
            set "PYCMD=py -3"
        )
    ) else (
        set "PYCMD=python"
    )
)

if exist "%~dp0requirements.txt" (
    %PYCMD% -m pip install -r "%~dp0requirements.txt" --quiet --user >nul 2>&1
) else (
    %PYCMD% -m pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user >nul 2>&1
)
if errorlevel 1 (
    echo Error al instalar dependencias. Revisa tu instalación de Python.
    pause
    exit /b 1
)

echo.
echo Iniciando aplicación Streamlit...
echo La aplicación se abrirá automáticamente en tu navegador.
echo.
echo Para detener la aplicación, presiona Ctrl+C
echo =========================================
echo.

pushd "%~dp0"
%PYCMD% -m streamlit run app.py
popd

pause
