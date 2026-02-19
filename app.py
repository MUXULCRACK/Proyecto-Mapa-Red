import streamlit as st
from streamlit_image_coordinates import streamlit_image_coordinates
from PIL import Image, ImageDraw
import pandas as pd
import os
from datetime import datetime

# ===========================================
# CONFIGURACIÓN INICIAL
# ===========================================
st.set_page_config(layout="wide")
st.title("Mapa Interactivo de Red – Empresa")

CSV_FILE = "network_points.csv"
DELETED_CSV_FILE = "deleted_points.csv"
IMAGE_FILE = "croquis.png"

CAT_RACK = "catalogo_racks.csv"
CAT_SWITCH = "catalogo_switch.csv"
CAT_PATCH = "catalogo_patch.csv"
CAT_LUGAR = "catalogo_lugares.csv"
CAT_DEPENDENCIA = "catalogo_dependencias.csv"

def create_or_fix_csv(filename, columns):
    try:
        df = pd.read_csv(filename)
        if list(df.columns) != columns:
            raise ValueError("Columnas incorrectas")
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError):
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        return df

# ===========================================
# CARGAR DATOS
# ===========================================
df = create_or_fix_csv(CSV_FILE, ["x","y","tipo","identificador","color","rack","puerto","dependencia","lugar","nomenclatura"])
df_deleted = create_or_fix_csv(DELETED_CSV_FILE, ["x","y","tipo","identificador","color","rack","puerto","dependencia","lugar","fecha_hora","ip","nomenclatura"])

df = df.drop_duplicates(subset=["x", "y"], keep="first")

cat_rack = create_or_fix_csv(CAT_RACK, ["rack"])
cat_switch = create_or_fix_csv(CAT_SWITCH, ["rack", "switch"])
cat_patch = create_or_fix_csv(CAT_PATCH, ["rack", "patch_panel"])
cat_lugar = create_or_fix_csv(CAT_LUGAR, ["lugar"])
cat_dependencia = create_or_fix_csv(CAT_DEPENDENCIA, ["dependencia"])

# Asegurar que existan valores por defecto si está vacío
if len(cat_dependencia) == 0:
    for dep in ["CM", "FN", "TI"]:
        cat_dependencia.loc[len(cat_dependencia)] = [dep]
    cat_dependencia.to_csv(CAT_DEPENDENCIA, index=False)

try:
    base_img = Image.open(IMAGE_FILE)
except:
    st.error(f"No encuentro la imagen: {IMAGE_FILE}")
    st.stop()

# ===========================================
# SIDEBAR
# ===========================================
st.sidebar.header("Opciones")
show_history = st.sidebar.checkbox("Ver Historial de Eliminados 🕒", value=False)

st.sidebar.markdown("---")
st.sidebar.subheader("➕ Agregar Rack")
new_rack = st.sidebar.text_input("Nombre del Rack")
if st.sidebar.button("Guardar Rack"):
    if new_rack.strip() and new_rack not in cat_rack["rack"].values:
        cat_rack.loc[len(cat_rack)] = [new_rack]
        cat_rack.to_csv(CAT_RACK, index=False)
        st.sidebar.success("Rack agregado.")
        st.rerun()

st.sidebar.subheader("➕ Agregar Switch")
if len(cat_rack) > 0:
    rack_sw = st.sidebar.selectbox("Rack:", cat_rack["rack"], key="sb_rack_sw")
    nombre_sw = st.sidebar.text_input("Nombre del Switch", key="sb_name_sw")
    if st.sidebar.button("Guardar Switch"):
        if nombre_sw.strip():
            cat_switch.loc[len(cat_switch)] = [rack_sw, nombre_sw]
            cat_switch.to_csv(CAT_SWITCH, index=False)
            st.sidebar.success("✅ Switch agregado.")
            st.rerun()

