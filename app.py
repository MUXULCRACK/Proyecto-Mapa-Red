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

# Columnas del CSV principal: ahora tiene switch Y patch_panel por separado
CSV_COLUMNS = ["x","y","color","rack","switch","patch_panel","puerto_switch","puerto_patch","dependencia","lugar","nomenclatura","comentarios"]

def create_or_fix_csv(filename, columns):
    try:
        df = pd.read_csv(filename)
        # Agregar columnas faltantes sin borrar datos
        for col in columns:
            if col not in df.columns:
                df[col] = ""
        df = df[columns]
        df.to_csv(filename, index=False)
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError, ValueError):
        df = pd.DataFrame(columns=columns)
        df.to_csv(filename, index=False)
        return df

# ===========================================
# CARGAR DATOS
# ===========================================
df = create_or_fix_csv(CSV_FILE, CSV_COLUMNS)
df_deleted = create_or_fix_csv(DELETED_CSV_FILE, ["x","y","color","rack","switch","patch_panel","puerto_switch","puerto_patch","dependencia","lugar","nomenclatura","comentarios","fecha_hora","ip"])

df = df.drop_duplicates(subset=["x", "y"], keep="first")

cat_rack       = create_or_fix_csv(CAT_RACK,       ["rack"])
cat_switch     = create_or_fix_csv(CAT_SWITCH,     ["rack", "switch"])
cat_patch      = create_or_fix_csv(CAT_PATCH,      ["rack", "patch_panel"])
cat_lugar      = create_or_fix_csv(CAT_LUGAR,      ["lugar"])
cat_dependencia= create_or_fix_csv(CAT_DEPENDENCIA,["dependencia"])

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
# SIDEBAR – CATÁLOGOS
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
                r = 6
                draw.ellipse([x-r, y-r, x+r, y+r], fill="#808080", outline="white", width=2)
                draw.line([x-3, y-3, x+3, y+3], fill="white", width=2)
                draw.line([x+3, y-3, x-3, y+3], fill="white", width=2)
    else:
        for _, row in points_df.iterrows():
            x, y, color = int(row['x']), int(row['y']), row['color']
            r = 4
            draw.ellipse([x-r, y-r, x+r, y+r], fill=color, outline="white", width=2)
    return image

colores_a_nombres = {
    "#00FF00": "🟢 Funcionando y ubicado (VERDE)",
    "#FF0000": "🔴 No sirve y ubicado (ROJO)",
    "#0000FF": "🔵 Sin identificar y funcionando (AZUL)",
    "#FFA500": "🟠 Ubicado sin switch (NARANJA)"
}

# Helper: obtener switches y patches para un rack
def get_switches(rack):
    if not rack:
        return []
    return cat_switch[cat_switch["rack"] == rack]["switch"].tolist()

def get_patches(rack):
    if not rack:
        return []
    return cat_patch[cat_patch["rack"] == rack]["patch_panel"].tolist()

# ===========================================
# MAPA 1: AGREGAR PUNTO
# ===========================================
st.subheader("📍 Mapa 1: Selección de ubicación")
st.write("Haz clic en este mapa limpio para capturar las coordenadas de un nuevo punto.")

clicked = streamlit_image_coordinates(base_img, key="map_add")

if clicked:
    if "last_click" not in st.session_state or st.session_state["last_click"] != clicked:
        st.session_state["last_click"] = clicked
        st.rerun()

