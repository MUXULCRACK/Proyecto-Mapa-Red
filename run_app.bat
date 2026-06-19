@echo off
setlocal

echo =========================================
echo   Mapa Interactivo de Red - Launcher
echo =========================================
echo.

echo Buscando una instalacion de Python compatible...

set "PYCMD="

:: 1. Probar comandos en el PATH que tengan pip
call :try_cmd "py -3" && goto :found
call :try_cmd "py" && goto :found
call :try_cmd "python" && goto :found
call :try_cmd "python3" && goto :found

:: 2. Probar rutas comunes del usuario (Windows App Store)
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    call :try_path "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" && goto :found
)
if exist "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" (
    call :try_path "%USERPROFILE%\AppData\Local\Microsoft\WindowsApps\python.exe" && goto :found
)

:: 3. Probar carpetas de instalacion de Python de un solo usuario (Programs)
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        call :try_path "%%d\python.exe" && goto :found
    )
)

:: 4. Probar carpetas en la raiz o Program Files
for /d %%d in ("C:\Python*") do (
    if exist "%%d\python.exe" (
        call :try_path "%%d\python.exe" && goto :found
    )
)
for /d %%d in ("C:\Program Files\Python*") do (
    if exist "%%d\python.exe" (
        call :try_path "%%d\python.exe" && goto :found
    )
)
for /d %%d in ("C:\Program Files (x86)\Python*") do (
    if exist "%%d\python.exe" (
        call :try_path "%%d\python.exe" && goto :found
    )
)

:: Fallback: si no se encontro Python con pip, al menos buscar uno que funcione
call :try_any_cmd "py -3" && goto :found
call :try_any_cmd "py" && goto :found
call :try_any_cmd "python" && goto :found
if exist "%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe" (
    set "PYCMD="%LOCALAPPDATA%\Microsoft\WindowsApps\python.exe""
    goto :found
)
for /d %%d in ("%LOCALAPPDATA%\Programs\Python\Python*") do (
    if exist "%%d\python.exe" (
        set "PYCMD="%%d\python.exe""
        goto :found
    )
)

echo No se encontro ninguna instalacion de Python compatible.
echo Instala Python (asegurate de marcar la casilla "Add Python to PATH" y de incluir pip) y vuelve a intentar.
pause
exit /b 1

:found
echo Python detectado: %PYCMD%
echo.
echo Intentando ejecutar Streamlit primero...
echo.
echo Iniciando aplicacion Streamlit...
echo Si falta alguna dependencia, el script la instalara y reintentara.
echo.
echo Para detener la aplicacion mas tarde, presiona Ctrl+C.
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
    echo Iniciando aplicacion Streamlit...
    echo.
    pushd "%~dp0"
    %PYCMD% -m streamlit run app.py
    popd
)

pause
exit /b 0

:try_cmd
%~1 -c "import pip" >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYCMD=%~1"
    exit /b 0
)
exit /b 1

:try_path
"%~1" -c "import pip" >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYCMD="%~1""
    exit /b 0
)
exit /b 1

:try_any_cmd
%~1 --version >nul 2>&1
if %ERRORLEVEL%==0 (
    set "PYCMD=%~1"
    exit /b 0
)
exit /b 1