st.sidebar.subheader("➕ Agregar Patch Panel")
if len(cat_rack) > 0:
    rack_pp = st.sidebar.selectbox("Rack:", cat_rack["rack"], key="sb_rack_pp")
    nombre_pp = st.sidebar.text_input("Nombre del Patch Panel", key="sb_name_pp")
    if st.sidebar.button("Guardar Patch Panel"):
        if nombre_pp.strip():
            cat_patch.loc[len(cat_patch)] = [rack_pp, nombre_pp]
            cat_patch.to_csv(CAT_PATCH, index=False)
            st.sidebar.success("✅ Patch Panel agregado.")
            st.rerun()

st.sidebar.subheader("➕ Agregar Lugar")
new_lugar = st.sidebar.text_input("Nombre del Lugar", key="sb_new_lugar")
if st.sidebar.button("Guardar Lugar"):
    if new_lugar.strip() and new_lugar not in cat_lugar["lugar"].values:
        cat_lugar.loc[len(cat_lugar)] = [new_lugar]
        cat_lugar.to_csv(CAT_LUGAR, index=False)
        st.sidebar.success("Lugar agregado.")
        st.rerun()

st.sidebar.subheader("➕ Agregar Dependencia")
new_dep = st.sidebar.text_input("Nombre de la Dependencia", key="sb_new_dep")
if st.sidebar.button("Guardar Dependencia"):
    if new_dep.strip() and new_dep not in cat_dependencia["dependencia"].values:
        cat_dependencia.loc[len(cat_dependencia)] = [new_dep]
        cat_dependencia.to_csv(CAT_DEPENDENCIA, index=False)
        st.sidebar.success("Dependencia agregada.")
        st.rerun()

# ===========================================
# FUNCIONES
# ===========================================
def draw_points(image, points_df, deleted_df=None, show_hist=False):
    draw = ImageDraw.Draw(image)
    if show_hist:
        if deleted_df is not None and not deleted_df.empty:
            last_3 = deleted_df.tail(3)
            for _, row in last_3.iterrows():
                x, y = int(row['x']), int(row['y'])
                r = 5  # Antes 8
                draw.ellipse([x-r, y-r, x+r, y+r], fill="#808080", outline="white", width=2)
                draw.line([x-3, y-3, x+3, y+3], fill="white", width=2)
                draw.line([x+3, y-3, x-3, y+3], fill="white", width=2)
    else:
        for _, row in points_df.iterrows():
            x, y, color = int(row['x']), int(row['y']), row['color']
            r = 3  # Antes 6
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline="white", width=2)
    return image

colores_a_nombres = {
    "#00FF00": "🟢 Funcionando y ubicado (VERDE)",
    "#FF0000": "🔴 No sirve y ubicado (ROJO)",
    "#0000FF": "🔵 Sin identificar y funcionando (AZUL)",
    "#FFA500": "🟠 Sin identificar y no se sabe funcionamiento (NARANJA)"
}

# Mapa 1: Selección de ubicación
st.subheader("📍 Mapa 1: Selección de ubicación")
st.write("Haz clic en este mapa limpio para capturar las coordenadas de un nuevo punto.")

# Obtenemos el click (sin pasar height para mayor precisión de coordenadas originales)
clicked = streamlit_image_coordinates(base_img, key="map_add")

if clicked:
    # Solo guardar y recargar si es un click nuevo o diferente al anterior
    if "last_click" not in st.session_state or st.session_state["last_click"] != clicked:
        st.session_state["last_click"] = clicked
        st.rerun()