if "last_click" in st.session_state:
    c_data = st.session_state["last_click"]
    with st.container(border=True):
        st.subheader("➕ Agregar Nuevo Punto de Red")
        st.info(f"📍 Coordenadas: X={c_data['x']}, Y={c_data['y']}")

        estado_sel = st.selectbox("Estado del Punto de Red:", list(colores_a_nombres.values()), key="new_point_status")
        color_sel = [c for c, n in colores_a_nombres.items() if n == estado_sel][0]
        is_completo = "VERDE" in estado_sel or "ROJO" in estado_sel or "NARANJA" in estado_sel

        with st.form("crear_punto"):
            nom_sel = st.text_input("Nombre del Punto (Nomenclatura):", help="Ej: PTO-01, RECEPCIÓN-A, etc.")

            if is_completo:
                st.markdown("**Conexión al Rack**")
                r_sel = st.selectbox("Rack de Destino:", cat_rack["rack"] if len(cat_rack) > 0 else ["(Sin racks)"])

                # Switch y Patch Panel juntos en dos columnas
                col_sw, col_pp = st.columns(2)
                with col_sw:
                    sw_list = get_switches(r_sel)
                    sw_sel = st.selectbox("Switch:", sw_list if sw_list else ["(No hay)"])
                    puerto_sw_sel = st.text_input("Puerto en Switch (número):")
                with col_pp:
                    pp_list = get_patches(r_sel)
                    pp_sel = st.selectbox("Patch Panel:", pp_list if pp_list else ["(No hay)"])
                    puerto_pp_sel = st.text_input("Puerto en Patch Panel (número):")

                st.markdown("---")
                st.markdown("**Ubicación y Responsable**")
                col_c3, col_c4 = st.columns(2)
                with col_c3:
                    dep_sel = st.selectbox("Dependencia:", cat_dependencia["dependencia"])
                with col_c4:
                    place_sel = st.selectbox("Lugar:", cat_lugar["lugar"])
            else:
                r_sel, sw_sel, pp_sel, puerto_sw_sel, puerto_pp_sel = "", "", "", "", ""
                st.markdown("**Ubicación y Responsable**")
                col_c1, col_c2 = st.columns(2)
                with col_c1:
                    dep_sel = st.selectbox("Dependencia:", cat_dependencia["dependencia"])
                with col_c2:
                    place_sel = st.selectbox("Lugar:", cat_lugar["lugar"])

            comentarios_sel = st.text_area("💬 Comentarios:", placeholder="Observaciones adicionales (opcional)...")

            if st.form_submit_button("✅ Guardar Punto", use_container_width=True):
                nom_existe = (df["nomenclatura"].astype(str) == nom_sel).sum() >= 2

                if is_completo and (not r_sel or sw_sel == "(No hay)" or pp_sel == "(No hay)" or not puerto_sw_sel or not puerto_pp_sel):
                    st.error("❌ Por favor completa todos los campos del rack (switch, patch panel, puerto en switch y puerto en patch panel).")
                elif not nom_sel:
                    st.error("❌ Por favor asigna una Nomenclatura o Nombre al punto.")
                elif nom_existe:
                    st.error(f"❌ La nomenclatura '**{nom_sel}**' ya está en uso 2 veces (máximo permitido).")
                elif is_completo and (puerto_sw_sel and not puerto_sw_sel.isnumeric() or puerto_pp_sel and not puerto_pp_sel.isnumeric()):
                    st.error("❌ Los puertos deben ser números.")
                else:
                    new_row = {
                        "x": c_data["x"], "y": c_data["y"],
                        "color": color_sel,
                        "rack": r_sel,
                        "switch": sw_sel,
                        "patch_panel": pp_sel,
                        "puerto_switch": puerto_sw_sel,
                        "puerto_patch": puerto_pp_sel,
                        "dependencia": dep_sel,
                        "lugar": place_sel,
                        "nomenclatura": nom_sel,
                        "comentarios": comentarios_sel
                    }
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    df.to_csv(CSV_FILE, index=False)
                    del st.session_state["last_click"]
                    st.success("✅ ¡Punto guardado con éxito!")
                    st.rerun()

st.markdown("---")

