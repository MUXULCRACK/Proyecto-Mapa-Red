# 🗺️ Mapa Interactivo de Red – Empresa

Aplicación web interactiva construida con **Streamlit** para visualizar, registrar y gestionar puntos de red sobre un croquis de instalaciones. Permite ubicar equipos en un mapa, asociarlos a racks, switches y patch panels, y hacer seguimiento del estado de cada conexión.

---

## 🚀 Cómo ejecutar

**En Windows:**
Haz doble clic en el archivo **`run_app.bat`**.

**En Mac o Linux:**
1. Abre una terminal en la carpeta del proyecto.
2. Da permisos de ejecución al script (solo la primera vez): `chmod +x run_app.sh`
3. Ejecuta el script: `./run_app.sh`

> Esto instalará las dependencias necesarias automáticamente y abrirá la aplicación en tu navegador.

Para detener la aplicación, presiona `Ctrl+C` en la ventana de comandos/terminal donde se está ejecutando.

---

## 📋 Requisitos

- Python instalado en el sistema
- Conexión a internet (solo la primera vez para instalar dependencias)

Dependencias (se instalan automáticamente):

```
streamlit
streamlit-image-coordinates
pandas
pillow
```

---

## 🗂️ Estructura de archivos

| Archivo | Descripción |
|---|---|
| `app.py` | Código principal de la aplicación |
| `croquis.png` | Imagen base del mapa de instalaciones |
| `network_points.csv` | Puntos de red registrados |
| `deleted_points.csv` | Historial de puntos eliminados |
| `catalogo_racks.csv` | Catálogo de racks disponibles |
| `catalogo_switch.csv` | Switches por rack |
| `catalogo_patch.csv` | Patch panels por rack |
| `catalogo_lugares.csv` | Catálogo de lugares/áreas |
| `catalogo_dependencias.csv` | Catálogo de dependencias/departamentos |
| `run_app.bat` | Lanzador de la aplicación (Windows) |
| `run_app.sh` | Lanzador de la aplicación (Mac/Linux) |
| `requirements.txt` | Dependencias de Python |

---

## 🎯 Funcionalidades

### Mapa 1 – Agregar puntos
- Haz clic sobre el croquis para capturar coordenadas
- Selecciona el **estado** del punto de red
- Completa los datos: Rack, Switch, Patch Panel, puertos, Dependencia, Lugar y Comentarios
- El nombre del punto puede repetirse hasta **2 veces**

### Mapa 2 – Visualización y filtros
- Visualiza todos los puntos sobre el croquis con colores según su estado
- Filtra por: **Rack y Equipo**, **Lugar** o **Dependencia**
- Haz clic sobre un punto para ver sus detalles completos
- Modo **Re-ubicación**: mueve un punto a una nueva posición en el mapa

### Listado de puntos
- Lista todos los puntos filtrados con sus datos
- Botón **✏️** para editar cualquier campo del punto
- Botón **🗑️** para eliminar (se guarda en el historial)

### Historial de eliminados 🕒
- Actívalo desde la barra lateral
- Muestra los últimos 3 puntos eliminados en el mapa (en gris)
- Haz clic sobre un punto gris para ver quién lo eliminó y cuándo

---

## 🎨 Estados de un punto

| Color | Estado | Descripción |
|---|---|---|
| 🟢 Verde | Funcionando y ubicado | Equipo identificado, conectado y operativo |
| 🟩 Verde Oscuro | Funcionando directos | Punto directo (sin patch panel), identificado y operativo |
| 🔴 Rojo | No sirve y ubicado | Equipo identificado pero sin funcionamiento |
| 🟠 Naranja | Ubicado sin switch | Equipo ubicado, sin conexión a switch registrada |
| 🟣 Morado | Ponchado erróneo | Equipo ubicado, pero con un ponchado incorrecto (sin información del switch) |
| 🔵 Azul | Sin identificar y funcionando | Equipo funcionando pero aún no identificado |
| 🟡 Amarillo | Funcionando sin usar | Puntos ubicados con conexión al switch, sin uso actual pero funcionales (sirve) |

---
Añadir amarillo y verde oscuro

## ⚙️ Catálogos (barra lateral)

Desde la barra lateral se pueden agregar entradas a los catálogos:
- **Rack** – Nombre del gabinete
- **Switch** – Asociado a un rack
- **Patch Panel** – Asociado a un rack
- **Lugar** – Área o zona física
- **Dependencia** – Departamento responsable CON VLAN
