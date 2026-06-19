@echo off
setlocal

echo =========================================
echo   Mapa Interactivo de Red - Launcher
echo =========================================
echo.

echo Verificando dependencias...
set "PYCMD=python"
where py >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYCMD=py -3"
) else (
    where python >nul 2>&1
    if errorlevel 1 (
        echo No se encontró Python en el PATH.
        echo Instala Python y vuelve a ejecutar este archivo.
        pause
        exit /b 1
    )
)

echo Python encontrado: %PYCMD%

echo Intentando ejecutar Streamlit primero...

echo.
echo Iniciando aplicación Streamlit...
echo Si falta alguna dependencia, el script la instalará y reintentará.
echo.
echo Para detener la aplicación más tarde, presiona Ctrl+C.
echo =========================================
echo.

pushd "%~dp0"
%PYCMD% -m streamlit run app.py
set "LASTERROR=%ERRORLEVEL%"
popd

if %LASTERROR% neq 0 (
    echo.
    echo Streamlit no pudo iniciarse. Intentando instalar las dependencias necesarias...
    if exist "%~dp0requirements.txt" (
        %PYCMD% -m pip install -r "%~dp0requirements.txt" --user
    ) else (
        %PYCMD% -m pip install streamlit streamlit-image-coordinates pandas pillow --user
    )
    if errorlevel 1 (
        echo.
        echo Error al instalar dependencias con %PYCMD%.
        echo Revisa el mensaje anterior para identificar el problema.
        pause
        exit /b 1
    )
    echo.
    echo Dependencias instaladas. Reintentando ejecutar Streamlit...
    echo.
    echo Iniciando aplicación Streamlit...
    echo.
    pushd "%~dp0"
    %PYCMD% -m streamlit run app.py
    popd
)

pause