# ===========================================
# MAPA 2: VISUALIZACIÓN Y FILTROS
# ===========================================
st.subheader("📋 Mapa 2: Visualización y Filtros")
st.write("Usa este mapa para buscar equipos específicos.")

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
            f_rk = st.selectbox("Rack:", rack_list, key="ff_rack")

            # Switch filter
            sw_opts = cat_switch[cat_switch["rack"] == f_rk]["switch"].tolist() if f_rk != "Todos" else cat_switch["switch"].tolist()
            f_sw = st.selectbox("Switch:", ["Todos"] + sorted([str(x) for x in sw_opts if pd.notna(x)]), key="ff_sw")
        with col_r2:
            # Patch Panel filter
            pp_opts = cat_patch[cat_patch["rack"] == f_rk]["patch_panel"].tolist() if f_rk != "Todos" else cat_patch["patch_panel"].tolist()
            f_pp = st.selectbox("Patch Panel:", ["Todos"] + sorted([str(x) for x in pp_opts if pd.notna(x)]), key="ff_pp")

            f_dp = st.selectbox("Dependencia:", ["Todos"] + list(cat_dependencia["dependencia"]), key="ff_dep")

        if f_rk != "Todos": df_f = df_f[df_f["rack"] == f_rk]
        if f_sw != "Todos": df_f = df_f[df_f["switch"].astype(str) == f_sw]
        if f_pp != "Todos": df_f = df_f[df_f["patch_panel"].astype(str) == f_pp]
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
        if df_deleted is not None and not df_deleted.empty:
            last_3 = df_deleted.tail(3).copy()
            last_3['dist'] = (last_3['x'] - cx)**2 + (last_3['y'] - cy)**2
            closest = last_3.loc[last_3['dist'].idxmin()]
            if closest['dist'] < 400:
                st.toast(f"🕒 Eliminado: {closest.get('nomenclatura','?')}", icon="🗑️")
                st.warning(
                    f"📜 **Historial de Eliminación:**\n\n"
                    f"- **Nomenclatura:** {closest.get('nomenclatura', 'N/A')}\n"
                    f"- **Rack:** {closest.get('rack','N/A')} | **Switch:** {closest.get('switch','N/A')} | **Patch Panel:** {closest.get('patch_panel','N/A')}\n"
                    f"- **Puerto:** {closest.get('puerto','N/A')}\n"
                    f"- **Eliminado el:** {closest.get('fecha_hora','N/A')}\n"
                    f"- **IP de Usuario:** {closest.get('ip', 'Desconocida')}"
                )
            else:
                st.warning("Haz clic cerca de un punto gris para ver su historial.")
    else:
        if "moving_idx" in st.session_state:
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

            if closest['dist'] < 400:
                st.toast(f"📍 Seleccionado: {closest['nomenclatura']}", icon="🎯")
                with st.container(border=True):
                    rack_val  = closest.get('rack','')
                    sw_val    = closest.get('switch','')
                    pp_val    = closest.get('patch_panel','')
                    psw_val   = closest.get('puerto_switch','')
                    ppp_val   = closest.get('puerto_patch','')
                    rack_info = ""
                    if rack_val:
                        rack_info = (f"- **Rack:** {rack_val}\n"
                                     f"- **Switch:** {sw_val} | **Puerto Switch:** {psw_val}\n"
                                     f"- **Patch Panel:** {pp_val} | **Puerto PP:** {ppp_val}\n")
                    coment_v = str(closest.get('comentarios','') or '')
                    coment_line = f"- **Comentarios:** {coment_v}\n" if coment_v else ""
                    st.info(
                        f"🔍 **Detalles del Punto:**\n\n"
                        f"- **Nomenclatura:** {closest.get('nomenclatura','N/A')}\n"
                        f"- **Estado:** {colores_a_nombres.get(closest['color'], 'Desconocido')}\n"
                        f"- **Ubicación:** {closest.get('lugar','')} | **Dependencia:** {closest.get('dependencia','')}\n"
                        f"{rack_info}"
                        f"{coment_line}"
                    )
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

