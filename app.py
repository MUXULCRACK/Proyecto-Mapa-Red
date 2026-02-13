import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import pandas as pd
import os

# ===========================================
# CONFIGURACIÓN INICIAL
# ===========================================
st.set_page_config(layout="wide")
st.title("Mapa Interactivo de Red – Empresa")

CSV_FILE = "network_points.csv"
IMAGE_FILE = "croquis.png"

CAT_RACK = "catalogo_racks.csv"
CAT_SWITCH = "catalogo_switch.csv"
CAT_PATCH = "catalogo_patch.csv"
CAT_LUGAR = "catalogo_lugares.csv"

# ===========================================
# CREAR ARCHIVOS SI NO EXISTEN O REPARAR SI ESTÁN CORRUPTOS
# ===========================================
def create_or_fix_csv(filename, columns):
    """Crea o repara un archivo CSV con las columnas especificadas"""
    try:
        # Intentar leer el archivo
        df = pd.read_csv(filename)
        # Verificar que tenga las columnas correctas
        if list(df.columns) != columns:
            raise ValueError("Columnas incorrectas")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError):
        # Si no existe, está vacío o tiene columnas incorrectas, crearlo
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        return df

# ===========================================
# CARGAR DATOS
# ===========================================
df = create_or_fix_csv(CSV_FILE, [
    "x","y","tipo","identificador","color",
    "rack","puerto","dependencia","lugar"
])

# Eliminar duplicados existentes en el archivo
# (un punto se considera duplicado si tiene el mismo rack, tipo, identificador y puerto)
original_count = len(df)
df = df.drop_duplicates(subset=["rack", "tipo", "identificador", "puerto"], keep="first")
if len(df) < original_count:
    df.to_csv(CSV_FILE, index=False)
    duplicados_eliminados = original_count - len(df)
    st.sidebar.success(f"🧹 Se eliminaron {duplicados_eliminados} punto(s) duplicado(s) del archivo.")

cat_rack = create_or_fix_csv(CAT_RACK, ["rack"])
cat_switch = create_or_fix_csv(CAT_SWITCH, ["rack", "switch"])
cat_patch = create_or_fix_csv(CAT_PATCH, ["rack", "patch_panel"])
cat_lugar = create_or_fix_csv(CAT_LUGAR, ["lugar"])

# ===========================================
# CARGAR IMAGEN
# ===========================================
try:
    base_img = Image.open(IMAGE_FILE)
except:
    st.error(f"No encuentro la imagen: {IMAGE_FILE}")
    st.stop()

# ===========================================
# AGREGAR RACK
# ===========================================
st.sidebar.header("Catálogo de Equipos")

st.sidebar.subheader("➕ Agregar Rack")
new_rack = st.sidebar.text_input("Nombre del Rack")

if st.sidebar.button("Guardar Rack"):
    if new_rack.strip() != "":
        if new_rack not in cat_rack["rack"].values:
            cat_rack.loc[len(cat_rack)] = [new_rack]
            cat_rack.to_csv(CAT_RACK, index=False)
            st.sidebar.success("Rack agregado.")
            st.rerun()
        else:
            st.sidebar.error("Ese rack ya existe.")

# ===========================================
# AGREGAR SWITCH
# ===========================================
st.sidebar.subheader("➕ Agregar Switch")

if len(cat_rack) > 0:
    rack_sw = st.sidebar.selectbox("Rack:", cat_rack["rack"])
    nombre_sw = st.sidebar.text_input("Nombre del Switch")

    if st.sidebar.button("Guardar Switch"):
        if nombre_sw.strip() != "":
            if not nombre_sw.isnumeric():
                cat_switch.loc[len(cat_switch)] = [rack_sw, nombre_sw]
                cat_switch.to_csv(CAT_SWITCH, index=False)
                st.sidebar.success("Switch agregado.")
                st.rerun()
            else:
                st.sidebar.error("Debe contener letras.")

# ===========================================
# AGREGAR PATCH PANEL
# ===========================================
st.sidebar.subheader("➕ Agregar Patch Panel")

if len(cat_rack) > 0:
    rack_pp = st.sidebar.selectbox("Rack para Patch:", cat_rack["rack"])
    num_pp = st.sidebar.text_input("Número Patch Panel")

    if st.sidebar.button("Guardar Patch Panel"):
        if num_pp.isnumeric():
            cat_patch.loc[len(cat_patch)] = [rack_pp, num_pp]
            cat_patch.to_csv(CAT_PATCH, index=False)
            st.sidebar.success("Patch Panel agregado.")
            st.rerun()
        else:
            st.sidebar.error("Debe ser numérico.")

# ===========================================
# AGREGAR LUGAR
# ===========================================
st.sidebar.subheader("➕ Agregar Lugar")
new_lugar = st.sidebar.text_input("Nombre del Lugar (ej: Oficina 101)")

