#!/bin/bash
echo "========================================="
echo "  Mapa Interactivo de Red - Launcher"
echo "========================================="
echo ""
echo "Verificando dependencias..."
# pip3 install streamlit streamlit-image-coordinates pandas pillow --quiet --user >/dev/null 2>&1 || pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user >/dev/null 2>&1

echo ""
echo "Iniciando aplicación Streamlit..."
echo "La aplicación se abrirá automáticamente en tu navegador."
echo ""
echo "Para detener la aplicación, presiona Ctrl+C"
echo "========================================="
echo ""

python3 -m streamlit run app.py || python -m streamlit run app.py
