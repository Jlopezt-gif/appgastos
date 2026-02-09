import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(page_title="Control de Finanzas", layout="wide")

# ================== ESTILOS ==================
st.markdown("""
<style>
.card {
    border-radius: 12px;
    padding: 16px;
    margin: 8px 0;
}
.kpi-title { font-size: 14px; color: #555; }
.kpi-value { font-size: 28px; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ================== HEADER ==================
logo_url = "https://drive.google.com/uc?export=download&id=1RWV3aq1Nm2GKyi5_RFam0RAF_cR2v_iX"

col_logo, col_title = st.columns([1, 6])
with col_logo:
    st.image(logo_url, width=80)
with col_title:
    st.markdown("## CONTROL DE FINANZAS")
    st.markdown("##### Dashboard del Cliente")

# ================== CONFIG ==================
BD_CLIENTS_URL = "https://docs.google.com/spreadsheets/d/1-m5M_SYYlD--xzRmPx6_7BnKmftPTbgzswKq1Tp1TH8/export?format=csv"

@st.cache_data(ttl=300)
def load_clients_db(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df["ID"] = df["ID"].astype(str).str.strip()
    return df

@st.cache_data(ttl=60)
def load_client_data(url):
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    return df

# ================== PARAM URL ==================
params = st.query_params
cliente_id = params.get("cliente")

if not cliente_id:
    st.error("❌ No se especificó el cliente en la URL. Usa: ?cliente=ID")
    st.stop()

cliente_id = str(cliente_id).strip()

# ================== CARGAR BD CLIENTES ==================
try:
    df_clients = load_clients_db(BD_CLIENTS_URL)
except:
    st.error("❌ No se pudo cargar la BD de clientes")
    st.stop()

row = df_clients[df_clients["ID"] == cliente_id]
if row.empty:
    st.error("❌ Cliente no encontrado en la BD de clientes")
    st.stop()

cliente_nombre = row.iloc[0]["Client"]
sheet_url = row.iloc[0]["URL Sheets"]

st.markdown(f"**👤 Usuario:** {cliente_nombre}")

# Convertir URL a CSV si hace falta
if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

# ================== CARGAR DATA ==================
try:
    df = load_client_data(sheet_url)
except:
    st.error("❌ No se pudo cargar el Google Sheets del cliente")
    st.stop()

# ================== LIMPIEZA Y FECHAS ==================
# Convertir Fecha: formato 30/1/2026 16:20:03
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True, errors="coerce")

# Asegurar tipos
df["Monto"] = pd.to_numeric(df["Monto"], errors="coerce").fillna(0)

# Mes en texto
mes_map = {
    1: "Enero", 2: "Febrero", 3: "Marzo", 4: "Abril", 5: "Mayo", 6: "Junio",
    7: "Julio", 8: "Agosto", 9: "Septiembre", 10: "Octubre", 11: "Noviembre", 12: "Diciembre"
}
df["MesNombre"] = df["Mes"].map(mes_map)

# ================== FILTROS ==================
st.markdown("### Filtros")

col_f1, col_f2, col_f3, col_f4 = st.columns(4)

with col_f1:
    categorias = ["Todas"] + sorted(df["Categoría"].dropna().unique().tolist())
    filtro_categoria = st.selectbox("Categoría", categorias)

with col_f2:
    anios = ["Todos"] + sorted(df["Año"].dropna().unique().astype(int).astype(str).tolist())
    filtro_anio = st.selectbox("Año", anios)

with col_f3:
    meses = ["Todos"] + [mes_map[i] for i in sorted(df["Mes"].dropna().unique())]
    filtro_mes = st.selectbox("Mes", meses)

with col_f4:
    dias = ["Todos"] + sorted(df["Dia"].dropna().unique().astype(int).astype(str).tolist())
    filtro_dia = st.selectbox("Día", dias)

df_f = df.copy()

if filtro_categoria != "Todas":
    df_f = df_f[df_f["Categoría"] == filtro_categoria]

if filtro_anio != "Todos":
    df_f = df_f[df_f["Año"].astype(str) == filtro_anio]

if filtro_mes != "Todos":
    df_f = df_f[df_f["MesNombre"] == filtro_mes]

if filtro_dia != "Todos":
    df_f = df_f[df_f["Dia"].astype(str) == filtro_dia]

# ================== KPIs ==================
ingreso = df_f[df_f["Tipo"] == "Ingreso"]["Monto"].sum()
gasto = df_f[df_f["Tipo"] == "Gasto"]["Monto"].sum()

# Presupuesto: último del mes filtrado, o último anterior, o 0
df_pres = df[df["Tipo"] == "Presupuesto"].sort_values("Fecha")

presupuesto = 0
if filtro_mes != "Todos" and filtro_anio != "Todos":
    mes_num = [k for k, v in mes_map.items() if v == filtro_mes][0]
    df_mes = df_pres[(df_pres["Año"].astype(str) == filtro_anio) & (df_pres["Mes"] == mes_num)]
    if not df_mes.empty:
        presupuesto = df_mes.iloc[-1]["Monto"]
    else:
        # último anterior
        df_ant = df_pres[(df_pres["Fecha"] < df_f["Fecha"].max())]
        if not df_ant.empty:
            presupuesto = df_ant.iloc[-1]["Monto"]
else:
    if not df_pres.empty:
        presupuesto = df_pres.iloc[-1]["Monto"]

presupuesto_disponible = presupuesto - gasto

# ================== COLORES KPI ==================
# Paleta
bg_azul = "#F0F4FF"
bg_rosa = "#FFF0F6"
bg_naranja = "#FFF7ED"
bg_cian = "#F0FDFF"

if presupuesto_disponible <= 0:
    bg_pd = bg_rosa
elif presupuesto_disponible <= 100:
    bg_pd = bg_naranja
else:
    bg_pd = bg_cian

# ================== MOSTRAR KPIs ==================
k1, k2, k3, k4 = st.columns(4)

with k1:
    st.markdown(f"""
    <div class="card" style="background:{bg_cian}">
        <div class="kpi-title">Ingreso Total</div>
        <div class="kpi-value">{ingreso:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="card" style="background:{bg_rosa}">
        <div class="kpi-title">Gasto Total</div>
        <div class="kpi-value">{gasto:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="card" style="background:{bg_azul}">
        <div class="kpi-title">Presupuesto</div>
        <div class="kpi-value">{presupuesto:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="card" style="background:{bg_pd}">
        <div class="kpi-title">Presupuesto Disponible</div>
        <div class="kpi-value">{presupuesto_disponible:,.2f}</div>
    </div>
    """, unsafe_allow_html=True)

# ================== GAUGE ==================
st.markdown("### Cumplimiento del Presupuesto")

# Evitar errores si presupuesto es 0
max_val = max(presupuesto, gasto, 1)

fig_gauge = go.Figure(go.Indicator(
    mode="gauge+number",
    value=gasto,
    number={"font": {"size": 36}},
    title={"text": "Gasto vs Presupuesto"},
    gauge={
        "axis": {"range": [0, max_val]},
        
        # Arco principal (lo gastado)
        "bar": {"color": "#1E88FF", "thickness": 0.35},
        
        # Fondo del gauge
        "bgcolor": "#F2F2F2",
        
        # Zonas de color (opcional, estilo suave)
        "steps": [
            {"range": [0, presupuesto], "color": "#EAF2FF"},
            {"range": [presupuesto, max_val], "color": "#F5F5F5"},
        ],
        
        # Línea de objetivo (presupuesto)
        "threshold": {
            "line": {"color": "#1E3A8A", "width": 4},
            "thickness": 0.75,
            "value": presupuesto
        }
    }
))

st.plotly_chart(fig_gauge, use_container_width=True)

# ================== BARRAS GASTO POR CATEGORIA ==================
st.markdown("### Gastos por Categoría")

df_cat = df_f[df_f["Tipo"] == "Gasto"].groupby("Categoría", as_index=False)["Monto"].sum()
df_cat = df_cat.sort_values("Monto", ascending=False)

fig_cat = px.bar(df_cat, x="Monto", y="Categoría", orientation="h")
st.plotly_chart(fig_cat, use_container_width=True)

# ================== AREA: GASTO VS PRESUPUESTO POR MES ==================
st.markdown("### Gasto vs Presupuesto Mensual")

# Gasto por mes
gasto_mes = df[df["Tipo"] == "Gasto"].groupby("Mes", as_index=False)["Monto"].sum()
gasto_mes["MesNombre"] = gasto_mes["Mes"].map(mes_map)

# Presupuesto por mes (último de cada mes)
pres_mes = df[df["Tipo"] == "Presupuesto"].sort_values("Fecha").groupby("Mes", as_index=False).last()
pres_mes["MesNombre"] = pres_mes["Mes"].map(mes_map)

fig_area = go.Figure()
fig_area.add_trace(go.Scatter(x=gasto_mes["MesNombre"], y=gasto_mes["Monto"], fill="tozeroy", name="Gasto"))
fig_area.add_trace(go.Scatter(x=pres_mes["MesNombre"], y=pres_mes["Monto"], fill="tozeroy", name="Presupuesto"))
st.plotly_chart(fig_area, use_container_width=True)

# ================== BARRAS: GASTO VS INGRESO POR MES ==================
st.markdown("### Gasto vs Ingreso por Mes")

gasto_mes2 = df[df["Tipo"] == "Gasto"].groupby("Mes", as_index=False)["Monto"].sum()
ing_mes2 = df[df["Tipo"] == "Ingreso"].groupby("Mes", as_index=False)["Monto"].sum()

gasto_mes2["MesNombre"] = gasto_mes2["Mes"].map(mes_map)
ing_mes2["MesNombre"] = ing_mes2["Mes"].map(mes_map)

fig_bar = go.Figure()
fig_bar.add_bar(y=gasto_mes2["MesNombre"], x=gasto_mes2["Monto"], name="Gasto", orientation="h")
fig_bar.add_bar(y=ing_mes2["MesNombre"], x=ing_mes2["Monto"], name="Ingreso", orientation="h")
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLAS ==================
st.markdown("### 📄 Registros de Gastos")
df_gastos = df_f[df_f["Tipo"] == "Gasto"][["ID", "Fecha", "Descripción", "Categoría", "Monto"]]
st.dataframe(df_gastos, use_container_width=True)

st.markdown("### 📄 Registros de Ingresos")
df_ing = df_f[df_f["Tipo"] == "Ingreso"][["ID", "Fecha", "Descripción", "Categoría", "Monto"]]
st.dataframe(df_ing, use_container_width=True)