if st.sidebar.button("Guardar Lugar"):
    if new_lugar.strip() != "":
        if new_lugar not in cat_lugar["lugar"].values:
            cat_lugar.loc[len(cat_lugar)] = [new_lugar]
            cat_lugar.to_csv(CAT_LUGAR, index=False)
            st.sidebar.success("Lugar agregado.")
            st.rerun()
        else:
            st.sidebar.error("Ese lugar ya existe.")

# ===========================================
# MOSTRAR MAPA Y CAPTURAR CLIC
# ===========================================
st.subheader("Agregar punto en el croquis")

# Mostrar imagen interactiva completa usando altura explícita
clicked = streamlit_image_coordinates(
    base_img,
    key="map_click",
    height=int(base_img.size[1])  # Altura original: 1200px para imagen completa
)

if clicked:

    st.success(f"X={clicked['x']}  Y={clicked['y']}")

    if len(cat_rack) == 0:
        st.warning("Primero debes crear un Rack.")
        st.stop()

    rack_sel = st.selectbox("Rack:", cat_rack["rack"])
    tipo = st.selectbox("Tipo:", ["SWITCH", "PATCH PANEL"])

    if tipo == "SWITCH":
        lista = cat_switch[cat_switch["rack"] == rack_sel]["switch"]
        if len(lista) == 0:
            st.warning("No hay switches en este rack.")
            st.stop()
        identificador = st.selectbox("Switch:", lista)

    else:
        lista = cat_patch[cat_patch["rack"] == rack_sel]["patch_panel"]
        if len(lista) == 0:
            st.warning("No hay patch panel en este rack.")
            st.stop()
        identificador = st.selectbox("Patch Panel:", lista)

    dependencia = st.selectbox("Dependencia:", ["CM", "FN", "TI"])

    estados = {
        "Funcionando (VERDE)": "#00FF00",
        "No sirve (ROJO)": "#FF0000",
        "Sin identificar (AZUL)": "#0000FF",
        "Pendiente (NARANJA)": "#FFA500"
    }

    estado = st.selectbox("Estado:", list(estados.keys()))
    color = estados[estado]

    puerto = st.text_input("Puerto")
    
    # Selector de lugar desde catálogo
    if len(cat_lugar) > 0:
        lugar = st.selectbox("Lugar:", cat_lugar["lugar"])
    else:
        st.warning("Primero debes agregar lugares en el catálogo.")
        lugar = ""

    if st.button("Guardar punto"):

        duplicado = df[
            (df["rack"] == rack_sel) &
            (df["tipo"] == tipo) &
            (df["identificador"] == identificador) &
            (df["puerto"] == puerto)
        ]

        if not duplicado.empty:
            st.error(f"⚠️ Ya hay un punto con ese puerto registrado:")
            st.warning(f"**Rack:** {rack_sel} | **{tipo}:** {identificador} | **Puerto:** {puerto}")
            st.info("💡 Verifica si quieres eliminar el punto existente en la sección de abajo antes de crear uno nuevo.")
            st.stop()

        new_row = {
            "x": clicked["x"],
            "y": clicked["y"],
            "tipo": tipo,
            "identificador": identificador,
            "color": color,
            "rack": rack_sel,
            "puerto": puerto,
            "dependencia": dependencia,
            "lugar": lugar
        }

        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(CSV_FILE, index=False)

        st.success("Punto guardado correctamente.")
        st.rerun()

# ===========================================
# FILTRAR Y VISUALIZAR PUNTOS
# ===========================================
st.subheader("📋 Visualizar Puntos")

filtro_tipo = st.radio(
    "Tipo de visualización:",
    ["Ver todos", "Filtrar por Rack + Identificador", "Filtrar por Lugar"],
    horizontal=True
)

df_filtrado = df.copy()

if filtro_tipo == "Filtrar por Rack + Identificador":
    col1, col2 = st.columns(2)
    with col1:
        if len(cat_rack) > 0:
            rack_filtro = st.selectbox("Rack:", ["Todos"] + list(cat_rack["rack"]))
        else:
            st.warning("No hay racks disponibles")
            rack_filtro = "Todos"
    
    with col2:
        # Crear lista de identificadores disponibles
        if rack_filtro != "Todos":
            # Mostrar solo equipos del rack seleccionado
            switches_disponibles = cat_switch[cat_switch["rack"] == rack_filtro]["switch"].tolist()
            patches_disponibles = cat_patch[cat_patch["rack"] == rack_filtro]["patch_panel"].tolist()
        else:
            # Mostrar todos los equipos
            switches_disponibles = cat_switch["switch"].tolist()
            patches_disponibles = cat_patch["patch_panel"].tolist()
        
        # Combinar ambas listas con prefijos
        identificadores = ["Todos"]
        identificadores += [f"SW: {sw}" for sw in switches_disponibles]
        identificadores += [f"PP: {pp}" for pp in patches_disponibles]
        
        identificador_filtro = st.selectbox("Identificador:", identificadores)
    
    if rack_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["rack"] == rack_filtro]
        
        # Mostrar inventario de equipos del rack seleccionado
        st.info(f"📦 **Equipos en {rack_filtro}:**")
        col_sw, col_pp = st.columns(2)
        
        with col_sw:
            switches_en_rack = cat_switch[cat_switch["rack"] == rack_filtro]
            if len(switches_en_rack) > 0:
                st.markdown("**🔌 Switches:**")
                for _, sw in switches_en_rack.iterrows():
                    st.markdown(f"- {sw['switch']}")
            else:
                st.markdown("**🔌 Switches:** _Ninguno_")
        
        with col_pp:
            patches_en_rack = cat_patch[cat_patch["rack"] == rack_filtro]
            if len(patches_en_rack) > 0:
                st.markdown("**📊 Patch Panels:**")
                for _, pp in patches_en_rack.iterrows():
                    st.markdown(f"- Patch Panel {pp['patch_panel']}")
            else:
                st.markdown("**📊 Patch Panels:** _Ninguno_")
    
    if identificador_filtro != "Todos":
        # Extraer el nombre real del identificador (después del prefijo "SW: " o "PP: ")
        identificador_real = identificador_filtro.split(": ", 1)[1] if ": " in identificador_filtro else identificador_filtro
        df_filtrado = df_filtrado[df_filtrado["identificador"] == identificador_real]