if "last_click" in st.session_state:
    c_data = st.session_state["last_click"]
    # Contenedor principal para el formulario de creación
    with st.container(border=True):
        st.subheader("➕ Agregar Nuevo Punto de Red")
        st.info(f"📍 Coordenadas: X={c_data['x']}, Y={c_data['y']}")
        
        # Selector de estado (debe estar fuera del st.form para ser reactivo)
        estado_sel = st.selectbox("Estado del Punto de Red:", list(colores_a_nombres.values()), key="new_point_status")
        color_sel = [c for c, n in colores_a_nombres.items() if n == estado_sel][0]
        is_completo = "VERDE" in estado_sel or "ROJO" in estado_sel

        with st.form("crear_punto"):
            nom_sel = st.text_input("Nombre del Punto (Nomenclatura):", help="Ej: PTO-01, RECEPCIÓN-A, etc.")
            if is_completo:
                st.markdown("**Conexión al Rack (Destino)**")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    r_sel = st.selectbox("Rack de Destino:", cat_rack["rack"])
                    t_sel = st.selectbox("Tipo de Conexión:", ["SWITCH", "PATCH PANEL"])
                with col_c2:
                    if t_sel == "SWITCH":
                        l_ids = cat_switch[cat_switch["rack"] == r_sel]["switch"].tolist()
                    else:
                        l_ids = cat_patch[cat_patch["rack"] == r_sel]["patch_panel"].tolist()
                    id_sel = st.selectbox("Equipo de Destino:", l_ids if l_ids else ["(No hay)"])
                    port_sel = st.text_input("Puerto en el Equipo:")
                
                st.markdown("---")
                st.markdown("**Ubicación y Responsable**")
                col_c3, col_c4 = st.columns(2)
                with col_c3:
                    dep_sel = st.selectbox("Dependencia:", cat_dependencia["dependencia"])
                with col_c4:
                    place_sel = st.selectbox("Lugar:", cat_lugar["lugar"])
            else:
                r_sel, t_sel, id_sel, port_sel = "", "", "", ""
                st.markdown("**Ubicación y Responsable**")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    dep_sel = st.selectbox("Dependencia:", cat_dependencia["dependencia"])
                with col_c2:
                    place_sel = st.selectbox("Lugar:", cat_lugar["lugar"])

            if st.form_submit_button("✅ Guardar Punto", use_container_width=True):
                # Validar Nomenclatura Única
                nom_existe = nom_sel in df["nomenclatura"].astype(str).values
                
                if is_completo and (not r_sel or not id_sel or not port_sel or id_sel == "(No hay)"):
                    st.error("❌ Por favor completa todos los campos técnicos.")
                elif not nom_sel:
                    st.error("❌ Por favor asigna una Nomenclatura o Nombre al punto.")
                elif nom_existe:
                    st.error(f"❌ La nomenclatura '**{nom_sel}**' ya está en uso por otro punto activo.")
                elif is_completo and not port_sel.isnumeric():
                    st.error("❌ El puerto debe ser un número.")
                else:
                    new_row = {"x": c_data["x"], "y": c_data["y"], "tipo": t_sel, "identificador": id_sel, "color": color_sel, "rack": r_sel, "puerto": port_sel, "dependencia": dep_sel, "lugar": place_sel, "nomenclatura": nom_sel}
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(CSV_FILE, index=False)
                    del st.session_state["last_click"]
                    st.success("✅ ¡Punto guardado con éxito!")
                    st.rerun()

st.markdown("---")

# Mapa 2: Visualización con Filtros
st.subheader("📋 Mapa 2: Visualización y Filtros")
st.write("Usa este mapa para buscar equipos específicos. Aquí es donde se aplican los filtros y se activa el historial.")

col_f1, col_f2, col_f3 = st.columns(3)
with col_f1:
    filtro_modo = st.radio("Filtro:", ["Todos", "Rack y Equipo", "Lugar", "Dependencia"], horizontal=True)