# ===========================================
# LISTADO DE PUNTOS
# ===========================================
st.subheader("📄 Listado de puntos")
if len(df_f) > 0:
    for idx, row in df_f.iterrows():
        with st.container():
            c1, c2, c3 = st.columns([6,1,1])
            with c1:
                rack_v = str(row.get('rack','') or '')
                sw_v   = str(row.get('switch','') or '')
                pp_v   = str(row.get('patch_panel','') or '')
                nom_v  = str(row.get('nomenclatura','') or row.get('lugar',''))
                if rack_v:
                    psw_v = str(row.get('puerto_switch','') or '')
                    ppp_v = str(row.get('puerto_patch','') or '')
                    st.write(f"🏠 **{nom_v}** | 🔌 Rack: {rack_v} | SW: {sw_v} (P:{psw_v}) | PP: {pp_v} (P:{ppp_v}) | {row.get('dependencia','')}")
                else:
                    st.write(f"🚩 **{nom_v}** | {row.get('lugar','')} | {row.get('dependencia','')}")
                coment_row = str(row.get('comentarios','') or '')
                caption_txt = f"Estado: {colores_a_nombres.get(row['color'], '??')}"
                if coment_row:
                    caption_txt += f" | 💬 {coment_row}"
                st.caption(caption_txt)
            with c2:
                if st.button("✏️", key=f"e_{idx}"):
                    st.session_state[f"ed_{idx}"] = True
                    st.rerun()
            with c3:
                if st.button("🗑️", key=f"d_{idx}"):
                    user_ip = "Local"
                    try:
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
                    rack_v = str(row.get('rack','') or '')
                    sw_v   = str(row.get('switch','') or '')
                    st.markdown(f"### ✏️ Editando: {row.get('nomenclatura','Punto')}")

                    e_estado = st.selectbox(
                        "Estado del Punto de Red:",
                        list(colores_a_nombres.values()),
                        index=list(colores_a_nombres.keys()).index(row['color']) if row['color'] in colores_a_nombres else 0,
                        key=f"edit_status_sel_{idx}"
                    )
                    e_color = [c for c, n in colores_a_nombres.items() if n == e_estado][0]
                    e_comp = "VERDE" in e_estado or "ROJO" in e_estado or "NARANJA" in e_estado

                    with st.form(f"f_edit_{idx}"):
                        e_nom = st.text_input("Nomenclatura / Nombre:", value=row.get('nomenclatura', ''))

                        if e_comp:
                            st.markdown("**Conexión al Rack**")
                            r_list = list(cat_rack["rack"])
                            r_idx  = r_list.index(rack_v) if rack_v in r_list else 0
                            e_rack = st.selectbox("Rack de Destino:", r_list, index=r_idx)

                            col_esw, col_epp = st.columns(2)
                            with col_esw:
                                e_sw_list = get_switches(e_rack)
                                e_sw_ids  = e_sw_list if e_sw_list else ["(No hay)"]
                                e_sw_idx  = e_sw_ids.index(sw_v) if sw_v in e_sw_ids else 0
                                e_sw = st.selectbox("Switch:", e_sw_ids, index=e_sw_idx)
                                e_psw = st.text_input("Puerto en Switch:", value=str(row.get('puerto_switch','')) if pd.notna(row.get('puerto_switch','')) else "")
                            with col_epp:
                                e_pp_list = get_patches(e_rack)
                                e_pp_ids  = e_pp_list if e_pp_list else ["(No hay)"]
                                cur_pp    = str(row.get('patch_panel','') or '')
                                e_pp_idx  = e_pp_ids.index(cur_pp) if cur_pp in e_pp_ids else 0
                                e_pp = st.selectbox("Patch Panel:", e_pp_ids, index=e_pp_idx)
                                e_ppp = st.text_input("Puerto en Patch Panel:", value=str(row.get('puerto_patch','')) if pd.notna(row.get('puerto_patch','')) else "")
                        else:
                            e_rack, e_sw, e_pp, e_psw, e_ppp = "", "", "", "", ""

                        st.markdown("---")
                        st.markdown("**Ubicación y Responsable**")
                        col_e3, col_e4 = st.columns(2)
                        with col_e3:
                            dep_list = list(cat_dependencia["dependencia"])
                            e_dep = st.selectbox("Dependencia:", dep_list,
                                                 index=dep_list.index(row['dependencia']) if row['dependencia'] in dep_list else 0)
                        with col_e4:
                            lug_list = list(cat_lugar["lugar"])
                            e_place = st.selectbox("Lugar:", lug_list,
                                                   index=lug_list.index(row['lugar']) if row['lugar'] in lug_list else 0)

                        e_comentarios = st.text_area("💬 Comentarios:", value=str(row.get('comentarios','') or ''), placeholder="Observaciones adicionales (opcional)...")

                        col_btns1, col_btns2 = st.columns(2)
                        with col_btns1:
                            if st.form_submit_button("💾 Actualizar Cambios", use_container_width=True):
                                nom_en_otros = (df.drop(idx)["nomenclatura"].astype(str) == e_nom).sum() >= 2
                                if not e_nom:
                                    st.error("❌ El punto debe tener una nomenclatura.")
                                elif nom_en_otros:
                                    st.error(f"❌ La nomenclatura '**{e_nom}**' ya está en uso 2 veces (máximo permitido).")
                                elif e_comp and ((e_psw and not e_psw.isnumeric()) or (e_ppp and not e_ppp.isnumeric())):
                                    st.error("❌ Los puertos deben ser números.")
                                else:
                                    old_x, old_y = row['x'], row['y']
                                    df.loc[idx, ["x","y","rack","switch","patch_panel","puerto_switch","puerto_patch","dependencia","lugar","color","nomenclatura","comentarios"]] = \
                                        [old_x, old_y, e_rack, e_sw, e_pp, e_psw, e_ppp, e_dep, e_place, e_color, e_nom, e_comentarios]
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