elif filtro_tipo == "Filtrar por Lugar":
    if len(cat_lugar) > 0:
        lugar_filtro = st.selectbox("Lugar:", ["Todos"] + list(cat_lugar["lugar"]))
        if lugar_filtro != "Todos":
            df_filtrado = df_filtrado[df_filtrado["lugar"] == lugar_filtro]
    else:
        st.warning("No hay lugares en el catálogo")

# Filtro adicional por estado (color)
st.markdown("---")
st.subheader("🎨 Filtrar por Estado")

estados_map = {
    "Todos": None,
    "Funcionando (VERDE)": "#00FF00",
    "No sirve (ROJO)": "#FF0000",
    "Sin identificar (AZUL)": "#0000FF",
    "Pendiente (NARANJA)": "#FFA500"
}

estado_filtro = st.selectbox("Estado:", list(estados_map.keys()))
if estado_filtro != "Todos":
    color_seleccionado = estados_map[estado_filtro]
    df_filtrado = df_filtrado[df_filtrado["color"] == color_seleccionado]

# ===========================================
# DIBUJAR PUNTOS FILTRADOS EN EL MAPA
# ===========================================
st.subheader("Mapa con puntos filtrados")

draw_img = base_img.copy()
draw = ImageDraw.Draw(draw_img)

valid_df = df_filtrado.dropna(subset=["x", "y"])

for _, row in valid_df.iterrows():
    cx, cy = int(row["x"]), int(row["y"])
    r = 10
    draw.ellipse(
        (cx-r, cy-r, cx+r, cy+r),
        fill=row["color"],
        outline="black"
    )

st.image(draw_img)  # Misma configuración que imagen interactiva

# ===========================================
# LISTA DE PUNTOS FILTRADOS
# ===========================================
st.subheader("📋 Lista de Puntos")

# Mostrar resultados con acciones integradas
if len(df_filtrado) > 0:
    st.success(f"📍 Se encontraron {len(df_filtrado)} punto(s)")
    
    # Mostrar cada punto con botones de acción
    for idx, row in df_filtrado.iterrows():
        with st.container():
            col1, col2, col3 = st.columns([6, 1, 1])
            
            with col1:
                # Información del punto
                lugar_info = f" | 📍 {row['lugar']}" if pd.notna(row.get('lugar')) and row.get('lugar') != '' else ""
                st.markdown(f"""
                **{row['rack']}** | {row['tipo']}: **{row['identificador']}** | Puerto: **{row['puerto']}** | 
                {row['dependencia']}{lugar_info}
                """)
            
            with col2:
                # Botón de editar
                if st.button("✏️ Editar", key=f"edit_{idx}", use_container_width=True):
                    st.session_state[f"editing_{idx}"] = True
                    st.rerun()
            
            with col3:
                # Botón de eliminar
                if st.button("🗑️", key=f"delete_{idx}", use_container_width=True, type="secondary"):
                    df = df.drop(idx)
                    df.to_csv(CSV_FILE, index=False)
                    st.success("Punto eliminado.")
                    st.rerun()
            
            # Mostrar editor si está en modo edición
            if st.session_state.get(f"editing_{idx}", False):
                with st.expander("✏️ Editar punto", expanded=True):
                    new_color = st.color_picker("Color:", row["color"], key=f"color_{idx}")
                    
                    col_save, col_cancel = st.columns(2)
                    with col_save:
                        if st.button("💾 Guardar", key=f"save_{idx}", use_container_width=True, type="primary"):
                            df.loc[idx, "color"] = new_color
                            df.to_csv(CSV_FILE, index=False)
                            st.session_state[f"editing_{idx}"] = False
                            st.success("Cambios guardados.")
                            st.rerun()
                    
                    with col_cancel:
                        if st.button("❌ Cancelar", key=f"cancel_{idx}", use_container_width=True):
                            st.session_state[f"editing_{idx}"] = False
                            st.rerun()
            
            st.markdown("---")
    
else:
    st.info("No se encontraron puntos con los filtros seleccionados")
