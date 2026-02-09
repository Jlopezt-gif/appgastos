import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime

st.set_page_config(page_title="Control de Finanzas", layout="wide")

# ================== ESTILOS ==================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Roboto+Condensed:wght@300;400;700&display=swap');

html, body, [class*="css"]  {
    font-family: 'Roboto Condensed', sans-serif;
    background-color: white;
}

.kpi-card {
    background: #f8f9fc;
    border-radius: 12px;
    padding: 16px;
    text-align: center;
}

.kpi-title {
    font-size: 16px;
    color: #666;
}

.kpi-value {
    font-size: 28px;
    font-weight: 700;
}

.table-title {
    font-size: 22px;
    font-weight: 700;
    margin-bottom: 10px;
}
</style>
""", unsafe_allow_html=True)

# ================== COLORES ==================
COLOR_AZUL = "#4E54D4"
COLOR_ROSA = "#F72D93"
COLOR_NARANJA = "#FFA333"
COLOR_CIAN = "#00C1D4"

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

# ================== CARGAR CLIENTE ==================
df_clients = load_clients_db(BD_CLIENTS_URL)
row = df_clients[df_clients["ID"] == cliente_id]

if row.empty:
    st.error("❌ Cliente no encontrado")
    st.stop()

cliente_nombre = row.iloc[0]["Client"]
sheet_url = row.iloc[0]["URL Sheets"]

if "export?format=csv" not in sheet_url:
    if "/edit" in sheet_url:
        sheet_url = sheet_url.split("/edit")[0] + "/export?format=csv"

df = load_client_data(sheet_url)

# ================== LIMPIEZA ==================
df["Fecha"] = pd.to_datetime(df["Fecha"])
df["Año"] = df["Año"].astype(int)
df["Mes"] = df["Mes"].astype(int)
df["Dia"] = df["Dia"].astype(int)

# ================== HEADER ==================
col_logo, col_title = st.columns([1, 5])
with col_logo:
    st.image("https://drive.google.com/uc?id=1qlZkn7u6xTgVmKu34U9i2mD_3XL7XF6N", width=120)
with col_title:
    st.markdown(f"<h1>CONTROL DE FINANZAS</h1><h3>{cliente_nombre}</h3>", unsafe_allow_html=True)

# ================== FILTROS ==================
st.markdown("### Filtros")

colf1, colf2, colf3, colf4, colf5 = st.columns([2,2,2,2,1])

anio_actual = datetime.now().year
mes_actual = datetime.now().month

categorias_gasto = [
"Transporte","Alimentación","Discoteca/Bar","Restaurant","Vestimenta","Antojos",
"Mascota","Hogar","Servicios","Salud","Educación","Entretenimiento","Otros"
]

with colf1:
    filtro_categoria = st.multiselect("Categoría", categorias_gasto, default=categorias_gasto)

with colf2:
    filtro_anio = st.selectbox("Año", sorted(df["Año"].unique()), index=list(sorted(df["Año"].unique())).index(anio_actual) if anio_actual in df["Año"].unique() else 0)

with colf3:
    meses_map = {1:"Enero",2:"Febrero",3:"Marzo",4:"Abril",5:"Mayo",6:"Junio",7:"Julio",8:"Agosto",9:"Septiembre",10:"Octubre",11:"Noviembre",12:"Diciembre"}
    filtro_mes = st.selectbox("Mes", list(meses_map.keys()), format_func=lambda x: meses_map[x], index=mes_actual-1 if mes_actual in meses_map else 0)

with colf4:
    dias_disponibles = sorted(df[(df["Año"]==filtro_anio) & (df["Mes"]==filtro_mes)]["Dia"].unique())
    filtro_dia = st.multiselect("Día", dias_disponibles, default=dias_disponibles)

with colf5:
    limpiar = st.button("Limpiar Filtros")

if limpiar:
    filtro_categoria = categorias_gasto
    filtro_anio = anio_actual
    filtro_mes = mes_actual
    filtro_dia = dias_disponibles

# ================== APLICAR FILTROS ==================
df_f = df[
    (df["Año"] == filtro_anio) &
    (df["Mes"] == filtro_mes) &
    (df["Dia"].isin(filtro_dia))
]

# ================== CALCULOS ==================
ingreso_total = df_f[df_f["Tipo"]=="Ingreso"]["Monto"].sum()
gasto_total = df_f[df_f["Tipo"]=="Gasto"]["Monto"].sum()

df_pres_mes = df_f[df_f["Tipo"]=="Presupuesto"].sort_values("Fecha")
if len(df_pres_mes) > 0:
    presupuesto_mes = df_pres_mes.iloc[-1]["Monto"]
else:
    presupuesto_mes = 0

presupuesto_disponible = presupuesto_mes - gasto_total

# ================== KPIs ==================
c1, c2, c3, c4 = st.columns(4)

with c1:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Ingreso</div><div class='kpi-value' style='color:{COLOR_CIAN}'>S/ {ingreso_total:,.2f}</div></div>", unsafe_allow_html=True)
with c2:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Gasto</div><div class='kpi-value' style='color:{COLOR_ROSA}'>S/ {gasto_total:,.2f}</div></div>", unsafe_allow_html=True)
with c3:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Presupuesto</div><div class='kpi-value' style='color:{COLOR_NARANJA}'>S/ {presupuesto_mes:,.2f}</div></div>", unsafe_allow_html=True)
with c4:
    st.markdown(f"<div class='kpi-card'><div class='kpi-title'>Presupuesto Disponible</div><div class='kpi-value' style='color:{COLOR_AZUL}'>S/ {presupuesto_disponible:,.2f}</div></div>", unsafe_allow_html=True)

# ================== GRAFICO GAUGE ==================
fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = gasto_total,
    title = {'text': "Cumplimiento del Presupuesto"},
    gauge = {
        'axis': {'range': [0, max(presupuesto_mes, gasto_total, 1)]},
        'bar': {'color': COLOR_ROSA},
        'threshold': {
            'line': {'color': COLOR_NARANJA, 'width': 4},
            'thickness': 0.75,
            'value': presupuesto_mes
        }
    }
))
st.plotly_chart(fig_gauge, use_container_width=True)

# ================== BARRAS HORIZONTALES POR CATEGORIA ==================
df_cat = df_f[(df_f["Tipo"]=="Gasto") & (df_f["Categoría"].isin(filtro_categoria))]
df_cat = df_cat.groupby("Categoría", as_index=False)["Monto"].sum().sort_values("Monto", ascending=False)

fig_cat = px.bar(df_cat, x="Monto", y="Categoría", orientation="h", text="Monto", color_discrete_sequence=[COLOR_AZUL])
fig_cat.update_layout(title="Gasto por Categoría", yaxis={'categoryorder':'total ascending'})
st.plotly_chart(fig_cat, use_container_width=True)

# ================== LINEAS: GASTO VS PRESUPUESTO MENSUAL ==================
df_meses = df.copy()

gasto_mes = df_meses[df_meses["Tipo"]=="Gasto"].groupby("Mes")["Monto"].sum()
pres_mes = df_meses[df_meses["Tipo"]=="Presupuesto"].sort_values("Fecha").groupby("Mes").last()["Monto"]

meses = range(1,13)
gasto_vals = [gasto_mes.get(m, 0) for m in meses]
pres_vals = [pres_mes.get(m, 0) for m in meses]

fig_line = go.Figure()
fig_line.add_trace(go.Scatter(x=list(meses), y=gasto_vals, mode="lines+markers+text", name="Gasto", text=gasto_vals, textposition="top center", line=dict(color=COLOR_ROSA)))
fig_line.add_trace(go.Scatter(x=list(meses), y=pres_vals, mode="lines+markers+text", name="Presupuesto", text=pres_vals, textposition="top center", line=dict(color=COLOR_NARANJA)))
fig_line.update_layout(title="Gasto vs Presupuesto Mensual", xaxis_title="Mes", yaxis_title="Monto")
st.plotly_chart(fig_line, use_container_width=True)

# ================== BARRAS: INGRESO VS GASTO POR MES ==================
ing_mes = df_meses[df_meses["Tipo"]=="Ingreso"].groupby("Mes")["Monto"].sum()

ing_vals = [ing_mes.get(m, 0) for m in meses]

fig_bar = go.Figure()
fig_bar.add_trace(go.Bar(x=list(meses), y=gasto_vals, name="Gasto", marker_color=COLOR_ROSA))
fig_bar.add_trace(go.Bar(x=list(meses), y=ing_vals, name="Ingreso", marker_color=COLOR_CIAN))
fig_bar.update_layout(title="Ingreso vs Gasto por Mes", barmode="group", xaxis_title="Mes", yaxis_title="Monto")
st.plotly_chart(fig_bar, use_container_width=True)

# ================== TABLAS ==================
colt1, colt2 = st.columns(2)

with colt1:
    st.markdown("<div class='table-title'>Gastos</div>", unsafe_allow_html=True)
    df_gastos = df_f[df_f["Tipo"]=="Gasto"][["ID","Fecha","Descripción","Categoría","Monto"]]
    st.dataframe(df_gastos, use_container_width=True)

with colt2:
    st.markdown("<div class='table-title'>Ingresos</div>", unsafe_allow_html=True)
    df_ing = df_f[df_f["Tipo"]=="Ingreso"][["ID","Fecha","Descripción","Categoría","Monto"]]
    st.dataframe(df_ing, use_container_width=True)
