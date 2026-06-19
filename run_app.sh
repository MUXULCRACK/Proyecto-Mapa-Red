#!/bin/bash
echo "========================================="
echo "   Mapa Interactivo de Red - Launcher"
echo "========================================="
echo ""
echo "Verificando dependencias..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" >/dev/null 2>&1 && pwd)"
cd "$SCRIPT_DIR"

# Detectar el comando de Python correcto disponible en el sistema
if command -v python3 &>/dev/null; then
    PYTHON_CMD="python3"
elif command -v python &>/dev/null; then
    PYTHON_CMD="python"
else
    echo "❌ Error: Python no está instalado o no se encuentra en el PATH."
    exit 1
fi

# Instalar dependencias capturando el estado de salida real
if [ -f "requirements.txt" ]; then
    $PYTHON_CMD -m pip install -r "requirements.txt" --quiet --user
else
    $PYTHON_CMD -m pip install streamlit streamlit-image-coordinates pandas pillow --quiet --user
fi

# Validar inmediatamente después de la acción de instalación
if [ $? -ne 0 ]; then
    echo "❌ Error al instalar dependencias. Verifica los permisos o tu conexión a internet."
    exit 1
fi

echo ""
echo "🚀 Iniciando aplicación Streamlit..."
echo "Si no se abre automáticamente, navega a http://localhost:8501"
echo ""
echo "Para detener la aplicación, presiona Ctrl+C"
echo "========================================="
echo ""

# Ejecutar Streamlit de forma directa
$PYTHON_CMD -m streamlit run app.py
