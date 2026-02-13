@echo off
echo =========================================
echo   Mapa Interactivo de Red - Launcher
echo =========================================
echo.
echo Verificando dependencias...
C:\Users\Huawei\AppData\Local\Microsoft\WindowsApps\python.exe -m pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user >nul 2>&1

echo.
echo Iniciando aplicación Streamlit...
echo La aplicación se abrirá automáticamente en tu navegador.
echo.
echo Para detener la aplicación, presiona Ctrl+C
echo =========================================
echo.

C:\Users\Huawei\AppData\Local\Microsoft\WindowsApps\python.exe -m streamlit run app.py

pause