with col_f2:
    df_f = df.copy()
    if filtro_modo == "Rack y Equipo":
        st.markdown("**Búsqueda por Conexión al Rack:**")
        col_r1, col_r2 = st.columns(2)
        with col_r1:
            rack_list = ["Todos"] + list(cat_rack["rack"])
            f_rk = st.selectbox("Rack de Destino:", rack_list, key="ff_rack")
            
            f_tp = st.selectbox("Tipo de Conexión:", ["Todos", "SWITCH", "PATCH PANEL"], key="ff_tipo")
        with col_r2:
            # Lista de identificadores dinámica según rack y tipo usando los catálogos
            if f_tp == "SWITCH":
                temp_ids = cat_switch[cat_switch["rack"] == f_rk]["switch"] if f_rk != "Todos" else cat_switch["switch"]
                id_list = ["Todos"] + sorted(list(temp_ids.unique()))
            elif f_tp == "PATCH PANEL":
                temp_ids = cat_patch[cat_patch["rack"] == f_rk]["patch_panel"] if f_rk != "Todos" else cat_patch["patch_panel"]
                id_list = ["Todos"] + sorted(list(temp_ids.unique()))
            else:
                all_ids = list(cat_switch["switch"].unique()) + list(cat_patch["patch_panel"].unique())
                # Asegurar que todos sean strings para evitar errores de ordenamiento
                id_list = ["Todos"] + sorted(list(set([str(x) for x in all_ids if pd.notna(x)])))
                
            f_id = st.selectbox("Equipo de Destino:", id_list, key="ff_id")
            f_dp = st.selectbox("Dependencia:", ["Todos"] + list(cat_dependencia["dependencia"]), key="ff_dep")

        # Aplicar filtros de forma acumulativa
        if f_rk != "Todos": df_f = df_f[df_f["rack"] == f_rk]
        if f_tp != "Todos": df_f = df_f[df_f["tipo"] == f_tp]
        if f_id != "Todos": df_f = df_f[df_f["identificador"] == f_id]
        if f_dp != "Todos": df_f = df_f[df_f["dependencia"] == f_dp]

    elif filtro_modo == "Lugar":
        lf = st.selectbox("Filtrar por Lugar:", ["Todos"] + list(cat_lugar["lugar"]))
        if lf != "Todos": df_f = df_f[df_f["lugar"] == lf]
    elif filtro_modo == "Dependencia":
        df_df = st.selectbox("Filtrar por Dependencia:", ["Todos"] + list(cat_dependencia["dependencia"]))
        if df_df != "Todos": df_f = df_f[df_f["dependencia"] == df_df]
with col_f3:
    sf = st.selectbox("Estado:", ["Todos"] + list(colores_a_nombres.values()))
    if sf != "Todos":
        cf = [c for c, n in colores_a_nombres.items() if n == sf][0]
        df_f = df_f[df_f["color"] == cf]

img_mapa2 = draw_points(base_img.copy(), df_f, df_deleted, show_history)
clicked_map2 = streamlit_image_coordinates(img_mapa2, key="map_view")

if clicked_map2:
    cx, cy = clicked_map2["x"], clicked_map2["y"]
    
    if show_history:
        # Modo HISTORIAL: Buscar en los últimos 3 eliminados
        if df_deleted is not None and not df_deleted.empty:
            last_3 = df_deleted.tail(3).copy()
            last_3['dist'] = (last_3['x'] - cx)**2 + (last_3['y'] - cy)**2
            closest = last_3.loc[last_3['dist'].idxmin()]
            if closest['dist'] < 400:
                st.toast(f"🕒 Eliminado: {closest['identificador']}", icon="🗑️")
                st.warning(f"📜 **Historial de Eliminación:**\n\n"
                           f"- **Nomenclatura:** {closest.get('nomenclatura', 'N/A')}\n"
                           f"- **Equipo:** {closest['identificador']}\n"
                           f"- **Rack:** {closest['rack'] if closest['rack'] else 'N/A'}\n"
                           f"- **Eliminado el:** {closest['fecha_hora']}\n"
                           f"- **IP de Usuario:** {closest.get('ip', 'Desconocida')}")
            else:
                st.warning("Haz clic cerca de un punto gris para ver su historial.")
    else:
        # Modo NORMAL: Buscar en puntos activos filtrados
        if "moving_idx" in st.session_state:
            # EJECUTAR RE-UBICACIÓN
            m_idx = st.session_state["moving_idx"]
            df.loc[m_idx, ["x", "y"]] = [cx, cy]
            df.to_csv(CSV_FILE, index=False)
            st.success(f"✅ Punto '{df.loc[m_idx, 'nomenclatura']}' re-ubicado correctamente.")
            del st.session_state["moving_idx"]
            st.rerun()
            
        if not df_f.empty:
            df_f['dist'] = (df_f['x'] - cx)**2 + (df_f['y'] - cy)**2
            closest_idx = df_f['dist'].idxmin()
            closest = df_f.loc[closest_idx]
            
            if closest['dist'] < 400: # Radio de ~20px
                st.toast(f"📍 Seleccionado: {closest['nomenclatura']}", icon="🎯")
                with st.container(border=True):
                    st.info(f"🔍 **Detalles del Punto:**\n\n"
                            f"- **Nomenclatura:** {closest.get('nomenclatura', 'N/A')}\n"
                            f"- **Estado:** {colores_a_nombres.get(closest['color'], 'Desconocido')}\n"
                            f"- **Ubicación:** {closest['lugar']} | **Dependencia:** {closest['dependencia']}\n"
                            f"- **Rack:** {closest['rack']} | **Tipo:** {closest['tipo']} | **Equipo:** {closest['identificador']} | **Puerto:** {closest['puerto']}")
                    
                    if st.button("🎯 Re-ubicar este punto", key=f"move_btn_{closest_idx}"):
                        st.session_state["moving_idx"] = closest_idx
                        st.toast("⚠️ Modo Re-ubicación: Haz clic en la nueva posición en el mapa.", icon="🗺️")
                        st.rerun()
            else:
                st.warning("No hay ningún punto cerca de donde hiciste clic.")

