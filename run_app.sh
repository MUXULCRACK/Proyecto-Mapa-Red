#!/bin/bash
echo "========================================="
echo "  Mapa Interactivo de Red - Launcher"
echo "========================================="
echo ""
echo "Verificando dependencias..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"

if [ -f "$SCRIPT_DIR/requirements.txt" ]; then
  python3 -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet --user >/dev/null 2>&1 || python -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet --user >/dev/null 2>&1
else
  python3 -m pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user >/dev/null 2>&1 || python -m pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user >/dev/null 2>&1
fi

if [ $? -ne 0 ]; then
  echo "Error al instalar dependencias. Revisa tu instalación de Python."
  exit 1
fi

echo ""
echo "Iniciando aplicación Streamlit..."
echo "La aplicación se abrirá automáticamente en tu navegador."
echo ""
echo "Para detener la aplicación, presiona Ctrl+C"
echo "========================================="
echo ""

cd "$SCRIPT_DIR"
python3 -m streamlit run app.py || python -m streamlit run app.py