if "moving_idx" in st.session_state:
    st.warning("🚨 **MODO RE-UBICACIÓN ACTIVO**: Haz clic en cualquier parte del **Mapa 2** para mover el punto seleccionado.")
    if st.button("❌ Cancelar Re-ubicación"):
        del st.session_state["moving_idx"]
        st.rerun()

# Lista
st.subheader("📄 Listado de puntos")
if len(df_f) > 0:
    for idx, row in df_f.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([6,1,1])
            with c1:
                if row['rack']:
                    st.write(f"🏠 **{row['nomenclatura'] if row.get('nomenclatura') else row['lugar']}** | 🔌 Rack: {row['rack']} | Eqp: {row['identificador']} | P:{row['puerto']} | {row['dependencia']}")
                else:
                    st.write(f"🚩 **{row['nomenclatura'] if row.get('nomenclatura') else row['dependencia']}** | {row['lugar']}")
                st.caption(f"Estado del Punto: {colores_a_nombres.get(row['color'], '??')}")
            with c2:
                if st.button("✏️", key=f"e_{idx}"):
                    st.session_state[f"ed_{idx}"] = True
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{idx}"):
                    # Intentar obtener IP del usuario
                    user_ip = "Local"
                    try:
                        # En Streamlit >= 1.37 se puede intentar obtener de los headers
                        headers = st.context.headers
                        user_ip = headers.get("X-Forwarded-For", "Local").split(",")[0]
                    except:
                        pass
                    
                    to_d = df.loc[[idx]].copy()
                    to_d["fecha_hora"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    to_d["ip"] = user_ip
                    
                    to_d.to_csv(DELETED_CSV_FILE, mode='a', header=not os.path.exists(DELETED_CSV_FILE), index=False)
                    df = df.drop(idx)
                    df.to_csv(CSV_FILE, index=False)
                    st.rerun()
            
            if st.session_state.get(f"ed_{idx}", False):
                with st.container(border=True):
                    st.markdown(f"### ✏️ Editando: {row['rack']} - {row['identificador']}")
                    
                    # Selector de estado reactivo
                    e_estado = st.selectbox("Estado del Punto de Red:", list(colores_a_nombres.values()), 
                                           index=list(colores_a_nombres.keys()).index(row['color']) if row['color'] in colores_a_nombres else 0,
                                           key=f"edit_status_sel_{idx}")
                    e_color = [c for c, n in colores_a_nombres.items() if n == e_estado][0]
                    e_comp = "VERDE" in e_estado or "ROJO" in e_estado
 
                    with st.form(f"f_edit_{idx}"):
                        e_nom = st.text_input("Nomenclatura / Nombre:", value=row.get('nomenclatura', ''))
                        
                        if e_comp:
                            st.markdown("**Detalles de Conexión al Rack**")
                            col_e1, col_e2 = st.columns(2)
                            with col_e1:
                                # Safely find index for rack
                                r_list = list(cat_rack["rack"])
                                r_idx = r_list.index(row['rack']) if row['rack'] in r_list else 0
                                e_rack = st.selectbox("Rack de Destino:", r_list, index=r_idx)
                                
                                e_tipo = st.selectbox("Tipo de Conexión:", ["SWITCH", "PATCH PANEL"], 
                                                    index=["SWITCH", "PATCH PANEL"].index(row['tipo']) if row['tipo'] in ["SWITCH", "PATCH PANEL"] else 0)
                            with col_e2:
                                if e_tipo == "SWITCH":
                                    e_l_ids = cat_switch[cat_switch["rack"] == e_rack]["switch"].tolist()
                                elif e_tipo == "PATCH PANEL":
                                    e_l_ids = cat_patch[cat_patch["rack"] == e_rack]["patch_panel"].tolist()
                                else:
                                    e_l_ids = []
                                
                                # Safely finding ID
                                id_list = e_l_ids if e_l_ids else ["(No hay)"]
                                id_idx = id_list.index(row['identificador']) if row['identificador'] in id_list else 0
                                e_id = st.selectbox("Equipo de Destino:", id_list, index=id_idx)
                                
                                e_port = st.text_input("Puerto en el Equipo:", value=str(row['puerto']) if pd.notna(row['puerto']) else "")
                        else:
                            e_rack, e_tipo, e_id, e_port = "", "", "", ""

                        st.markdown("---")
                        st.markdown("**Ubicación y Responsable**")
                        col_e3, col_e4 = st.columns(2)
                        with col_e3:
                            e_dep = st.selectbox("Dependencia:", cat_dependencia["dependencia"], index=list(cat_dependencia["dependencia"]).index(row['dependencia']) if row['dependencia'] in list(cat_dependencia["dependencia"]) else 0)
                        with col_e4:
                            e_place = st.selectbox("Lugar:", cat_lugar["lugar"], index=list(cat_lugar["lugar"]).index(row['lugar']) if row['lugar'] in list(cat_lugar["lugar"]) else 0)
                        
                        col_btns1, col_btns2 = st.columns(2)
                        with col_btns1:
                            if st.form_submit_button("💾 Actualizar Cambios", use_container_width=True):
                                # Validar Nomenclatura Única (excluyendo a sí mismo por el índice)
                                nom_en_otros = e_nom in df.drop(idx)["nomenclatura"].astype(str).values
                                
                                if not e_nom:
                                    st.error("❌ El punto debe tener una nomenclatura.")
                                elif nom_en_otros:
                                    st.error(f"❌ La nomenclatura '**{e_nom}**' ya está en uso por otro punto.")
                                elif e_tipo != "None" and e_port and not e_port.isnumeric():
                                    st.error("❌ El puerto debe ser un número.")
                                else:
                                    # Conservamos X e Y originales
                                    old_x, old_y = row['x'], row['y']
                                    df.loc[idx, ["x","y","rack","tipo","identificador","puerto","dependencia","lugar","color","nomenclatura"]] = [old_x, old_y, e_rack, e_tipo, e_id, e_port, e_dep, e_place, e_color, e_nom]
                                    df.to_csv(CSV_FILE, index=False)
                                st.session_state[f"ed_{idx}"] = False
                                st.success("✅ Cambios guardados.")
                                st.rerun()
                        with col_btns2:
                            if st.form_submit_button("❌ Cancelar", use_container_width=True):
                                st.session_state[f"ed_{idx}"] = False
                                st.rerun()
else:
    st.info("No se encontraron puntos.")
